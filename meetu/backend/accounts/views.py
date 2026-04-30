from django.views.generic import TemplateView
from django.shortcuts import redirect

class IndexView(TemplateView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/meetings/')
        return super().get(request, *args, **kwargs)

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from meetings.models import MeetingMember

@login_required
def profile_view(request):
    profile = request.user.userprofile
    past_meetings = MeetingMember.objects.filter(user=profile).select_related('meeting').order_by('-joined_at')
    favorites = profile.favorites.all()
    
    return render(request, 'accounts/profile.html', {
        'profile': profile,
        'past_meetings': past_meetings,
        'favorites': favorites
    })

@login_required
def user_detail_view(request, user_id):
    target_profile = get_object_or_404(UserProfile, user__id=user_id)
    is_favorite = request.user.userprofile.favorites.filter(id=target_profile.id).exists()
    
    return render(request, 'accounts/user_detail.html', {
        'target_profile': target_profile,
        'is_favorite': is_favorite
    })

@login_required
def toggle_favorite(request, user_id):
    if request.method == 'POST':
        target_profile = get_object_or_404(UserProfile, user__id=user_id)
        my_profile = request.user.userprofile
        
        if target_profile in my_profile.favorites.all():
            my_profile.favorites.remove(target_profile)
        else:
            my_profile.favorites.add(target_profile)
            
    return redirect('user_detail', user_id=user_id)
