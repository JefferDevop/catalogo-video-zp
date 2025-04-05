from django.contrib import admin
from .models import Order, Orderdet
from inventory.models import ItemactItem
from django import forms


class OrderdetInlineForm(forms.ModelForm):
    class Meta:
        model = Orderdet
        fields = '__all__'

    # Sobrescribimos el queryset para que muestre los productos desde ItemactItem
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar productos donde qty_available sea mayor que 0
        self.fields['item'].queryset = ItemactItem.objects.filter(qty_available__gt=0) # Usar el modelo ItemactItem para el campo 'item'


class IpdetInline(admin.TabularInline):
    model = Orderdet
    form = OrderdetInlineForm  # Usar el formulario que ajusta el queryset
    readonly_fields = ('subtotal',)
    extra = 0  # Puedes ajustar esto según tus necesidades


class IpAdmin(admin.ModelAdmin):    
    list_display = ('tipo', 'number', 'total', 'created_date')
    list_display_links = ('tipo', 'number', 'total', 'created_date')
    search_fields = ('number', 'created_data',)
    readonly_fields = ('total',)
    inlines = [IpdetInline]    
    list_per_page = 6

# Registrar el modelo en el admin
admin.site.register(Order, IpAdmin)