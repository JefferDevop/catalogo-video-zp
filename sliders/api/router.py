from rest_framework.routers import DefaultRouter
from sliders.api.views import SlidersApiViewSet


router_sliders = DefaultRouter()

router_sliders.register(
    prefix='sliders', basename='sliders', viewset=SlidersApiViewSet   
)