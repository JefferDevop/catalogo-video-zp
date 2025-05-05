from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from accounts.models import Address
import uuid
from decouple import config
from rest_framework.response import Response
from django.db import connection
from ..models import MercadoPagoNotification, Payment
from inventory.models import Itemact, ItemactItem

import requests


from .serializers import PaymentSerializer


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def generate_external_reference(email):
    email_prefix = email.split("@")[0]  # Toma el prefijo del email (antes del @)
    unique_id = str(uuid.uuid4())  # Genera un UUID único
    return f"{email_prefix}-{unique_id}"


# def get_status_payment(data_id):
#     try:
#         # Obtener el token de acceso desde las configuraciones
#         MERCADOPAGO_ACCESS_TOKEN = config('MERCADOPAGO_ACCESS_TOKEN')

#         # Construir la URL de la API usando data_id
#         url = f"https://api.mercadopago.com/v1/payments/{data_id}"
#         headers = {
#             "Authorization": f"Bearer {MERCADOPAGO_ACCESS_TOKEN}"
#         }

#         # Realizar la solicitud a la API de MercadoPago
#         response = requests.get(url, headers=headers)

#         # Verificar si la respuesta es exitosa
#         if response.status_code == 200:
#             data = response.json()

#             return data

#         return None, None
    
#     except MercadoPagoNotification.DoesNotExist:
#         print(f"No se encontró un registro con data_id: {data_id}")
#         return None, None

#     except requests.exceptions.RequestException as e:
#         print(f"Error al realizar la solicitud a MercadoPago: {e}")
#         return None, None

#     except Exception as e:
#         print(f"Error inesperado: {e}")
#         return None, None


def create_payment_and_items(response_data, client_ip, address):
    
    items_data = response_data.get('items', [])  
    total_amount = sum(item['unit_price'] * item['quantity'] for item in items_data)


    items_data = [
        {**item, 'codigo': item.pop('id')} if 'id' in item else item
        for item in items_data
    ]


    payment_data = {
        'mercadopago_id': generate_external_reference('order@gmail.com'),
        'transaction_amount': total_amount,
        'ip_address': client_ip,
        # 'external_resource_url': response_data.get('init_point', 'www.default.com'),
        'payment_method_id': 'pse',
        'items': items_data,
        'address': address,
        'external_reference': response_data.get('external_reference', 'default-external-reference'),
    }

    print('payment_data', payment_data)

    serializer = PaymentSerializer(data=payment_data)


    
    if serializer.is_valid():
        try:           
            payment = serializer.save()                  
            return Response(response_data, status=status.HTTP_201_CREATED) # Porque response_data y no Payment ???
        except Exception as e:
            raise ValidationError({"detail": str(e)})
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentApiViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
 
    def create(self, request):
        data = request.data
        items_data = data.get('items', [])
        address = data.get('address')
        wholesale = data.get('wholesale', False)
        client_ip = get_client_ip(request) 

        # productos_sin_stock = []

        # print(f"Verificando stock para {items_data}")
        # # -------------------------
        # # Verificar stock en ItemactItem antes de procesar la compra
        # for item_wrapper in items_data:
        #     item = next(iter(item_wrapper.values()))  # Obtener el primer (y único) valor del diccionario

        #     codigo = item.get('codigo')
        #     name = item.get('name')
        #     cantidad_solicitada = item_wrapper.get('quantity', 0)

        #     try:
        #         item_stock = ItemactItem.objects.get(codigo=codigo)  # Buscar el producto en ItemactItem

        #         if item_stock.qty_available < cantidad_solicitada:
        #             productos_sin_stock.append({
        #                 "name": f"{name} {codigo}" ,
        #                 "disponible": item_stock.qty_available,
        #                 "solicitado": cantidad_solicitada
        #             })

        #     except ItemactItem.DoesNotExist:
        #         productos_sin_stock.append({
        #             "name": f"{name} {codigo}" ,
        #             "disponible": 0,
        #             "solicitado": cantidad_solicitada
        #         })

        # # Si hay productos sin stock suficiente, retornar mensaje y salir
        # if productos_sin_stock:
        #     return Response(
        #         {"error": "Stock insuficiente para algunos productos", "productos": productos_sin_stock},
        #     status=status.HTTP_400_BAD_REQUEST
        #     )
        
        #--------------------------
      
        items = []
        for product in items_data:  # Iteramos sobre cada producto
            # item_data = product.get("0", {})
            # price = float(item_data.get("price1", 0))
           
            item = {
                "id": product.get("codigo"),
                "title": product.get("name_extend"),
                "description": product.get("description", "Descripción del producto"),
                "picture_url": product.get("images", "https://example.com/default-image.jpg"),
                "quantity": product.get("quantity", 1), 
                "talla": product.get("talla"),
                "currency_id": "COP",
                "unit_price": float(product.get("price2" if wholesale else "price1", 0)),        
            }

            items.append(item) 

        try:
            address_instance = Address.objects.get(id=address)
        except Address.DoesNotExist:
            address_instance = None


        try:
            city = address_instance.city.strip().lower() if address_instance and address_instance.city else ""
            envio_price = 10000 if city == 'cali' else 0
        except AttributeError:
            envio_price = 0  # Valor por defecto si address_instance no es válido

        # Agregar el producto de envío a los items
        # envio_item = {
        #     "id": "envio",
        #     "title": "Costo de envío",
        #     "description": f"Envío a {city.capitalize()}" if address_instance else "Envío",
        #     "quantity": 1,
        #     "currency_id": "COP",
        #     "unit_price": envio_price,
        # }

    
        # items.append(envio_item)  # Añadir el envío a los items
  
        
        payload = {
            "items": items,
            "external_reference": generate_external_reference(address_instance.email),
            # "total_amount": total_amount,
            "payment_methods": {
                "excluded_payment_types": [{"id": "ticket"}],
                "default_payment_method_id": "pse",
                "installments": 1,
            },
            "payer": {
                "email": f'{address_instance.name} {address_instance.lastname}: {address_instance.email}'
            },            
           
            "notification_url": "https://antotex.soluciones.space/api/notifications/",
            "back_urls": {
                "success": "https://antotex.vercel.app/",
                "failure": "https://antotex.vercel.app/",
                "pending": "https://antotex.vercel.app/payment"
            },
            "auto_return": "approved",
        }


        return create_payment_and_items(payload, client_ip, address)

       

        # MERCADOPAGO_ACCESS_TOKEN = config('MERCADOPAGO_ACCESS_TOKEN')

        # url = "https://api.mercadopago.com/checkout/preferences"
        # headers = {
        #     "Content-Type": "application/json",
        #     "Authorization": f"Bearer {MERCADOPAGO_ACCESS_TOKEN}"
        # }

        # try:
        #     response = requests.post(url, json=payload, headers=headers)          
        #     response_data = response.json()

        #     print('--**--',response_data)

        #     if response.status_code in [200, 201]:
        #         return create_payment_and_items(response_data, client_ip, address)
        #     else:
        #         return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
               
        # except requests.exceptions.RequestException as e:
        #     return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # except Exception as e:           
        #     return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



# class NotificationsApiViewSet(ModelViewSet):
#     def create(self, request, *args, **kwargs):
#         # Imprimir el payload recibido para depuración
#         print("Notificación recibida de MercadoPago:")
#         # print(request.data)

#         data = request.data
#         data_id = data.get('data', {}).get('id')

#         # Procesar y guardar la notificación
#         try:
#             notification, created = MercadoPagoNotification.objects.update_or_create(
#                 data_id=data_id,
#                 defaults={
#                     'topic': data.get('topic'),
#                     'resource': data.get('resource'),
#                     'action': data.get('action'),
#                     'api_version': data.get('api_version'),
#                     'date_created': data.get('date_created'),
#                     'notification_id': data.get('id'),
#                     'live_mode': data.get('live_mode', False),
#                     'user_id': data.get('user_id'),
#                 }
#             )

#             if created:
#                 print(f"Notificación creada con data_id: {data_id}")
#             else:
#                 print(f"Notificación actualizada con data_id: {data_id}")

#             # Intentar obtener el estado del pago y external_reference
#             try:
#                 payment_status, external_reference = get_status_payment(data_id)  # Cambiado a `payment_status`

#                 if payment_status and external_reference:
#                     print(f"Estado del pago: {payment_status}, External Reference: {external_reference}")
#                     # Aquí puedes agregar lógica para procesar el estado del pago, como actualizar un modelo relacionado.
#                 else:
#                     print(f"No se pudo obtener el estado del pago o el external_reference para data_id: {data_id}")
#             except Exception as e:
#                 print(f"Error al obtener el estado del pago: {e}")

#         except Exception as e:
#             print(f"Error al procesar la notificación: {e}")
#             return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         return Response({"message": "Notification processed"}, status=status.HTTP_200_OK)



# class NotificationsApiViewSet(ModelViewSet):
#     def create(self, request, *args, **kwargs):
#         print("Notificación recibida de MercadoPago:")

#         data = request.data
#         data_id = data.get('data', {}).get('id')

#         # Validar que `data_id` tenga información
#         if not data_id:
#             print("Notificación ignorada: no contiene data_id.")
#             return Response({"message": "Notification ignored: no data_id found"}, status=status.HTTP_200_OK)

#         try:
#             # Crear una nueva notificación en MercadoPagoNotification
#             notification = MercadoPagoNotification(
#                 topic=data.get('topic'),
#                 resource=data.get('resource'),
#                 action=data.get('action'),
#                 api_version=data.get('api_version'),
#                 data_id=data_id,
#                 date_created=data.get('date_created'),
#                 notification_id=data.get('id'),
#                 live_mode=data.get('live_mode', False),
#                 user_id=data.get('user_id'),
#             )
#             notification.save()
#             print(f"Nuevo registro creado para data_id: {data_id}")

#             try:
#                 # Obtener estado del pago y external_reference
#                 payment_status, external_reference = get_status_payment(data_id)

#                 if not external_reference:
#                     print(f"No se obtuvo external_reference para data_id: {data_id}")
#                     return Response({"message": "No external_reference found"}, status=status.HTTP_400_BAD_REQUEST)

#                 # Buscar y actualizar el modelo Payment
#                 try:
#                     payment = Payment.objects.get(external_reference=external_reference)
#                     payment.pay = True
#                     payment.status = payment_status
#                     payment.save()

#                     print(f"Modelo Payment actualizado: pay=True, status={payment_status}")
#                 except Payment.DoesNotExist:
#                     print(f"No se encontró un registro en Payment con external_reference: {external_reference}")
#                     return Response(
#                         {"message": f"Payment not found for external_reference: {external_reference}"},
#                         status=status.HTTP_404_NOT_FOUND,
#                     )

#             except Exception as e:
#                 print(f"Error al obtener estado del pago: {e}")
#                 return Response(
#                     {"message": "Error processing payment status", "details": str(e)},
#                     status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 )

#         except Exception as e:
#             print(f"Error al procesar la notificación: {e}")
#             return Response(
#                 {"message": "Internal Server Error", "details": str(e)},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )

#         return Response({"message": "Notification processed successfully"}, status=status.HTTP_200_OK)



# class NotificationsApiViewSet(ModelViewSet):
#     def create(self, request, *args, **kwargs):
#         print("Notificación recibida de MercadoPago:")

#         data = request.data
#         data_id = data.get('data', {}).get('id')

#         # Verificar si `data_id` tiene información
#         if not data_id:
#             return Response(
#                 {"error": "Invalid notification: missing data_id"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         try:
#             # Crear un registro de la notificación
#             notification = MercadoPagoNotification.objects.create(
#                 topic=data.get('topic'),
#                 resource=data.get('resource'),
#                 action=data.get('action'),
#                 api_version=data.get('api_version'),
#                 data_id=data_id,
#                 date_created=data.get('date_created'),
#                 notification_id=data.get('id'),
#                 live_mode=data.get('live_mode', False),
#                 user_id=data.get('user_id'),
#             )
#             print(f"Nuevo registro creado para data_id: {data_id}")

#             # Intentar obtener el estado del pago y el external_reference
#             try:

#                  # Obtener la data completa del pago
#                 payment_data = get_status_payment(data_id)

#                 if not payment_data:
#                     print(f"No se pudo obtener la data para data_id: {data_id}")
#                     return Response({"message": "Error fetching payment data"}, status=status.HTTP_400_BAD_REQUEST)

#                 # Extraer status y external_reference
#                 payment_status = payment_data.get("status")
#                 external_reference = payment_data.get("external_reference")


#                 if not external_reference:
#                     print(f"No se obtuvo external_reference para data_id: {data_id}")
#                     return Response(
#                         {"message": "No external_reference found"},
#                         status=status.HTTP_400_BAD_REQUEST,
#                     )

#                 # Intentar obtener y actualizar el modelo Payment
#                 try:
#                     payment = Payment.objects.get(external_reference=external_reference)
#                     payment.status = payment_status
#                     payment.save()

#                     print(f"Modelo Payment actualizado: pay=True, status={payment_status}")

#                 except Payment.DoesNotExist:

#                     return Response(
#                         {
#                             "message": f"Payment not found for external_reference: {external_reference}"
#                         },
#                         status=status.HTTP_404_NOT_FOUND,
#                     )

#                 # Si el pago está aprobado, procesar los ítems
#                 if payment_status == "approved":
#                     items = payment_data.get("additional_info", {}).get("items", [])
#                     self.process_items(items, data_id)

#                     payment = Payment.objects.get(external_reference=external_reference)
#                     payment.pay = True
#                     payment.save()
#                 else:
#                     print(f"Estado del pago no aprobado: {payment_status}")

#             except Exception as e:
#                 print(f"Error al obtener el estado del pago: {e}")
#                 return Response(
#                     {"error": "Error al obtener el estado del pago"},
#                     status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 )

#         except Exception as e:
#             print(f"Error al procesar la notificación: {e}")
#             return Response(
#                 {"error": "Error al procesar la notificación"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )

#         return Response({"message": "Notification processed"}, status=status.HTTP_200_OK)

#     def process_items(self, items, data_id):
#         """
#         Procesa el listado de ítems de la notificación y los guarda en el modelo Itemact.
#         """
#         print(f"Procesando ítems para la notificación con data_id: {items}")

#         try:
#             for item in items:

#                 if item.get("id") == "envio":
#                     print(f"Ítem ignorado con código: {item.get('id')}")
#                     continue

#                 Itemact.objects.create(
#                     number=data_id,  # Asociar al identificador de la notificación
#                     item_id=item.get("id"),
#                     codigo=item.get("description"),
#                     qty_orderdet=item.get("quantity", 0),
#                     tipo="payment",
#                 )
#                 print(f"Itemact creado para el ítem: {item.get('description')}")
#         except Exception as e:
#             print(f"Error al procesar los ítems: {e}")
#             raise


class NotificationsApiViewSet(ModelViewSet):
    def create(self, request, *args, **kwargs):
        print("Notificación recibida de MercadoPago:")


# class NotificationsApiViewSet(ModelViewSet):
#     def create(self, request, *args, **kwargs):
#         print("Notificación recibida de MercadoPago:--------------------------")

#         data = request.data
#         data_id = data.get("data", {}).get("id")

#         if not data_id:
#             return Response(
#                 {"error": "Invalid notification: missing data_id"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         # Crear un registro de la notificación
#         try:
#             notification = MercadoPagoNotification.objects.create(
#                 topic=data.get("topic"),
#                 resource=data.get("resource"),
#                 action=data.get("action"),
#                 api_version=data.get("api_version"),
#                 data_id=data_id,
#                 date_created=data.get("date_created"),
#                 notification_id=data.get("id"),
#                 live_mode=data.get("live_mode", False),
#                 user_id=data.get("user_id"),
#             )
#             print(f"Nuevo registro de notificación creado para data_id: {data_id}")
#         except Exception as e:
#             print(f"Error al guardar la notificación: {e}")
#             return Response(
#                 {"error": "Error al guardar la notificación"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )

#         # Obtener y procesar el estado del pago
#         try:
#             payment_data = get_status_payment(data_id)
#             if not payment_data:
#                 return Response(
#                     {"error": "Error fetching payment data"},
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )

#             payment_status = payment_data.get("status")
#             external_reference = payment_data.get("external_reference")

#             if not external_reference:
#                 return Response(
#                     {"error": "No external_reference found"},
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )

#             # Actualizar el modelo Payment
#             payment = self.update_payment_status(external_reference, payment_status)
#             if not payment:
#                 return Response(
#                     {"error": f"Payment not found for external_reference: {external_reference}"},
#                     status=status.HTTP_404_NOT_FOUND,
#                 )

#             # Procesar los ítems si el pago está aprobado
#             if payment_status == "approved":
#                 items = payment_data.get("additional_info", {}).get("items", [])
#                 self.process_items(items, data_id)

#                 payment.pay = True
#                 payment.save()
#                 print(f"Pago aprobado. Payment actualizado: pay=True")
#             else:
#                 print(f"Estado del pago no aprobado: {payment_status}")

#         except Exception as e:
#             print(f"Error al procesar el estado del pago: {e}")
#             return Response(
#                 {"error": "Error al procesar el estado del pago"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )

#         return Response({"message": "Notification processed"}, status=status.HTTP_200_OK)

#     def update_payment_status(self, external_reference, payment_status):
#         """
#         Actualiza el estado del modelo Payment basado en el external_reference.
#         """
#         try:
#             payment = Payment.objects.get(external_reference=external_reference)
#             payment.status = payment_status
#             payment.save()
#             print(f"Modelo Payment actualizado: status={payment_status}")
#             return payment
#         except Payment.DoesNotExist:
#             print(f"No se encontró un Payment con external_reference: {external_reference}")
#             print(f"Status: {payment_status}")
#             return None

#     def process_items(self, items, data_id):

#         # "Procesando ítems para la notificación con data_id: {data_id}")

#         for item in items:
#             try:
#                 if item.get("id") == "envio":
#                     print(f"Ítem ignorado con código: {item.get('id')}")
#                     continue

#                 Itemact.objects.create(
#                     number=data_id,
#                     item_id=item.get("id"),
#                     codigo=item.get("description"),
#                     qty_orderdet=item.get("quantity", 0),
#                     tipo="payment",
#                 )
#                 print(f"Itemact creado para el ítem: {item.get('description')}")
#             except Exception as e:
#                 print(f"Error al procesar el ítem {item.get('description')}: {e}")
#                 continue