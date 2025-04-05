from django.db import models
from django.db import models, transaction
from customers.models import Client, Product_public
from django_tenants.utils import get_public_schema_name, schema_exists, get_tenant_model

class Itemact(models.Model):   
    codigo = models.CharField(max_length=250, editable=False, default='', verbose_name="Código")
    ipdet = models.ForeignKey('receipts.Ipdet', on_delete=models.CASCADE, null=True, blank=True, default=None, verbose_name="In")        
    orderdet = models.ForeignKey('orders.Orderdet', on_delete=models.CASCADE, null=True, blank=True, default=None, verbose_name="Out")        
    oedet = models.ForeignKey('bills.Oedet', on_delete=models.CASCADE, null=True, blank=True, default=None)        
    cost = models.DecimalField(max_digits=12, decimal_places=2, blank=False, null=False, default= 0.0, verbose_name=(u'Costo'))
    item = models.ForeignKey('products.Product', on_delete=models.PROTECT, null=True, blank=True, default=None, verbose_name="Nombre")
    qty_ipdet = models.DecimalField(max_digits=9, decimal_places=2, default= 0, verbose_name="Entradas")
    qty_orderdet = models.DecimalField(max_digits=9, decimal_places=2, default= 0, verbose_name="Salidas")
    qty_oedet = models.DecimalField(max_digits=9, decimal_places=2, default= 0)
    tipo = models.CharField(editable=False, max_length=20, null=True, blank=True)
    number = models.CharField(max_length=255, editable=False, default="0")
    talla = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name=(u'Talla'))
    color = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name=(u'Color'))
    price = models.DecimalField(max_digits=12, decimal_places=2, blank=False, null=False, default= 0.0, verbose_name=(u'Precio'))
    discount = models.DecimalField(max_digits=12, decimal_places=2, blank=False, null=False, default= 0.0, verbose_name=(u'Descuento'))
    
    class Meta:
        verbose_name = "Actividades de Inventario"
        verbose_name_plural = "Actividades de Inventario"

    def __str__(self):
        return str(self.ipdet)
    


class ItemactItem(models.Model):
    item = models.ForeignKey('products.Product', on_delete=models.CASCADE, null=True, blank=True, default="", verbose_name=(u'Nombre'))
    codigo = models.CharField(max_length=250, editable=False, default='', verbose_name="Código")
    tenant = models.ForeignKey('customers.Client', on_delete=models.CASCADE, blank=True, default="", null=True)
    qty_current = models.DecimalField(max_digits=9, decimal_places=2, default= 0, verbose_name=(u'Ingresan'))
    qty_discount = models.DecimalField(max_digits=9, decimal_places=2, default= 0, verbose_name=(u'Salen'))
    qty_available = models.DecimalField(max_digits=9, decimal_places=2, default= 0.0, verbose_name=(u'Stock'))
    name = models.CharField(max_length=200, blank=True, null=True)
    uuid = models.UUIDField(editable=False, blank=True, null=True)
    images = models.CharField(max_length=600, null=True, default="", blank=True)
    image_alterna = models.CharField(max_length=600, null=True, default="", blank=True)
    description = models.TextField(max_length=2000, blank=True, default="")
    discount = models.DecimalField(max_digits=12, decimal_places=2, blank=False, null=False, default= 0.0, verbose_name=(u'Descuento'))
    price = models.DecimalField(max_digits=12, decimal_places=2, blank=False, null=False, default= 0.0, verbose_name=(u'Precio de Venta'))
    price1 = models.DecimalField(max_digits=12, decimal_places=2, default= 0.0, verbose_name=(u'Precio'))
    price2 = models.DecimalField(max_digits=12, blank=True, null=True, decimal_places=2, default= 0.0, verbose_name=(u'Mayorista'))
    price_old = models.DecimalField(max_digits=12, blank=True, null=True, decimal_places=2, default= 0.0)
    cost = models.DecimalField(max_digits=12, decimal_places=2, blank=False, null=False, default= 0.0, verbose_name=(u'Costo'))
    flag = models.CharField(max_length=200, null=True, blank=True, default="")
    ref = models.CharField(max_length=200, null=True, blank=True, default="")
    slug = models.CharField(max_length=200, null=True,  blank=True, default="")
    active = models.BooleanField(max_length=5, null=True, default="True", verbose_name='Activo')
    soldout = models.BooleanField(max_length=5, null=True, default="False", verbose_name='Agotado')
    offer = models.BooleanField(max_length=5, null=True, default="False", verbose_name='Oferta')
    home = models.CharField(max_length=5, blank=True, null=True,  default="")
    talla = models.CharField(max_length=20, null=True, blank=True, default='única', verbose_name=(u'Talla'))
    color = models.CharField(max_length=20, null=True, blank=True, default='único', verbose_name=(u'Color'))
    service = models.BooleanField(default=False, verbose_name=("Servicio"))
    class Meta:
        verbose_name = "Existencia"
        verbose_name_plural = "Existencias"

    # def save(self, *args, **kwargs):  
    #     try:
    #         with transaction.atomic():                           
    #             ecommerce_obj = Product_public.objects.get(item=self.uuid)
                          
    #             # Actualizar el campo 'disponible' de Ecommerce con el valor de self.available
    #             ecommerce_obj.qty = self.qty_available
    #             ecommerce_obj.save()
    #             print('Se ha actualizado la disponibilidad del producto en Ecommerce')

    #         super(ItemactItem, self).save(*args, **kwargs)

    #     except Exception as e:
    #         # Manejar la excepción e imprimir un mensaje de error
    #         print(f"Error al actualizar ItemactItem y Ecommerce: {e}")
    #         # Realizar un rollback de la transacción en caso de error
    #         transaction.set_rollback(True)

    
    def __str__(self):
        return f"{self.item} - {self.name}"
    
  