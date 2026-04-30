from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
from .models import Meeting, MeetingMember, Evaluation
from accounts.models import UserProfile

@login_required
def meeting_list(request):
    category = request.GET.get('category')
    if category:
        meetings = Meeting.objects.filter(category=category).order_by('-created_at')
    else:
        meetings = Meeting.objects.all().order_by('-created_at')
    return render(request, 'meetings/meeting_list.html', {'meetings': meetings, 'current_category': category})

@login_required
def meeting_create(request):
    if request.method == 'POST':
        category = request.POST.get('category')
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        lat = request.POST.get('lat')
        lng = request.POST.get('lng')
        place_name = request.POST.get('place_name', '선택된 위치')
        schedule_str = request.POST.get('schedule')

        if category in dict(Meeting.CATEGORY_CHOICES) and lat and lng and schedule_str and title:
            meeting = Meeting.objects.create(
                host=request.user.userprofile,
                category=category,
                title=title,
                description=description,
                location={
                    'name': place_name,
                    'lat': lat,
                    'lng': lng
                },
                schedule=schedule_str
            )
            MeetingMember.objects.create(meeting=meeting, user=request.user.userprofile)
            return redirect('meeting_list')
    
    context = {
        'kakao_map_api_key': settings.KAKAO_MAP_API_KEY
    }
    return render(request, 'meetings/meeting_create.html', context)

@login_required
def meeting_join(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id)
    profile = request.user.userprofile
    
    # 이미 멤버인 경우 바로 채팅방으로 이동
    if MeetingMember.objects.filter(meeting=meeting, user=profile).exists():
        return redirect('meeting_chat', meeting_id=meeting.id)
    
    # 정원 초과 확인
    if meeting.members.count() >= meeting.max_members:
        from django.contrib import messages
        messages.error(request, '이 모임은 이미 정원이 가득 찼습니다.')
        return redirect('meeting_list')
    
    # 멤버로 등록 후 채팅방으로 이동
    MeetingMember.objects.create(meeting=meeting, user=profile)
    return redirect('meeting_chat', meeting_id=meeting.id)

@login_required
def evaluate_user(request, meeting_id, user_id):
    if request.method == 'POST':
        meeting = get_object_or_404(Meeting, id=meeting_id)
        evaluatee = get_object_or_404(UserProfile, user__id=user_id)
        evaluator = request.user.userprofile
        
        # Check if both are members of the meeting
        if not MeetingMember.objects.filter(meeting=meeting, user=evaluator).exists() or \
           not MeetingMember.objects.filter(meeting=meeting, user=evaluatee).exists():
            return JsonResponse({'error': 'Both users must be members of the meeting.'}, status=403)
            
        if evaluator == evaluatee:
            return JsonResponse({'error': 'You cannot evaluate yourself.'}, status=400)
            
        score_type = request.POST.get('score_type')
        if score_type == 'good':
            score = 0.5
        elif score_type == 'bad':
            score = -0.5
        else:
            return JsonResponse({'error': 'Invalid score type.'}, status=400)
            
        evaluation, created = Evaluation.objects.get_or_create(
            evaluator=evaluator,
            evaluatee=evaluatee,
            meeting=meeting,
            defaults={'score': score}
        )
        
        if created:
            evaluatee.manner += score
            evaluatee.save()
            return JsonResponse({'success': True, 'new_manner': evaluatee.manner})
        else:
            return JsonResponse({'error': 'You have already evaluated this user for this meeting.'}, status=400)
            
    return JsonResponse({'error': 'Invalid request method.'}, status=405)
