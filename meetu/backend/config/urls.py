from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from accounts.views import IndexView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('accounts.urls')),
    path('', IndexView.as_view(), name='index'),
    path('api/', include('chat.urls')),
    path('meetings/', include('meetings.urls')),
    path('reports/', include('reports.urls')),
    path('dashboard/', RedirectView.as_view(url='/meetings/')),
]
