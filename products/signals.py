from django.db.models.signals import post_save, pre_delete
from django_tenants.utils import connection
from django.dispatch import receiver
from .models import Product
# from customers.models import Product_public
from inventory.models import ItemactItem, Itemact
from django.db import transaction


@receiver(post_save, sender=Product)
def sync_producto(sender, instance, created, **kwargs):
    tenant_name = connection.tenant.schema_name

 
        # Definir los valores por defecto para ItemactItem
    itemactitem_data =  {
        'codigo': instance.codigo,
        'name': instance.name_extend,
        'images': instance.images,
        'image_alterna': instance.image_alterna,
        'description': instance.description,
        'price1': instance.price1,
        'price2': instance.price2,
        'price_old': instance.price_old,
        'flag': instance.flag,
        'ref': instance.ref,
        'slug': instance.slug,
        'active': instance.active,
        'soldout': instance.soldout,
        'offer': instance.offer,
        'home': instance.home,
        'service': instance.service,
    }

    # Crear o actualizar la instancia de ItemactItem
    if created and instance.service:
        # Crear una nueva instancia de ItemactItem si el producto es nuevo y 'service' es True
        ItemactItem.objects.create(item=instance, **itemactitem_data)
    elif not created:
        # Verificar si existen movimientos asociados en Itemact
        movimientos_existentes = Itemact.objects.filter(item=instance).exists()
        
        if not movimientos_existentes:
            # Actualizar o crear la instancia de ItemactItem si no hay movimientos
            ItemactItem.objects.update_or_create(item=instance, defaults=itemactitem_data)
    
    # try:
    #     with transaction.atomic():
    #         defaults = {
    #             'item': instance.item,
    #             'name_extend': instance.name_extend,
    #             'images': instance.images,
    #             'image_alterna': instance.image_alterna,
    #             'description': instance.description,
    #             'price1': instance.price1,
    #             'price2': instance.price2,
    #             'price_old': instance.price_old,
    #             'flag': instance.flag,
    #             'ref': instance.ref,
    #             'slug': instance.slug,
    #             'published': instance.published,
    #             'active': instance.active,
    #             'soldout': instance.soldout,
    #             'offer': instance.offer,
    #             'home': instance.home,
    #             'created_date': instance.created_date,
    #             'modified_date': instance.modified_date,
    #             'domain': tenant_name,
    #         }

    #         product_public, created = Product_public.objects.update_or_create(
    #             codigo=instance.codigo,
    #             defaults=defaults
    #         )

    #         if created:
    #             print("Registro creado con éxito...")
    #         else:
    #             print("Registro actualizado con éxito...")
    # except Exception as e:
    #     print(f"Error inesperado al sincronizar el producto: {e}")
        

# Señal para manejar la eliminación de Producto
# @receiver(pre_delete, sender=Product)
# def delete_product(sender, instance, **kwargs):
#     try:
#         product_public = Product_public.objects.get(item=instance.item)
#         product_public.delete()
#     except Product_public.DoesNotExist:
#         pass  # No hay nada que eliminar
#     except Exception as e:
#         transaction.set_rollback(True)
#         print(f"Error en la señal pre_delete: {e}")