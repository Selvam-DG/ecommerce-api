from rest_framework import serializers
from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""
    
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'is_active', 'product_count', 'created_at', 'updated_at')
        read_only_fields = ('id', 'slug', 'created_at', 'updated_at')
    
    def get_product_count(self, obj):
        """Return count of active products in category."""
        return obj.products.filter(is_active=True).count()


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    in_stock = serializers.BooleanField(read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Product
        fields = (
            'id', 'name', 'slug', 'description', 'price', 'stock', 
            'category', 'category_name', 'image', 'is_active', 'is_featured',
            'in_stock', 'created_by', 'created_by_name', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'slug', 'created_by', 'created_at', 'updated_at')
    
    def validate_price(self, value):
        """Validate that price is positive."""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0.")
        return value
    
    def validate_stock(self, value):
        """Validate that stock is not negative."""
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative.")
        return value


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for product list."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    in_stock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Product
        fields = ('id', 'name', 'slug', 'price', 'stock', 'category_name', 'image', 'is_active', 'is_featured', 'in_stock')


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating products."""
    
    class Meta:
        model = Product
        fields = ('name', 'description', 'price', 'stock', 'category', 'image', 'is_active', 'is_featured')
    
    def validate_price(self, value):
        """Validate that price is positive."""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0.")
        return value
    
    def validate_stock(self, value):
        """Validate that stock is not negative."""
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative.")
        return value