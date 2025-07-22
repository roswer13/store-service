from rest_framework import serializers

from products.models import Product
from categories.models import Category


class ProductSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True, allow_blank=False, error_messages={'blank': 'Product name cannot be blank.'})
    description = serializers.CharField(required=True, allow_blank=False, error_messages={'blank': 'Product description cannot be blank.'})
    price = serializers.FloatField(required=True)
    id_category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        error_messages={'does_not_exist': 'Category does not exist.'}
    )

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')