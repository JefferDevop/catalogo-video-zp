from rest_framework import serializers
from accounts.models import Account, Address


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'username', 'email', 'first_name',
                  'last_name', 'password', 'is_active', 'is_staff']

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'title', 'name', 'lastname', 'address', 'email', 'password',
                  'city', 'country', 'active', 'phone', 'date_joined', 'select', 'user']