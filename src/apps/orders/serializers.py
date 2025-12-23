from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items."""
    
    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'product_price', 'quantity', 'subtotal')
        read_only_fields = ('id', 'product_name', 'product_price', 'subtotal')


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for orders."""
    
    items = OrderItemSerializer(many=True, read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Order
        fields = (
            'id', 'order_number', 'user', 'user_email', 'status',
            'shipping_address', 'shipping_city', 'shipping_state', 
            'shipping_zip_code', 'shipping_country', 'phone_number',
            'subtotal', 'shipping_cost', 'tax', 'total', 'notes',
            'items', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'order_number', 'user', 'created_at', 'updated_at')


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating orders."""
    
    class Meta:
        model = Order
        fields = (
            'shipping_address', 'shipping_city', 'shipping_state',
            'shipping_zip_code', 'shipping_country', 'phone_number', 'notes'
        )
    
    def validate(self, attrs):
        """Validate shipping information."""
        if not attrs.get('shipping_address'):
            raise serializers.ValidationError("Shipping address is required.")
        if not attrs.get('shipping_city'):
            raise serializers.ValidationError("Shipping city is required.")
        if not attrs.get('phone_number'):
            raise serializers.ValidationError("Phone number is required.")
        return attrs


class OrderListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for order list."""
    
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ('id', 'order_number', 'status', 'total', 'item_count', 'created_at')
    
    def get_item_count(self, obj):
        """Return total number of items in order."""
        return obj.items.count()


class UpdateOrderStatusSerializer(serializers.Serializer):
    """Serializer for updating order status."""
    
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
    
    def validate_status(self, value):
        """Validate status transition."""
        order = self.context.get('order')
        
        # Define valid status transitions
        valid_transitions = {
            'pending': ['processing', 'cancelled'],
            'processing': ['shipped', 'cancelled'],
            'shipped': ['delivered'],
            'delivered': [],
            'cancelled': []
        }
        
        current_status = order.status
        if value not in valid_transitions.get(current_status, []):
            raise serializers.ValidationError(
                f"Cannot transition from {current_status} to {value}."
            )
        
        return value