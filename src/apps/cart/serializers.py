from rest_framework import serializers
from .models import Cart, CartItem
from apps.products.models import Product


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for cart items."""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    product_image = serializers.ImageField(source='product.image', read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_name', 'product_price', 'product_image', 'quantity', 'subtotal', 'created_at')
        read_only_fields = ('id', 'created_at')
    
    def validate_quantity(self, value):
        """Validate quantity."""
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1.")
        return value
    
    def validate(self, attrs):
        """Validate that product is available in requested quantity."""
        product = attrs.get('product')
        quantity = attrs.get('quantity', 1)
        
        if not product.is_active:
            raise serializers.ValidationError("This product is not available.")
        
        if quantity > product.stock:
            raise serializers.ValidationError(f"Only {product.stock} items available in stock.")
        
        return attrs


class CartSerializer(serializers.ModelSerializer):
    """Serializer for shopping cart."""
    
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Cart
        fields = ('id', 'items', 'total_items', 'total_price', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class AddToCartSerializer(serializers.Serializer):
    """Serializer for adding items to cart."""
    
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1, min_value=1)
    
    def validate_product_id(self, value):
        """Validate that product exists and is active."""
        try:
            product = Product.objects.get(id=value, is_active=True)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found or not available.")
        return value
    
    def validate(self, attrs):
        """Validate that product has enough stock."""
        product_id = attrs['product_id']
        quantity = attrs['quantity']
        
        try:
            product = Product.objects.get(id=product_id)
            if quantity > product.stock:
                raise serializers.ValidationError(f"Only {product.stock} items available in stock.")
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found.")
        
        return attrs


class UpdateCartItemSerializer(serializers.Serializer):
    """Serializer for updating cart item quantity."""
    
    quantity = serializers.IntegerField(min_value=1)