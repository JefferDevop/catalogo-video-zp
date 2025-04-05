from django.contrib import admin
from .models import Video



class VideoAdmin(admin.ModelAdmin):
    list_display = ("name", "video_url")
    list_display_links = ("name", "video_url")

admin.site.register(Video, VideoAdmin)