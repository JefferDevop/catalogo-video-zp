from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
# from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from rest_framework.response import Response 
from rest_framework.decorators import action
from rest_framework import status
from ..models import Order, Orderdet
from inventory.models import ItemactItem
from .serializers import OrderdetSerializer, OrderSerializer
from rest_framework.exceptions import ValidationError



class OrderApiViewSet(ModelViewSet):
    # permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['slug']

    @action(detail=False, methods=['post'])
    def create_order(self, request):
       
        serializer = self.get_serializer(data=request.data)
    
        if serializer.is_valid():
            with transaction.atomic():
            
                orderdet_data = request.data.get('orderdetData', [])  # Obtener datos de los elementos del pedido
                
                if not orderdet_data:  # Verificar si no hay detalles
                    raise ValidationError({'detail': 'Debe incluir al menos un detalle de pedido.'})
                
                try:
                    # Calcular el total de la orden
                    total_order = sum(order['price'] * order['qty'] for order in orderdet_data)
                    
                    # Incluir el total en los datos del serializer
                    serializer.validated_data['total'] = total_order
                    
                    order = serializer.save()
                except Exception as e:
                    print("Error al guardar el pedido:", e)
                    return Response({'detail': 'Error al guardar el pedido.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                orderdet_instances = []

                for orderdet_item in orderdet_data:
                    item_id = orderdet_item.get('item')  # Obtener el ID del item
                  
                    try:
                        itemact_item = ItemactItem.objects.get(item=item_id)  # Obtener el objeto ItemactItem con el ID
                     
                    except ItemactItem.DoesNotExist:
                        transaction.set_rollback(True)
                        return Response({'detail': f'El ítem con ID {item_id} no existe.'}, status=status.HTTP_400_BAD_REQUEST)
                
                    qty_available = itemact_item.qty_available  # Obtener la cantidad disponible del item
                    if orderdet_item.get('qty') > qty_available:
                        transaction.set_rollback(True)                    
                        item_name = itemact_item.name  # Nombre del ítem                   
                        item_code = itemact_item.item_id  # Código del ítem
                       
                        return Response({'detail': f'La cantidad solicitada del ítem "{item_name}" (código: {item_code}) excede la cantidad disponible.'}, status=status.HTTP_400_BAD_REQUEST)
                
                    # Asignar el pedido al detalle del pedido                  
                    orderdet_item['order'] = order.id

                    # Crear el serializer del detalle del pedido
                    orderdet_serializer = OrderdetSerializer(data=orderdet_item, context=self.get_serializer_context())
             
                    if orderdet_serializer.is_valid():
                        orderdet_instances.append(orderdet_serializer.save())
                    else:
                        # Si hay algún error en la validación del detalle del pedido, devolver los errores
                        transaction.set_rollback(True)
                        return Response(orderdet_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class OrderdetApiViewSet(ModelViewSet):
    # permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = OrderdetSerializer
    queryset = Orderdet.objects.all()
    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['slug']




# class OrderApiViewSet(ModelViewSet):
#     serializer_class = OrderSerializer
#     queryset = Order.objects.all()

#     @action(detail=False, methods=['post'])
#     def create_order(self, request):        
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             with transaction.atomic():
#                 orderdet_data = request.data.get('orderdetData', [])  # Obtener datos de los elementos del pedido
             
#                 if not orderdet_data:  # Verificar si no hay detalles
#                     raise ValidationError({'detail': 'Debe incluir al menos un detalle de pedido.'})
            
#                 order = serializer.save()  # Guardar la cabecera del pedido
                
#                 orderdet_instances = []
#                 for orderdet_item in orderdet_data:
#                     item_id = orderdet_item.get('item')  # Obtener el ID del item
#                     try:
#                         itemact_item = ItemactItem.objects.get(item_id=item_id)  # Obtener el objeto ItemactItem con el ID
#                     except ItemactItem.DoesNotExist:
#                         transaction.set_rollback(True)
#                         return Response({'detail': f'El ítem con ID {item_id} no existe.'}, status=status.HTTP_400_BAD_REQUEST)
                
#                     qty_available = itemact_item.qty_available  # Obtener la cantidad disponible del item
#                     if orderdet_item.get('qty') > qty_available:
#                         transaction.set_rollback(True)
#                         item_name = itemact_item.name  # Nombre del ítem
#                         item_code = itemact_item.codigo  # Código del ítem
#                         return Response({'detail': f'La cantidad solicitada del ítem "{item_name}" (código: {item_code}) excede la cantidad disponible.'}, status=status.HTTP_400_BAD_REQUEST)
                
#                     # Asignar el pedido al detalle del pedido
#                     orderdet_item['order'] = order.id
#                     # Crear el serializer del detalle del pedido
#                     orderdet_serializer = OrderdetSerializer(data=orderdet_item, context=self.get_serializer_context())
#                     if orderdet_serializer.is_valid():
#                         orderdet_instances.append(orderdet_serializer.save())
#                     else:
#                         # Si hay algún error en la validación del detalle del pedido, devolver los errores
#                         transaction.set_rollback(True)
#                         return Response(orderdet_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#                 return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



