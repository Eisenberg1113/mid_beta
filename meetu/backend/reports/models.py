from django.db import models
from accounts.models import UserProfile

class Report(models.Model):
    reporter = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='reports_sent')
    target = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='reports_received')
    reason = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Report)
def check_report_count_for_ban(sender, instance, created, **kwargs):
    if created:
        target_profile = instance.target
        report_count = Report.objects.filter(target=target_profile).count()
        if report_count >= 5:
            user = target_profile.user
            user.is_active = False
            user.save()
