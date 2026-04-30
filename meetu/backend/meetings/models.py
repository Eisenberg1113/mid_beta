from django.db import models
from accounts.models import UserProfile

class Meeting(models.Model):
    CATEGORY_CHOICES = [('운동','운동'), ('게임','게임'), ('스터디','스터디'), ('식사','식사')]
    host = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=100, default="새로운 모임")
    description = models.TextField(blank=True, null=True)
    location = models.JSONField(default=dict, blank=True)
    schedule = models.DateTimeField(null=True, blank=True)
    max_members = models.IntegerField(default=4)
    created_at = models.DateTimeField(auto_now_add=True)

class MeetingMember(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

class Evaluation(models.Model):
    evaluator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='evaluations_given')
    evaluatee = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='evaluations_received')
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='evaluations')
    score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('evaluator', 'evaluatee', 'meeting')

