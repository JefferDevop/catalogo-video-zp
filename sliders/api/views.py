from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly




from sliders.models import Slider
from sliders.api.serializers import SliderSerializer


class SlidersApiViewSet(ModelViewSet):    
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = SliderSerializer
    queryset = Slider.objects.all().order_by('order')
 