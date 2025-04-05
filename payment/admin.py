from django.contrib import admin
from .models import Payment, Item




# Registramos el modelo Item
# @admin.register(Item)
# class ItemAdmin(admin.ModelAdmin):
#     list_display = ('title', 'quantity', 'unit_price', 'codigo')

# Registramos el modelo Payment
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'required', 'pay', 'dispatched', 'delivered', 'transaction_amount', 'get_name', 'get_address', 'get_phone', 'created_at')

    readonly_fields = ('id', 'required', 'get_email', 'get_pass', 'transaction_amount', 'get_name', 'get_address', 'get_phone', 'payment_method_id', 'status', 'created_at')

    exclude = ('callback_url', 'ip_address', 'email', 'external_resource_url', 'status_detail', 'address', 'payment_type_id', 'entity_type',  'mercadopago_id')

    list_filter = (
        'created_at','required','dispatched','delivered'
    )

    # search_fields = ('id', 'get_name', 'transaction_amount', 'get_phone')
    # list_editable = ('dispatched', 'delivered')
    # list_per_page = 10
    # def get_readonly_fields(self, request, obj=None):
    #     if obj: # editing an existing object
    #         return self.readonly_fields + ('dispatched', 'delivered')
    #     return self.readonly_fields # creating a new object

    ordering = ('id','created_at')

    def get_address(self, obj):
        if obj.address:
            return f"{obj.address.address}, {obj.address.city}, {obj.address.country}"
        return 'No disponible'
    get_address.short_description = 'Dirección'

    def get_name(self, obj):
        if obj.address:
            return f"{obj.address.name} {obj.address.lastname}" 
        return 'No disponible'
    get_name.short_description = 'Nombre'

    def get_phone(self, obj):
        if obj.address:
            return obj.address.phone
        return 'No disponible'
    get_phone.short_description = 'Teléfono'

    def get_email(self, obj):
        if obj.address:
            return obj.address.email
        return 'No disponible'
    get_email.short_description = 'Correo'

    def get_pass(self, obj):
        if obj.address:
            return obj.address.password
        return 'No disponible'
    get_pass.short_description = 'Identificación'

    class ItemInline(admin.TabularInline):
        model = Item
        readonly_fields = [field.name for field in Item._meta.fields]
        extra = 0  

    inlines = [ItemInline] 