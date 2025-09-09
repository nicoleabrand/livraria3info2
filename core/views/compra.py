from rest_framework.viewsets import ModelViewSet
from rest_framework.viewsets import ModelViewSet
from core.models import Compra
from core.serializers.compra import (
    CompraCreateUpdateSerializer,
    CompraListSerializer,
    CompraSerializer,
)
from core.serializers import CompraCreateUpdateSerializer, CompraListSerializer, CompraSerializer

class CompraViewSet(ModelViewSet):
    def get_queryset(self):
        usuario = self.request.user
        if usuario.is_superuser:
            return Compra.objects.all()
        if usuario.groups.filter(name='administradores'):
            return Compra.objects.all()
        return Compra.objects.filter(usuario=usuario)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return CompraCreateUpdateSerializer
        return CompraSerializer
        
    def get_serializer_class(self):
        if self.action == 'list':
            return CompraListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return CompraCreateUpdateSerializer
        return CompraSerializer