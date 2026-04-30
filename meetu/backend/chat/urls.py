from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    # meetings/<int:meeting_id>/messages/
    path('meetings/<int:meeting_id>/messages/', views.MessageAPIView.as_view(), name='message_api'),
]
