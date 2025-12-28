from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import VendorRequest, Address

User = get_user_model()


class AddressSerializer(serializers.ModelSerializer):
    """Serializer for user addresses."""
    
    class Meta:
        model = Address
        fields = (
            'id', 'address_type', 'full_name', 'phone', 
            'address_line1', 'address_line2', 'city', 'state', 
            'zip_code', 'country', 'is_default', 'notes',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ('email', 'password', 'password2', 'first_name', 'last_name', 'phone')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }
    
    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        """Create and return a new user with customer role."""
        validated_data.pop('password2')
        # All new users start as customers and unverified
        validated_data['role'] = 'customer'
        validated_data['is_verified'] = False
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user details."""
    
    full_name = serializers.SerializerMethodField()
    can_sell = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'full_name', 'phone', 
            'role', 'is_verified', 'can_sell', 'vendor_request_pending', 'date_joined'
        )
        read_only_fields = (
            'id', 'email', 'role', 'is_verified', 'vendor_request_pending', 'date_joined'
        )
    
    def get_full_name(self, obj):
        """Return user's full name."""
        return obj.get_full_name()
    
    def get_can_sell(self, obj):
        """Return whether user can sell products."""
        return obj.can_sell_products()


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone')


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change endpoint."""
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True)
    
    def validate(self, attrs):
        """Validate that new passwords match."""
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs


class EmailVerificationSerializer(serializers.Serializer):
    """Serializer for email verification."""
    
    token = serializers.UUIDField(required=True)
    
    def validate_token(self, value):
        """Validate that token exists and is valid."""
        from .models import EmailVerificationToken
        
        try:
            token = EmailVerificationToken.objects.get(token=value)
            if not token.is_valid():
                raise serializers.ValidationError("Verification token has expired or already been used.")
        except EmailVerificationToken.DoesNotExist:
            raise serializers.ValidationError("Invalid verification token.")
        
        return value


class ResendVerificationSerializer(serializers.Serializer):
    """Serializer for resending verification email."""
    
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """Validate that user exists and is not verified."""
        try:
            user = User.objects.get(email=value)
            if user.is_verified:
                raise serializers.ValidationError("Email is already verified.")
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        
        return value


class VendorRequestSerializer(serializers.ModelSerializer):
    """Serializer for vendor role upgrade request."""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    reviewed_by_email = serializers.EmailField(source='reviewed_by.email', read_only=True)
    
    class Meta:
        model = VendorRequest
        fields = (
            'id', 'user', 'user_email', 'business_name', 'business_description',
            'business_address', 'tax_id', 'status', 'reviewed_by', 'reviewed_by_email',
            'review_notes', 'created_at', 'updated_at', 'reviewed_at'
        )
        read_only_fields = (
            'id', 'user', 'status', 'reviewed_by', 'review_notes',
            'created_at', 'updated_at', 'reviewed_at'
        )


class VendorRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating vendor request."""
    
    class Meta:
        model = VendorRequest
        fields = ('business_name', 'business_description', 'business_address', 'tax_id')
    
    def validate(self, attrs):
        """Validate vendor request."""
        user = self.context['request'].user
        
        # Check if user is already a vendor
        if user.role == 'vendor':
            raise serializers.ValidationError("You are already a vendor.")
        
        # Check if user has pending request
        if VendorRequest.objects.filter(user=user, status='pending').exists():
            raise serializers.ValidationError("You already have a pending vendor request.")
        
        return attrs


class VendorRequestReviewSerializer(serializers.Serializer):
    """Serializer for reviewing vendor requests."""
    
    ACTION_CHOICES = [
        ('approve', 'Approve'),
        ('reject', 'Reject'),
    ]
    
    action = serializers.ChoiceField(choices=ACTION_CHOICES, required=True)
    review_notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_action(self, value):
        """Validate action."""
        if value not in ['approve', 'reject']:
            raise serializers.ValidationError("Invalid action. Must be 'approve' or 'reject'.")
        return value