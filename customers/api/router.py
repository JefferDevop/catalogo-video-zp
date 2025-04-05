from rest_framework.routers import DefaultRouter
from ..api.views import ProductPublicApiViewSet


router_productpublic = DefaultRouter()

router_productpublic.register(
    prefix='productspublic', basename='productspublic', viewset=ProductPublicApiViewSet
)
