from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet
from django.db.models import Q

from .serializers import ItemactItemSerializer
from ..models import ItemactItem
from django_filters import rest_framework as filters

from django_filters.rest_framework import DjangoFilterBackend


class ItemactItemFilter(filters.FilterSet):
    id_categoria = filters.NumberFilter(method='filter_by_category')
    item_id = filters.CharFilter(field_name='item_id', lookup_expr='exact')
    codigo = filters.CharFilter(field_name='codigo', lookup_expr='exact')
    slug = filters.CharFilter(field_name='slug', lookup_expr='exact')

    class Meta:
        model = ItemactItem
        fields = ['item_id','codigo', 'slug']

    def filter_by_category(self, queryset, name, value):
        # Filtrar por el id de categoría utilizando la relación con CategoryProduct
        return queryset.filter(item__categoryproduct__category__id=value)
    

class ItemactItemApiViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ItemactItemSerializer
    queryset = ItemactItem.objects.all().order_by('id')
    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['product']


class InventoryApiViewSet(ModelViewSet):
    # permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ItemactItemSerializer
    queryset = ItemactItem.objects.all().order_by('id')
    filter_backends = [DjangoFilterBackend]
    filterset_class = ItemactItemFilter

    def get_queryset(self):
        # Filtrar productos con qty_available mayor a 0
        return ItemactItem.objects.filter(Q(qty_available__gt=0) | Q(service=True)).order_by('id')
   
    
    # Filtro por categoría relacionada a través del campo 'item'
    # filterset_fields = ['item__category__id']