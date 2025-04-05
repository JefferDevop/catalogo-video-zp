from django.contrib import admin
from .models import Ip, Ipdet
from products.models import Product
from django import forms
from django.shortcuts import render
from django.urls import path
from django.contrib import messages


class CsvImportForm(forms.Form):
    csv_upload = forms.FileField()


# class ValorAttributInline(admin.TabularInline):
#     model = Ipdet.valores_atributos.through
#     extra = 1


# class AttributInline(admin.TabularInline):
#     model = Attribut
#     extra = 1


# class IpdetInline(admin.TabularInline):
#     model = Ipdet
#     extra = 0  # No agregar formularios vacíos por defecto
#     exclude = ('discount', 'codigo', 'tipo', 'price')  # Ocultar campos innecesarios
#     readonly_fields = ('subtotal',)

#     def formfield_for_dbfield(self, db_field, **kwargs):
#         """Modifica el tamaño del campo para mejorar la UI en Django Admin"""
#         if db_field.name in ['talla', 'color', 'qty', 'cost']:
#             kwargs['widget'] = forms.TextInput(attrs={'size': '5'})  # Tamaño más visible
#         return super().formfield_for_dbfield(db_field, **kwargs)
        
    
class IpdetInline(admin.TabularInline):
    model = Ipdet
    extra = 0  # No agregar formularios vacíos por defecto
    exclude = ('discount', 'codigo', 'tipo', 'price')  # Ocultar campos innecesarios
    readonly_fields = ('subtotal',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Filtra las opciones del campo de clave foránea para mostrar
        solo los productos con 'service' establecido en False.
        """
        if db_field.name == 'item':  # Asegúrate de que 'product' es el nombre correcto del campo
            kwargs['queryset'] = Product.objects.filter(service=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """Modifica el tamaño del campo para mejorar la UI en Django Admin"""
        if db_field.name in ['talla', 'color', 'qty', 'cost']:
            kwargs['widget'] = forms.TextInput(attrs={'size': '5'})  # Tamaño más visible
        return super().formfield_for_dbfield(db_field, request, **kwargs)

class IpAdmin(admin.ModelAdmin):    
    list_display = ('tipo', 'number', 'concept','total', 'created_date')
    list_display_links = ('tipo', 'concept', 'number', 'total', 'created_date')
    search_fields = ('number', 'concept', 'created_date')
    readonly_fields = ('total',)
    inlines = [IpdetInline]    
    list_per_page = 12
    


    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path("upload-csv/", self.upload_csv),
        ]
        return new_urls + urls

    def upload_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES.get("csv_upload")

        form = CsvImportForm()
        data = {"form": form}
        return render(request, "admin/csv_receipts.html", data)
    
    # def has_delete_permission(self, request, obj=None):
    #     return True





# class IpdetAdmin(admin.ModelAdmin):
#     list_display = ('item', 'qty', 'atributos_asociados')
#     list_filter = ('item', )
#     inlines = [ValorAttributInline]








    
admin.site.register(Ip, IpAdmin)
# admin.site.register(Ipdet, IpdetAdmin)
