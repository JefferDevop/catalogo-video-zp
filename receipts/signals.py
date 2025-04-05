from django.db.models.signals import post_save, post_delete
from django.db.models import Sum
from django.db import transaction, IntegrityError
from django.dispatch import receiver
from .models import Ipdet
from inventory.models import Itemact


def normalize_code(codigo):
    """
    Normaliza un código eliminando espacios, convirtiendo a minúsculas
    y eliminando caracteres innecesarios.
    """
    return ''.join(codigo.lower().split())



@receiver(post_save, sender=Ipdet)
def create_or_update_ipdet(sender, instance, created, **kwargs):
    try:      
        with transaction.atomic():                

            codigo_normalizado = normalize_code(instance.codigo)
            # Si es creado, crea un nuevo itemact, de lo contrario, actualiza el existente
            itemact, _ = Itemact.objects.get_or_create(ipdet=instance, defaults={
                'qty_ipdet': instance.qty,
                'tipo': instance.tipo,
                'number': instance.number,
                'item': instance.item,
                'codigo':codigo_normalizado,
                'talla':instance.talla,
                'color':instance.color,
                'price':instance.price,
                'cost':instance.cost,
                'discount':instance.discount
            })

            # Si no es creado, actualiza el itemact existente
            if not created:

                # Ajustar la cantidad en inventario sin reemplazarla
                itemact.qty_ipdet = instance.qty  
                itemact.tipo = instance.tipo
                itemact.number = instance.number
                itemact.item = instance.item
                itemact.codigo = codigo_normalizado
                itemact.talla = instance.talla
                itemact.color = instance.color
                itemact.price = instance.price
                itemact.cost = instance.cost
                itemact.discount = instance.discount
                itemact.save()


    except IntegrityError as e:
        transaction.set_rollback(True)
        print(f"Error de integridad de base de datos: {e}")

    except Ipdet.DoesNotExist:
        transaction.set_rollback(True)
        print(f"Error: No se encontró un Ipdet para el Ipdet {instance}")

    except Exception as e:
        transaction.set_rollback(True)
        print(f"Error inesperado (Ipdet): {e}")

