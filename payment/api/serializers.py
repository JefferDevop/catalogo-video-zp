from rest_framework.serializers import ModelSerializer
from ..models import Payment, Item
from django.db import transaction
from rest_framework.exceptions import ValidationError


class ItemSerializer(ModelSerializer):
    class Meta:
        model = Item
        fields = ['title', 'quantity', 'unit_price', 'currency_id', 'codigo', 'description']

    # def create(self, validated_data):         
    #     codigo = validated_data.pop('id', None)     
      
    #     if codigo:
    #         validated_data['codigo'] = codigo
        
    #     return super().create(validated_data)

class PaymentSerializer(ModelSerializer):
    items = ItemSerializer(many=True)

    class Meta:
        model = Payment
        fields = '__all__'
    
    def create(self, validated_data):           
        # print("Datos validados en PaymentSerializer.create:", validated_data) 
        items_data = validated_data.pop('items', [])           
        
        try:
            with transaction.atomic():
                # Crear el registro del pago
                payment = Payment.objects.create(**validated_data)

                # Usar el ItemSerializer para crear los items relacionados
                for item_data in items_data:
                    item_serializer = ItemSerializer(data=item_data)
                    if item_serializer.is_valid():                      
                        item_serializer.save(payment=payment)
                    else:
                        print("Error en los datos del item:", item_serializer.errors)
                        raise ValidationError({"detail": "Error en los items"})

                return payment
        except Exception as e:
            raise ValidationError({"detail": str(e)})
        




# class NotificationSerializer(ModelSerializer):
#     class Meta:
#         model = Notification
#         fields = '__all__'