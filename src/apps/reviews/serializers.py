from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Review, ReviewHelpful, ReviewReport, VendorResponse
from apps.products.models import Product
from apps.orders.models import Order

User = get_user_model()


class VendorResponseSerializer(serializers.ModelSerializer):
    """Serializer for vendor responses."""
    
    vendor_name = serializers.CharField(source='vendor.get_full_name', read_only=True)
    
    class Meta:
        model = VendorResponse
        fields = ('id', 'response', 'vendor_name', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for product reviews."""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    vendor_response = VendorResponseSerializer(read_only=True)
    is_helpful = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = (
            'id', 'product', 'product_name', 'user', 'user_name',
            'order', 'rating', 'title', 'comment', 'is_verified_purchase',
            'is_approved', 'helpful_count', 'vendor_response',
            'is_helpful', 'can_edit', 'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'user', 'is_verified_purchase', 'is_approved',
            'helpful_count', 'created_at', 'updated_at'
        )
    
    def get_is_helpful(self, obj):
        """Check if current user found this review helpful."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ReviewHelpful.objects.filter(review=obj, user=request.user).exists()
        return False
    
    def get_can_edit(self, obj):
        """Check if current user can edit this review."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.user == request.user
        return False
    
    def validate_rating(self, value):
        """Validate rating is between 1 and 5."""
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
    
    def validate(self, attrs):
        """Validate review data."""
        request = self.context.get('request')
        product = attrs.get('product')
        
        # Check if user already reviewed this product
        if self.instance is None:  # Only on creation
            if Review.objects.filter(product=product, user=request.user).exists():
                raise serializers.ValidationError("You have already reviewed this product.")
        
        return attrs


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating reviews."""
    
    class Meta:
        model = Review
        fields = ('product', 'order', 'rating', 'title', 'comment')
    
    def validate_rating(self, value):
        """Validate rating is between 1 and 5."""
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
    
    def validate(self, attrs):
        """Validate that user can review this product."""
        request = self.context.get('request')
        product = attrs.get('product')
        order = attrs.get('order')
        
        # Check if user already reviewed this product
        if Review.objects.filter(product=product, user=request.user).exists():
            raise serializers.ValidationError("You have already reviewed this product.")
        
        # If order provided, validate it
        if order:
            # Check order belongs to user
            if order.user != request.user:
                raise serializers.ValidationError("This order doesn't belong to you.")
            
            # Check if product is in the order
            if not order.items.filter(product=product).exists():
                raise serializers.ValidationError("This product is not in the specified order.")
        
        return attrs


class ReviewListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for review lists."""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Review
        fields = (
            'id', 'user_name', 'rating', 'title', 'comment',
            'is_verified_purchase', 'helpful_count', 'created_at'
        )


class ReviewReportSerializer(serializers.ModelSerializer):
    """Serializer for review reports."""
    
    reported_by_name = serializers.CharField(source='reported_by.get_full_name', read_only=True)
    review_content = serializers.CharField(source='review.comment', read_only=True)
    
    class Meta:
        model = ReviewReport
        fields = (
            'id', 'review', 'review_content', 'reported_by', 'reported_by_name',
            'reason', 'description', 'status', 'admin_notes',
            'created_at', 'reviewed_at'
        )
        read_only_fields = (
            'id', 'reported_by', 'status', 'admin_notes',
            'created_at', 'reviewed_at'
        )


class VendorResponseCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating vendor responses."""
    
    class Meta:
        model = VendorResponse
        fields = ('response',)
    
    def validate(self, attrs):
        """Validate vendor response."""
        request = self.context.get('request')
        review = self.context.get('review')
        
        # Check if user is vendor or admin
        if request.user.role not in ['vendor', 'admin']:
            raise serializers.ValidationError("Only vendors can respond to reviews.")
        
        # Check if vendor owns the product (or is admin)
        if request.user.role == 'vendor':
            if review.product.created_by != request.user:
                raise serializers.ValidationError("You can only respond to reviews of your own products.")
        
        # Check if response already exists
        if hasattr(review, 'vendor_response'):
            raise serializers.ValidationError("Response already exists for this review.")
        
        return attrs


class MarkHelpfulSerializer(serializers.Serializer):
    """Serializer for marking review as helpful."""
    
    helpful = serializers.BooleanField()