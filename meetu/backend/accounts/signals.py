from allauth.socialaccount.signals import social_account_added
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile
import random, string

def generate_nickname():
    return 'user_' + ''.join(random.choices(string.ascii_lowercase, k=6))

@receiver(post_save, sender=User)
def create_profile_on_user_save(sender, instance, created, **kwargs):
    if created and not UserProfile.objects.filter(user=instance).exists():
        UserProfile.objects.create(user=instance, nickname=generate_nickname())

@receiver(social_account_added)
def create_profile(request, sociallogin, **kwargs):
    user = sociallogin.user
    if not UserProfile.objects.filter(user=user).exists():
        UserProfile.objects.create(user=user, nickname=generate_nickname())
