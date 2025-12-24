from rest_framework import serializers
from .models import Payment, Refund


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payment details."""
    
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    is_successful = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Payment
        fields = (
            'id', 'order', 'order_number', 'user', 'user_email',
            'payment_method', 'status', 'amount', 'currency',
            'transaction_id', 'transaction_fee', 'failure_reason',
            'is_successful', 'created_at', 'updated_at', 'paid_at'
        )
        read_only_fields = (
            'id', 'user', 'transaction_id', 'transaction_fee',
            'created_at', 'updated_at', 'paid_at'
        )


class CreatePaymentIntentSerializer(serializers.Serializer):
    """Serializer for creating payment intent."""
    
    order_id = serializers.IntegerField()
    payment_method = serializers.ChoiceField(choices=Payment.PAYMENT_METHOD_CHOICES)
    
    def validate_order_id(self, value):
        """Validate that order exists and belongs to user."""
        from apps.orders.models import Order
        
        try:
            order = Order.objects.get(id=value)
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found.")
        
        # Check if order already has a payment
        if hasattr(order, 'payment'):
            if order.payment.status in ['completed', 'processing']:
                raise serializers.ValidationError("Order already has a payment.")
        
        return value


class ConfirmPaymentSerializer(serializers.Serializer):
    """Serializer for confirming payment."""
    
    payment_intent_id = serializers.CharField()
    
    def validate_payment_intent_id(self, value):
        """Validate payment intent ID."""
        if not value:
            raise serializers.ValidationError("Payment intent ID is required.")
        return value


class CashOnDeliverySerializer(serializers.Serializer):
    """Serializer for cash on delivery payment."""
    
    order_id = serializers.IntegerField()
    
    def validate_order_id(self, value):
        """Validate that order exists and belongs to user."""
        from apps.orders.models import Order
        
        try:
            order = Order.objects.get(id=value)
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found.")
        
        # Check if order already has a payment
        if hasattr(order, 'payment'):
            raise serializers.ValidationError("Order already has a payment.")
        
        return value


class RefundSerializer(serializers.ModelSerializer):
    """Serializer for refund details."""
    
    payment_order_number = serializers.CharField(source='payment.order.order_number', read_only=True)
    
    class Meta:
        model = Refund
        fields = (
            'id', 'payment', 'payment_order_number', 'amount', 'reason',
            'status', 'created_at', 'updated_at', 'processed_at'
        )
        read_only_fields = ('id', 'status', 'created_at', 'updated_at', 'processed_at')


class CreateRefundSerializer(serializers.Serializer):
    """Serializer for creating refund."""
    
    payment_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    reason = serializers.CharField()
    
    def validate_payment_id(self, value):
        """Validate that payment exists and is refundable."""
        try:
            payment = Payment.objects.get(id=value)
        except Payment.DoesNotExist:
            raise serializers.ValidationError("Payment not found.")
        
        if payment.status != 'completed':
            raise serializers.ValidationError("Only completed payments can be refunded.")
        
        return value
    
    def validate(self, attrs):
        """Validate refund amount."""
        payment_id = attrs.get('payment_id')
        amount = attrs.get('amount')
        
        try:
            payment = Payment.objects.get(id=payment_id)
            
            # Calculate total already refunded
            total_refunded = sum(
                refund.amount for refund in payment.refunds.filter(status='completed')
            )
            
            if amount > (payment.amount - total_refunded):
                raise serializers.ValidationError(
                    f"Refund amount cannot exceed remaining amount: {payment.amount - total_refunded}"
                )
        except Payment.DoesNotExist:
            pass
        
        return attrs


class PaymentWebhookSerializer(serializers.Serializer):
    """Serializer for payment webhook data."""
    
    event_type = serializers.CharField()
    payment_intent_id = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    status = serializers.CharField(required=False)