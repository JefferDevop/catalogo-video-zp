from rest_framework.serializers import ModelSerializer
from videos.models import Video



class VideosSerializer(ModelSerializer):
    class Meta:
        model = Video
        fields = ["video_url", "name"]
