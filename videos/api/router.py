from rest_framework.routers import DefaultRouter
from videos.api.views import VideosApiViewSet

router_videos = DefaultRouter()


router_videos.register(
    prefix='videos', basename='videos', viewset=VideosApiViewSet
)
