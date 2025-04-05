from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account, UserProfile, Address
from django.utils.html import format_html




class AddressAdmin(admin.ModelAdmin):
    list_display = ('title', 'email', 'name', 'lastname', 'address', 'city',  'phone', 'country', 'active')
    search_fields = ('name', 'address', 'city')
    list_filter = ('city',)
     
    ordering = ('name',)

class AccountAdmin(UserAdmin):
    list_display = ('email',  'date_joined', 'is_active')
    list_display_links = ('email', )
    readonly_fields = ('last_login', 'date_joined')
    ordering = ('-date_joined',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        return format_html('<img src="{}" width="130" style="border-radius:50%;">'.format(object.profile_picture.url))
    thumbnail.short_description = 'Profile Picture'
    list_display = ('thumbnail', 'user', 'city', 'state', 'country')

admin.site.register(Account, AccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Address, AddressAdmin)
