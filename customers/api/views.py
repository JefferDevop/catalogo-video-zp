from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet

from .serializers import CustomerSerializer, ProducPublictSerializer
from customers.models import Customer, Product_public


class CustomerApiViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()


class ProductPublicApiViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ProducPublictSerializer
    queryset = Product_public.objects.all().order_by('id')
    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['product']