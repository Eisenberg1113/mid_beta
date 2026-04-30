from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from datetime import datetime, timezone
import time

from .models import ChatMessage
from meetings.models import Meeting, MeetingMember
from .serializers import ChatMessageSerializer

# 일반 Django 뷰
@login_required
def meeting_chat_view(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id)
    # 해당 모임의 멤버인지 확인 (선택적)
    if not MeetingMember.objects.filter(meeting=meeting, user=request.user.userprofile).exists():
        # 멤버가 아니라면 입장을 막거나 리다이렉트
        return redirect('meeting_list')
    
    # 초기 메시지 로드
    initial_messages = ChatMessage.objects.filter(meeting=meeting).order_by('sent_at')
    serializer = ChatMessageSerializer(initial_messages, many=True, context={'request': request})
    
    import json
    # 모임 멤버 목록
    members = MeetingMember.objects.filter(meeting=meeting).select_related('user')
    
    return render(request, 'chat/chat.html', {
        'meeting': meeting,
        'initial_messages_json': json.dumps(serializer.data),
        'members': members
    })


# DRF API 뷰
class MessageAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, meeting_id):
        """
        Long-Polling 방식으로 새 메시지를 조회합니다.
        'last_id' 쿼리 파라미터 이후에 생성된 메시지를 반환합니다.
        """
        try:
            last_id = int(request.GET.get('last_id', '0'))
        except ValueError:
            return Response({'error': 'Invalid last_id format'}, status=status.HTTP_400_BAD_REQUEST)

        # 약 25초 동안 새 메시지를 기다림
        for _ in range(25):
            messages = ChatMessage.objects.filter(
                meeting_id=meeting_id,
                id__gt=last_id
            ).order_by('id')

            if messages.exists():
                serializer = ChatMessageSerializer(messages, many=True, context={'request': request})
                return Response(serializer.data)
            
            time.sleep(1) # 1초 대기

        return Response([], status=status.HTTP_200_OK) # 타임아웃, 빈 배열 반환

    def post(self, request, meeting_id):
        """
        새 메시지를 생성합니다.
        """
        meeting = get_object_or_404(Meeting, id=meeting_id)
        content = request.data.get('content')

        if not content:
            return Response({'error': 'Content is required.'}, status=status.HTTP_400_BAD_REQUEST)

        message = ChatMessage.objects.create(
            meeting=meeting,
            sender=request.user.userprofile,
            content=content
        )
        
        serializer = ChatMessageSerializer(message, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
