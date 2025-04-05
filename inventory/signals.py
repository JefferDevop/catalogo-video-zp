from django.db.models import F, Value, Case, When, IntegerField
from django.db.models.signals import post_save, pre_delete, pre_save
from django.db.models import Sum
from django.db import transaction
from django.dispatch import receiver
from .models import Itemact, ItemactItem
from django.db.models.functions import Coalesce


def normalize_code(codigo):
    return ''.join(codigo.lower().split())

def get_qty_data(codigo_itemact):
    """Obtiene las cantidades agregadas para un código de Itemact."""
    return Itemact.objects.filter(codigo=codigo_itemact).aggregate(
        Eqtyorderdet=Sum('qty_orderdet'),
        Eqtyipdet=Sum('qty_ipdet'),
        Eqtyoedet=Sum('qty_oedet')
    )

def update_itemact_item(itemact_item, Eqtyipdet, Eqtyorderdet, Eqtyoedet, qty_available, instance):
    """Actualiza los datos de un ItemactItem."""
    itemact_item.qty_current = Eqtyipdet
    itemact_item.qty_discount = Eqtyorderdet + Eqtyoedet
    itemact_item.qty_available = qty_available
    itemact_item.price = instance.price

    itemact_item.save()



@receiver(post_save, sender=Itemact)
def post_save_crear_itemactitem(sender, instance, created, **kwargs):
    try:
        with transaction.atomic():
            codigo_itemact = normalize_code(instance.codigo)

            # Obtener datos agregados de las cantidades
            qty_data = get_qty_data(codigo_itemact)

            Eqtyorderdet = qty_data['Eqtyorderdet'] or 0
            Eqtyipdet = qty_data['Eqtyipdet'] or 0
            Eqtyoedet = qty_data['Eqtyoedet'] or 0

            qty_available = Eqtyipdet - Eqtyorderdet - Eqtyoedet

            # Buscar el ItemactItem
            itemact_item = ItemactItem.objects.filter(codigo=codigo_itemact, item=instance.item).first()
          

            if itemact_item:
              
                # Si existe, actualizar
                update_itemact_item(itemact_item, Eqtyipdet, Eqtyorderdet, Eqtyoedet, qty_available, instance)
            else:
                # Crear un nuevo ItemactItem
                itemact_item = ItemactItem.objects.create(
                    qty_current=Eqtyipdet,
                    qty_discount=Eqtyorderdet + Eqtyoedet,
                    qty_available=qty_available,
                    name=instance.item.name_extend or "name",
                    uuid=instance.item.item,
                    slug=instance.item.slug,
                    price=instance.price,
                    price1=instance.item.price1 or 0,
                    price2=instance.item.price2 or 0,
                    price_old=instance.item.price_old or 0,
                    cost=instance.cost or 0,
                    images=instance.item.images or "",
                    image_alterna=instance.item.image_alterna or "",
                    description=instance.item.description or "",
                    flag=instance.item.flag or "",
                    ref=instance.item.ref or "",
                    active=instance.item.active or True,
                    soldout=instance.item.soldout or False,
                    offer=instance.item.offer or False,
                    home=instance.item.home or False,
                    codigo=instance.codigo,  # Utilizar el nuevo código generado
                    item=instance.item,
                    talla=instance.talla,
                    color=instance.color,
                    discount=instance.discount or 0
                )

    except Exception as e:
        transaction.set_rollback(True)
        print(f"Error inesperado al crear o actualizar ItemactItem - (ItemactItem): {e}")




# @receiver(pre_save, sender=Itemact)
# def pre_save_actualizar_itemactitem(sender, instance, **kwargs):

#     try:
#         if instance.pk:  # Solo procede si la instancia ya existe (no es nueva)
#             with transaction.atomic():
#                 # Obtener la instancia original antes de la actualización
#                 original_instance = Itemact.objects.get(pk=instance.pk)
#                 codigo_original = normalize_code(original_instance.codigo)  # Usar el código original

#                 # Obtener datos agregados de las cantidades usando el código original
#                 qty_data = get_qty_data(codigo_original)

#                 Eqtyorderdet = qty_data['Eqtyorderdet'] or 0
#                 Eqtyipdet = qty_data['Eqtyipdet'] or 0
#                 Eqtyoedet = qty_data['Eqtyoedet'] or 0

#                 qty_available = Eqtyipdet - Eqtyorderdet - Eqtyoedet

#                 # Buscar el ItemactItem correspondiente usando el código original
#                 itemact_item = ItemactItem.objects.filter(
#                     codigo=codigo_original,
#                     item=original_instance.item
#                 ).first()

#                 if not itemact_item:
#                     print(f"No se encontró ItemactItem para actualizar con código {codigo_original}")
#                     return

#                 # Actualizar los datos de ItemactItem
#                 itemact_item.talla = instance.talla  # Actualizar talla si cambia
#                 itemact_item.color = instance.color  # Actualizar color si cambia
#                 itemact_item.codigo = normalize_code(instance.codigo)  # Actualizar el código
#                 update_itemact_item(itemact_item, Eqtyipdet, Eqtyorderdet, Eqtyoedet, qty_available, instance)

#                 # Guardar los cambios en ItemactItem
#                 itemact_item.save()

#                 print(f"ItemactItem actualizado con éxito para {itemact_item.name}")

#     except Itemact.DoesNotExist:
#         print("No se encontró el Itemact original, no se pudo completar la operación.")
#     except Exception as e:
#         transaction.set_rollback(True)
#         print(f"Error inesperado al actualizar ItemactItem - (ItemactItem): {e}")

        

@receiver(pre_delete, sender=Itemact)
def restar_cantidades(sender, instance, **kwargs):
    print("Restando cantidades...")
    try:
        with transaction.atomic():
            codigo_itemact = normalize_code(instance.codigo)

            # Obtener el ItemactItem correspondiente
            itemact_item = ItemactItem.objects.filter(codigo=codigo_itemact).first()

            if not itemact_item:
                print(f"No se encontró ningún registro en ItemactItem con el código: {codigo_itemact}")
                return

            # Actualizar las cantidades en ItemactItem
            if instance.qty_ipdet > 0:
                ItemactItem.objects.filter(codigo=codigo_itemact).update(
                    qty_current=F('qty_current') - instance.qty_ipdet,
                    qty_available=F('qty_available') - instance.qty_ipdet
                )

            if instance.qty_oedet > 0 or instance.qty_orderdet > 0:
                ItemactItem.objects.filter(codigo=codigo_itemact).update(
                    qty_discount=F('qty_discount') - instance.qty_oedet - instance.qty_orderdet,
                    qty_available=F('qty_available') + instance.qty_oedet + instance.qty_orderdet
                )

    except Exception as e:
        transaction.set_rollback(True)
        print(f"Error inesperado al restar cantidades: {e}")
