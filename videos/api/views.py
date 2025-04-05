from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly


from videos.models import Video
from videos.api.serializers import VideosSerializer


class VideosApiViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = VideosSerializer
    queryset = Video.objects.all()
  
   

