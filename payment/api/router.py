from rest_framework.routers import DefaultRouter
from .views import PaymentApiViewSet, NotificationsApiViewSet




router_payment = DefaultRouter()
router_notifications = DefaultRouter()


router_payment.register(
    prefix='payment', basename='payment', viewset=PaymentApiViewSet 
)


router_notifications.register(
    prefix='notifications', basename='notifications', viewset=NotificationsApiViewSet 
)
