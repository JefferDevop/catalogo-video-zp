from django.db import models
from accounts.models import Account, Address
from products.models import Product



class Payment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    amount_paid = models.CharField(max_length=100) # this is the total amount paid
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_id


class Order(models.Model):
    STATUS = (
        ('PENDIENTE', 'Pendiente'),
        ('ACEPTADO', 'Aceptado'),
        ('DESPACHADO', 'Despachado'),
        ('ENTREGADO','Entregado'),
        ('CANCELADO','Cancelado'),
        ('RECHAZADO','Rechazado'),
        ('DEVUELTO', 'Devuelto')
    )

    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    order_note = models.CharField(max_length=100, blank=True)
    sub_total = models.FloatField(default = 0)
    discount = models.FloatField(default = 0)    
    tax = models.FloatField(default = 0)
    total = models.FloatField()
    status = models.CharField(max_length=10, choices=STATUS, default='Pendiente')
    ip = models.CharField(blank=True, max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'

    def __str__(self):
        return self.first_name


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.FloatField()
    tax = models.FloatField(default = 0)
    discount = models.FloatField(default = 0)
    total = models.FloatField(default = 0)
    sub_total = models.FloatField(default = 0)
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.product_name
