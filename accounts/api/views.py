from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated 
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from rest_framework.views import APIView

from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView


from accounts.models import Account, Address
from accounts.api.serializers import UserSerializer, AddressSerializer


class AddressApiViewSet(ModelViewSet):  
    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer
    queryset = Address.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user_id', 'active', 'select']


class UserApiViewSet(ModelViewSet):
    #permission_classes = [IsAdminUser]
    serializer_class = UserSerializer
    queryset = Account.objects.all()

    def create(self, request, *args, **kwargs):
        # request.data._mutable = True
        request.data['password'] = make_password(request.data['password'])
        return super().create(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        password = request.data['password']
        if password:
            request.data['password'] = make_password(password)
        else:
            request.data['password'] = request.user.password
        return super().partial_update(request, *args, **kwargs)


# class TokenApiViewSet(ModelViewSet):

#     def post(self, request, *args, **kwargs):
#         usuario = request.GET.get('email', '')
#         contraseña = request.GET.get('password', '')

#         token_obtain_view = TokenObtainPairView.as_view()
#         response = token_obtain_view(request)

#         if response.status_code == 200:    
#             token = obtener_token(usuario, contraseña)         
#             return Response({'token': token}, status=status.HTTP_200_OK)
#         else:   
#             return Response({'error': 'Error en la autenticación inicial'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
