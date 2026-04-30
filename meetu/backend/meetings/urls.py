from django.urls import path
from . import views
from chat.views import meeting_chat_view

urlpatterns = [
    path('', views.meeting_list, name='meeting_list'),
    path('create/', views.meeting_create, name='meeting_create'),
    path('<int:meeting_id>/join/', views.meeting_join, name='meeting_join'),
    path('<int:meeting_id>/chat/', meeting_chat_view, name='meeting_chat'),
    path('<int:meeting_id>/evaluate/<int:user_id>/', views.evaluate_user, name='evaluate_user'),
]
