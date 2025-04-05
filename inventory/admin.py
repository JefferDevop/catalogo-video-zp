from django.contrib import admin
from .models import ItemactItem, Itemact


class ItemactAdmin(admin.ModelAdmin):
    list_display = ('ipdet', 'orderdet', 'item','talla', 'color', 'qty_ipdet', 'qty_orderdet', 'cost')
    search_fields = ('talla', 'color', 'codigo', 'item__name_extend',)
    list_filter = ('talla', 'color')

    # Configura list_display_links como vacío para no tener enlaces en los campos de la lista
    list_display_links = None

    def has_view_permission(self, request, obj=None):
        return False

    def get_fields(self, request, obj=None):
        fields = ('item', 'talla', 'color', 'qty_current', 'qty_discount', 'qty_available', 'discount', 'price', 'offer', 'active', 'soldout')
        return fields
    
    def get_readonly_fields(self, request, obj=None):
        return self.get_fields(request, obj)
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def changelist_view(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}  # Asegurar que no sea None
        extra_context['title'] = "Actividades de inventario"  # Cambia el título aquí
        return super().changelist_view(request, extra_context=extra_context)
    






class ItemactItemAdmin(admin.ModelAdmin):
    list_display = ('item', 'talla', 'color', 'qty_available', 'price1')
    search_fields = ('name', 'talla', 'color', 'codigo')
    list_filter = ('talla', 'color')
    list_per_page = 12

    def changelist_view(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}  # Asegurar que no sea None
        extra_context['title'] = "Listado de Existencias"  # Cambia el título aquí
        return super().changelist_view(request, extra_context=extra_context)
    

    # Configura list_display_links como vacío para no tener enlaces en los campos de la lista
    list_display_links = None

    def has_view_permission(self, request, obj=None):
        return False

    def get_fields(self, request, obj=None):
        fields = ('item', 'talla', 'color', 'qty_current', 'qty_discount', 'qty_available', 'discount', 'price', 'offer', 'active', 'soldout')
        return fields
    
    def get_readonly_fields(self, request, obj=None):
        return self.get_fields(request, obj)
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

    

    # def has_change_permission(self, request, obj=None):
    #     return False
    
    # def has_delete_permission(self, request, obj=None):
    #     return False
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(qty_available__gt=0)
       
    ordering = ('item',)


admin.site.register(ItemactItem, ItemactItemAdmin)
admin.site.register(Itemact, ItemactAdmin)
