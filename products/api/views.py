from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Q
from rest_framework import filters



from products.models import Gallery, Category, Product, CategoryProduct
from products.api.serializers import GallerySerializer, CategorySerializer, ProductSerializer, CategoryProductSerializer


class CategoryApiViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['slug']


class ProductApiViewSet(ModelViewSet):    
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ProductSerializer
    queryset = Product.objects.all().order_by('codigo')
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['flag', 'name_extend', 'description', 'ref', 'codigo', 'price1']
    filterset_fields = ['slug', 'flag', 'active']


class ProductOEApiViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.filter(
            Q(offer=True) | Q(home=True)).order_by('name_extend')
        return queryset


class CategoryProductApiViewSet(ModelViewSet):    
    # permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = CategoryProductSerializer
    queryset = CategoryProduct.objects.all().order_by('id')
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category']



# class AtrributeProductApiViewSet(ModelViewSet):
#     permission_classes = [IsAuthenticatedOrReadOnly]
#     serializer_class = AttributeProductSerializer
#     queryset = AttributProduct.objects.all().order_by('id')
#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = ['product']
    

class GalleryApiViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = GallerySerializer
    queryset = Gallery.objects.all().order_by('id')
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product']
