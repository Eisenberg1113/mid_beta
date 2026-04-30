from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ChatMessage
from accounts.models import UserProfile

class ChatSenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['nickname']

class ChatMessageSerializer(serializers.ModelSerializer):
    sender = ChatSenderSerializer(read_only=True)
    is_mine = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = ['id', 'sender', 'content', 'sent_at', 'is_mine']

    def get_is_mine(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, "user"):
            return obj.sender.user == request.user
        return False
