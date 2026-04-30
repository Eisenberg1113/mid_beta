from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.conf import settings
from .models import Meeting, MeetingMember, Evaluation
import json

class CustomMeetingAdmin(admin.ModelAdmin):
    list_display = ('category', 'host', 'schedule', 'max_members', 'created_at')
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('density-dashboard/', self.admin_site.admin_view(self.density_dashboard_view), name='density_dashboard'),
        ]
        return custom_urls + urls

    def density_dashboard_view(self, request):
        meetings = Meeting.objects.all()
        locations = []
        for m in meetings:
            if m.location and 'lat' in m.location and 'lng' in m.location:
                locations.append({
                    'title': f"[{m.category}] {m.location.get('name', '장소')}",
                    'lat': m.location['lat'],
                    'lng': m.location['lng']
                })
                
        context = dict(
            self.admin_site.each_context(request),
            kakao_map_api_key=settings.KAKAO_MAP_API_KEY,
            locations_json=json.dumps(locations),
            title="모임 밀집도 대시보드"
        )
        return render(request, 'admin/density_dashboard.html', context)

admin.site.register(Meeting, CustomMeetingAdmin)
admin.site.register(MeetingMember)
admin.site.register(Evaluation)
