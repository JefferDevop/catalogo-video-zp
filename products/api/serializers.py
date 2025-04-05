from rest_framework.serializers import ModelSerializer, SerializerMethodField
from inventory.api.serializers import  ItemactItemSerializer
from products.models import Gallery, Category, Product, CategoryProduct



class ProductSerializer(ModelSerializer):
    # atributData = AttributSerializer(source='atribut', read_only=True, many=True)
    class Meta:
        model = Product
        fields = [
            "codigo",
            "ref",
            "flag",
            "name_extend",
            "slug",
            "description",          
            "images",
            "video_url",
            "image_alterna",
            "price_old",
            "price1",
            "qty",
            "price2",
            "active",
            "soldout",
            "offer",
            "home",       
        ]

class CategorySerializer(ModelSerializer):    
    class Meta:
        model = Category
        fields = ["id", "codigo", "name", "slug", "image", "image_alterna"]

class CategoryProductSerializer(ModelSerializer):
    categoryData = CategorySerializer(source="category", read_only=True)
    productData = ProductSerializer(source="product", read_only=True)
    itemactitemData = SerializerMethodField()

    class Meta:
        model = CategoryProduct
        fields = ["id", "active", "productData", "categoryData", "itemactitemData"]

    def get_itemactitemData(self, obj):
        # Obtener la instancia de ItemactItem asociada al CategoryProduct
        itemact_item_instance = obj.product.itemactitem_set.first()  # Puedes ajustar esta lógica según tus necesidades

        # Serializar la instancia de ItemactItem
        if itemact_item_instance:
            serializer = ItemactItemSerializer(itemact_item_instance)
            return serializer.data
        else:
            return None  # O devuelve un valor predeterminado si no hay instancia de ItemactItem asociada

class GallerySerializer(ModelSerializer):
    class Meta:
        model = Gallery
        fields = ["id", "product", "image", "image_alterna",]

# class AttributSerializer(ModelSerializer):
#     class Meta:
#         model = Attribut
#         fields = ["id", "name"]

# class AttributeProductSerializer(ModelSerializer):
#     dataAttribute = AttributSerializer(source="attribut", read_only=True)
#     dataProduct = ProductSerializer(source="product", read_only=True)

#     class Meta:
#         model = CategoryProduct
#         fields = ["dataAttribute", "dataProduct"]