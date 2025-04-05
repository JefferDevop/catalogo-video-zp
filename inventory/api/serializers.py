
from rest_framework import serializers
# from products.api.serializers import ProductSerializer
from ..models import ItemactItem
from products.models import CategoryProduct




class ItemactItemSerializer(serializers.ModelSerializer):

    # category_name = serializers.CharField(source='item.category.name', read_only=True)
    # atributData = AttributSerializer(source='atribut', read_only=True, many=True)

    # product_data = CategorySerializer(source='catagory', read_only=True)
    # product_data = ProductSerializer(source='item', read_only=True)

    id_categoria = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()
    class Meta:
        model = ItemactItem
        fields = [
            "id",
            "qty_available",
            "price",
            "item_id",
            "talla",
            "color",
            "id_categoria",
            "codigo",
            "name",
            "uuid",
            "images",
            "image_alterna",
            "description",          
            "discount",
            "price1",
            "price2",
            "price_old",
            "flag",
            "ref",
            "slug",
            "active",
            "soldout",
            "offer",
            "home",       
            "product",
            'cost',
            'service'
            
            # "product_data",
            # "category_name",                   
        ]

    def get_product(self, obj):
        # Importar el ProductSerializer dentro del método para evitar importación circular
        from products.api.serializers import ProductSerializer
        return ProductSerializer(obj.item).data

    def get_id_categoria(self, obj):
        # Obtener la categoría a través del item del producto
        category_product = CategoryProduct.objects.filter(product=obj.item).first()
        if category_product:
            return category_product.category.id
        return None
   

