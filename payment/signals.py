# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.db.models import Sum




# @receiver(post_save, sender=Item)
# def create_itemact_for_item(sender, instance, created, **kwargs):
#     # print(f"Item creado: {instance.description}")  # Agregar un print para ver si se ejecuta
#     try:
#         with transaction.atomic():
#             # Si se ha creado un Item, se crea un nuevo Itemact
#             if created:
                
#                 itemact = Itemact.objects.create(
#                     number=instance.id,
#                     item_id=instance.codigo,
#                     codigo=instance.description,
#                     qty_orderdet=instance.quantity,
#                     tipo='payment',  # Establecer tipo como 'payment'
#                 )

#     except Exception as e:
#         transaction.set_rollback(True)
#         print(f"Error al crear Itemact: {e}")



from .models import Item 
from inventory.models import Itemact
from django.db import transaction, IntegrityError
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Payment

@receiver(post_save, sender=Payment)
def manage_itemacts(sender, instance, created, **kwargs):
    """Crea o elimina Itemact por cada Item asociado a Payment dentro de una transacción atómica."""
    
    if not created:  # Solo en actualizaciones
        print(f"📌 Payment actualizado: {instance.id}, Pay: {instance.pay}")

        # Obtener los productos relacionados con este Payment
        items = Item.objects.filter(payment=instance)

        try:
            with transaction.atomic():  # Iniciar transacción

                if instance.pay:  # Si `pay` es True, crear un Itemact por cada Item
                    for item in items:
                        print(f"🔍 Creando Itemact para Item: {item.codigo}")
                        itemact, created = Itemact.objects.get_or_create(
                            number=instance.id,
                            item_id=item.codigo,
                            codigo=item.description,
                            qty_orderdet=item.quantity,
                            tipo="EFECTIVO",
                        )
                        print(f"✅ Itemact creado: {itemact}") if created else print(f"ℹ️ Itemact ya existía: {itemact}")

                else:  # Si `pay` es False, eliminar todos los Itemact relacionados
                    itemacts_deleted = Itemact.objects.filter(number=instance.id).delete()
                    print(f"❌ {itemacts_deleted[0]} Itemacts eliminados")

        except Exception as e:
            print(f"⚠️ Error en la transacción: {e}")
            raise  # Lanza la excepción para que Django maneje el rollback automático