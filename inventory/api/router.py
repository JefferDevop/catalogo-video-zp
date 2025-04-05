from rest_framework.routers import DefaultRouter
from ..api.views import ItemactItemApiViewSet, InventoryApiViewSet


router_ecommerce = DefaultRouter()
router_inventory = DefaultRouter()


router_ecommerce.register(
    prefix='product_ecommerce', basename='product_ecommerce', viewset=ItemactItemApiViewSet
)


router_inventory.register(
    prefix='inventory', basename='inventory', viewset=InventoryApiViewSet
)