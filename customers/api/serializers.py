from rest_framework.serializers import ModelSerializer
from customers.models import Customer, Product_public

# from warehome.api.serializers import StockSerializer

class CustomerSerializer(ModelSerializer):
    # stock_data = StockSerializer(source='stock', read_only=True)

    class Meta:
        model = Customer
        fields = ['id_n', 'company' ]


class ProducPublictSerializer(ModelSerializer):
    # atributData = AttributSerializer(source='atribut', read_only=True, many=True)
    class Meta:
        model = Product_public
        fields = [
            "id",
            "item",
            "codigo",
            "name_extend",
            "images",
            "image_alterna",
            "description",          
            "price1",
            "price2",
            "price_old",
            "flag",
            "ref",
            "slug",
            "published_public",
            "published",
            "active",
            "soldout",
            "offer",
            "home",       
            "created_date",
            "modified_date",
            "domain",
            "qty",
        ]