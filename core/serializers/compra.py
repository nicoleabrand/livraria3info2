from rest_framework.serializers import CharField, ModelSerializer, SerializerMethodField
from core.models import Compra, ItensCompra
from rest_framework.serializers import (
    CharField,
    CurrentUserDefault,
    DateTimeField, # novo
    HiddenField,
    ModelSerializer,
    SerializerMethodField,
    ValidationError,
)

class ItensCompraCreateUpdateSerializer(ModelSerializer):
    class Meta:
        model = ItensCompra
        fields = ('livro', 'quantidade', 'preco')

    def validate_quantidade(self, quantidade):
        if quantidade <= 0:
            raise ValidationError('A quantidade deve ser maior do que zero.')
        return quantidade
    def validate(self, item):
        if item['quantidade'] > item['livro'].quantidade:
            raise ValidationError('Quantidade de itens maior do que a quantidade em estoque.')
        return item

class ItensCompraSerializer(ModelSerializer):
    total = SerializerMethodField()
    class Meta:
        model = ItensCompra
        fields = ('livro', 'quantidade', 'total')
        depth = 1

    def get_total(self, instance):
        return instance.quantidade * instance.livro.preco
    def get_total(self, instance):
        return instance.quantidade * instance.preco
   
class CompraCreateUpdateSerializer(ModelSerializer):
    itens = ItensCompraCreateUpdateSerializer(many=True)
    usuario = HiddenField(default=CurrentUserDefault())

    class Meta:
        model = Compra
        fields = ('id', 'usuario', 'itens')

    def create(self, validated_data):
        itens_data = validated_data.pop('itens')
        compra = Compra.objects.create(**validated_data)
        for item_data in itens_data:
            ItensCompra.objects.create(compra=compra, **item_data)
        compra.save()
        return compra
    
    def update(self, compra, validated_data):
        itens = validated_data.pop('itens')
        if itens:
            compra.itens.all().delete()
            for item in itens:
                item['preco'] = item['livro'].preco  # grava o preço histórico
                ItensCompra.objects.create(compra=compra, **item)
        compra.save()
        return super().update(compra, validated_data)
    def create(self, validated_data):
        itens = validated_data.pop('itens')
        compra = Compra.objects.create(**validated_data)
        for item in itens:
            item['preco'] = item['livro'].preco # preço do livro no momento da compra
            ItensCompra.objects.create(compra=compra, **item)
        compra.save()
        return compra

class CompraSerializer(ModelSerializer):
    usuario = CharField(source='usuario.email', read_only=True)
    status = CharField(source='get_status_display', read_only=True)
    data = DateTimeField(read_only=True) # novo campo
    itens = ItensCompraSerializer(many=True, read_only=True)

    class Meta:
        model = Compra
        fields = ('id', 'usuario', 'status', 'total', 'data', 'itens') # modificado


class ItensCompraListSerializer(ModelSerializer):
    livro = CharField(source='livro.titulo', read_only=True)

    class Meta:
        model = ItensCompra
        fields = ('quantidade', 'preco', 'livro')  # mudou
        depth = 1

class CompraListSerializer(ModelSerializer):
    usuario = CharField(source='usuario.email', read_only=True)
    itens = ItensCompraListSerializer(many=True, read_only=True)

    class Meta:
        model = Compra
        fields = ('id', 'usuario', 'itens')
