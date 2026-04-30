from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
    path('profile/<int:user_id>/', views.user_detail_view, name='user_detail'),
    path('profile/<int:user_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
]
