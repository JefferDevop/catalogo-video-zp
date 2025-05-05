from django.db import models
from accounts.models import Address

class Payment(models.Model):
    required = models.BooleanField(default=True, verbose_name='Solicitado')
    pay = models.BooleanField(default=False, verbose_name='Pagado')
    dispatched = models.BooleanField(default=False, verbose_name='Despachado')
    delivered = models.BooleanField(default=False, verbose_name='Entregado')    
    external_reference = models.CharField(max_length=255, null=True, blank=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='payments')
    mercadopago_id = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)
    status_detail = models.CharField(max_length=255, null=True, blank=True)
    payment_method_id = models.CharField(max_length=100, null=True, blank=True, verbose_name="Pago")
    payment_type_id = models.CharField(max_length=100, null=True, blank=True)
    transaction_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Total" )
    external_resource_url = models.URLField(max_length=500, null=True, blank=True)
    callback_url = models.URLField(max_length=500, blank=True, null=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    entity_type = models.CharField(max_length=50, default='individual')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.mercadopago_id
    
    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"




class Item(models.Model):
    payment = models.ForeignKey(Payment, related_name='items', on_delete=models.CASCADE)
    codigo = models.CharField(max_length=255, default='', verbose_name="Código")
    talla = models.CharField(max_length=30, null=True, blank=True, verbose_name="Talla")
    description = models.CharField(max_length=255, blank=True, null=True, default='', verbose_name="Descripción")
    title = models.CharField(max_length=255, verbose_name="Nombre")
    quantity = models.IntegerField(verbose_name="Cantidad")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    subtotal = models.DecimalField(max_digits=18, decimal_places=2, default=0.0, verbose_name="Total")
    currency_id = models.CharField(max_length=10)

    def save(self, *args, **kwargs):
        self.subtotal = self.unit_price * self.quantity
       
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    


class MercadoPagoNotification(models.Model):
    topic = models.CharField(max_length=250, null=True, blank=True, verbose_name="Tipo de Notificación")
    resource = models.TextField(null=True, blank=True, verbose_name="Recurso")
    action = models.CharField(max_length=100, null=True, blank=True, verbose_name="Acción")
    api_version = models.CharField(max_length=10, null=True, blank=True, verbose_name="Versión API")
    data_id = models.CharField(max_length=50, null=True, blank=True, verbose_name="ID de los Datos")
    date_created = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Creación")
    notification_id = models.BigIntegerField(null=True, blank=True, verbose_name="ID de Notificación")
    live_mode = models.BooleanField(default=False, verbose_name="Modo en Vivo")
    user_id = models.CharField(max_length=50, null=True, blank=True, verbose_name="ID del Usuario")
    
    date_received = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Recepción")

    class Meta:
        verbose_name = "Notificación de MercadoPago"
        verbose_name_plural = "Notificaciones de MercadoPago"

    def __str__(self):
        return f"{self.topic} - {self.data_id or self.resource}"