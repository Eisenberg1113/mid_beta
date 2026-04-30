from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import UserProfile
from .models import Report

@login_required
def submit_report(request, user_id):
    target_profile = get_object_or_404(UserProfile, user__id=user_id)
    
    if request.user.userprofile == target_profile:
        messages.error(request, "자신을 신고할 수 없습니다.")
        return redirect('user_detail', user_id=user_id)
        
    if request.method == 'POST':
        reason = request.POST.get('reason')
        if reason:
            Report.objects.create(
                reporter=request.user.userprofile,
                target=target_profile,
                reason=reason
            )
            messages.success(request, f"{target_profile.nickname} 님을 신고했습니다.")
            return redirect('meeting_list')
            
    return render(request, 'reports/submit.html', {'target_profile': target_profile})
