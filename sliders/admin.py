from django.contrib import admin
from .models import Slider

class SliderAdmin(admin.ModelAdmin):    
    list_display = ('order', )
    list_display_links = ('order',)  
    
admin.site.register(Slider, SliderAdmin)