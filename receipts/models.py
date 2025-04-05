from django.db import models
from django.db.models import Max, Sum
from inventory.models import ItemactItem
from django.core.exceptions import ValidationError

from django.core.serializers import serialize



class Ip(models.Model):
    TIPO = [
        # ('SALDOS INICIALES', 'EA'),
        ('ENTRADA', 'E1')
    ]

    cust = models.ForeignKey('custs.Tercero', on_delete=models.PROTECT, verbose_name="Proveedor")
    number = models.PositiveIntegerField(editable=False, default=0, verbose_name=u'No. Documento')
    tipo = models.CharField(max_length=20, choices=TIPO, default='E1')
    total = models.DecimalField(max_digits=22, decimal_places=2, default=0.00)
    concept = models.CharField(max_length=80, verbose_name='Concepto', null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name="Creado")

    class Meta:
        unique_together = ('number', 'tipo')
        verbose_name = "Entrada"
        verbose_name_plural = "Entrada de mercancía"

    def save(self, *args, **kwargs):

        # Calcular el total sumando los subtotales de los detalles relacionados
        total_calculado = self.detalles.aggregate(Sum('subtotal'))['subtotal__sum'] or 0
        self.total = total_calculado


        try:
            if not self.pk:
                ultimo_numero = Ip.objects.filter(tipo=self.tipo).aggregate(Max('number'))['number__max']
                nuevo_numero = ultimo_numero + 1 if ultimo_numero else 1
                self.number = nuevo_numero

            super(Ip, self).save(*args, **kwargs)

        except Exception as e:
            # Manejar la excepción y retornar un mensaje personalizado
            return f"No se pudo guardar la entrada. Error: {str(e)}"

    def __str__(self):
        return f"{self.tipo} No. {self.number}"
    

class Ipdet(models.Model):   
    ip = models.ForeignKey(Ip, related_name='detalles', on_delete=models.CASCADE)     
    item = models.ForeignKey('products.Product', on_delete=models.PROTECT ,verbose_name="Nombre")
    tipo = models.CharField(editable=False, max_length=20, null=True, blank=True)
    number = models.PositiveIntegerField(editable=False, default=0, verbose_name="Numero")
    qty = models.DecimalField(max_digits=9, decimal_places=2, blank=False, null=False, default= 1, verbose_name=(u'Cantidad'))
    cost = models.DecimalField(max_digits=12, decimal_places=2, blank=False, null=False, default= 0.0, verbose_name=(u'Costo'))
    price = models.DecimalField(max_digits=12, decimal_places=2, blank=False, null=False, default= 0.0, verbose_name=(u'Precio'))
    discount = models.DecimalField(max_digits=12, decimal_places=2, blank=False, null=False, default= 0.0, verbose_name=(u'Descuento'))
    subtotal = models.DecimalField(max_digits=22, decimal_places=2, blank=False, null=False, default= 0.0, verbose_name=(u'SubTotal'))
    talla = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name=(u'Talla'))
    color = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name=(u'Color'))
    codigo = models.CharField(max_length=250, editable=False, default='', verbose_name="Código")
    comments = models.CharField(max_length=250, blank=True, verbose_name=(u'Comentario'))
        

    # def save(self, *args, **kwargs):
    #     # Limpiar espacios y convertir a minúsculas los campos `talla` y `color`
    #     if self.talla:
    #         self.talla = self.talla.replace(" ", "").lower()
    #     if self.color:
    #         self.color = self.color.replace(" ", "").lower()

    #     # Calcular subtotal
    #     self.tipo, self.number = self.ip.tipo, self.ip.number
    #     self.subtotal = self.cost * self.qty

    #     # Generar código basado en el código del producto relacionado
    #     item_codigo = self.item.codigo if self.item and hasattr(self.item, 'codigo') else 'undefined'
    #     self.codigo = f"{item_codigo}-{self.talla or ''}-{self.color or ''}"

    #     # Guardar la instancia actual
    #     super().save(*args, **kwargs)

    #     # Actualizar el total de la instancia relacionada `ip` después de guardar
    #     total_calculado = self.ip.detalles.aggregate(Sum('subtotal'))['subtotal__sum'] or 0
    #     self.ip.total = total_calculado
    #     self.ip.save()

    def save(self, *args, **kwargs):
        """
        Guarda la instancia asegurando que los datos sean consistentes en el inventario.
        """

        # Limpiar espacios y convertir a minúsculas `talla` y `color`
        if self.talla:
            self.talla = self.talla.replace(" ", "").lower()
        if self.color:
            self.color = self.color.replace(" ", "").lower()

        # Calcular subtotal
        self.tipo, self.number = self.ip.tipo, self.ip.number
        self.subtotal = self.cost * self.qty

        # Generar código basado en item, talla y color
        new_codigo = self.item.codigo if self.item and hasattr(self.item, 'codigo') else 'undefined'
        item_codigo = new_codigo.replace(" ", "").lower()
        nuevo_codigo = f"{item_codigo}-{self.talla or ''}-{self.color or ''}"

        # Verificar si es una actualización (no una creación)
        old_instance = Ipdet.objects.filter(pk=self.pk).first() if self.pk else None

       

        if old_instance:
            # Buscar el item en inventario
            item = ItemactItem.objects.filter(codigo=old_instance.codigo).first()

            if item:
                # Calcular la diferencia en cantidades
                Q_actual = old_instance.qty
                Q_nueva = self.qty
                Q_diferencia = Q_actual - Q_nueva  
                Q_consolidada = item.qty_available
                Q_nueva_consolidada = Q_consolidada - Q_diferencia

    
                if nuevo_codigo != old_instance.codigo:
                    print(f"El código ha cambiado de {old_instance.codigo} a {nuevo_codigo}")
                    # if Q_actual != Q_nueva:
                    #     item.qty_available = Q_nueva_consolidada
                    #     item.save(update_fields=['qty_available'])
                    item.qty_available -= Q_actual  # Restar la cantidad anterior del inventario anterior
                    if item.qty_available < 0:
                        raise ValidationError("No se puede realizar el cambio porque el inventario anterior quedaría en negativo.")
                    item.save(update_fields=['qty_available'])

                    # if item_nuevo:
                    #     item_nuevo.qty_available += Q_nueva  # Agregar la nueva cantidad en el nuevo inventario
                    #     item_nuevo.save(update_fields=['qty_available'])

                # Caso 2: Cambio de cantidad
                elif Q_actual != Q_nueva:
                    # Actualizar la cantidad disponible del ítem
                    item.qty_available = Q_nueva_consolidada
                    item.save(update_fields=['qty_available'])


        # Guardar la instancia actual
        self.codigo = nuevo_codigo  # Asignar el nuevo código
        super().save(*args, **kwargs)

        # Actualizar el total de `ip`
        total_calculado = self.ip.detalles.aggregate(Sum('subtotal'))['subtotal__sum'] or 0
        self.ip.total = total_calculado
        self.ip.save()



    def delete(self, *args, **kwargs):
        # Verificar si eliminarlo haría que el inventario quede en negativo
        item = ItemactItem.objects.filter(codigo=self.codigo).first()  # Busca por código

        if item and (item.qty_available - self.qty) < 0:  # Validar si el inventario quedará negativo
            raise ValidationError("No se puede eliminar porque el inventario quedaría en negativo.")

        # Guardar la referencia a la Ip antes de eliminar el detalle
        ip = self.ip

        # Llamar al método delete original para eliminar el objeto
        super(Ipdet, self).delete(*args, **kwargs)

        # Recalcular el total de la Ip una vez eliminado el detalle
        total_calculado = ip.detalles.aggregate(Sum('subtotal'))['subtotal__sum'] or 0
        ip.total = total_calculado
        ip.save()

    
    class Meta:
        verbose_name = "Detalle"
        verbose_name_plural = "Detalles"

    def __str__(self):
        return str(self.ip)
