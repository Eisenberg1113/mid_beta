from django.db import models
from meetings.models import Meeting
from accounts.models import UserProfile

class ChatMessage(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    sender = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
