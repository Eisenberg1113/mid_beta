from django.urls import path
from . import views

urlpatterns = [
    path('submit/<int:user_id>/', views.submit_report, name='submit_report'),
]
