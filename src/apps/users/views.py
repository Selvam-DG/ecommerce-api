from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
    EmailVerificationSerializer,
    ResendVerificationSerializer,
    VendorRequestSerializer,
    VendorRequestCreateSerializer,
    VendorRequestReviewSerializer,
    AddressSerializer,
)
from .models import EmailVerificationToken, VendorRequest, Address
from .utils import send_verification_email

User = get_user_model()


# Address Views
class AddressListCreateView(generics.ListCreateAPIView):
    """API endpoint to list and create user addresses."""
    
    serializer_class = AddressSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint to retrieve, update, or delete an address."""
    
    serializer_class = AddressSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


class UserRegistrationView(generics.CreateAPIView):
    """API endpoint for user registration."""
    
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create verification token and send email
        token = EmailVerificationToken.objects.create(user=user)
        send_verification_email(user, token)
        
        return Response({
            'user': UserSerializer(user).data,
            'message': 'User registered successfully. Please check your email to verify your account.'
        }, status=status.HTTP_201_CREATED)


class VerifyEmailView(APIView):
    """API endpoint to verify email address."""
    
    permission_classes = (AllowAny,)
    
    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        token_uuid = serializer.validated_data['token']
        
        try:
            token = EmailVerificationToken.objects.get(token=token_uuid)
            
            if not token.is_valid():
                return Response(
                    {'error': 'Verification token has expired or already been used.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Mark token as used
            token.is_used = True
            token.save()
            
            # Verify user
            user = token.user
            user.is_verified = True
            user.save()
            
            return Response({
                'message': 'Email verified successfully. You can now login.',
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        
        except EmailVerificationToken.DoesNotExist:
            return Response(
                {'error': 'Invalid verification token.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ResendVerificationEmailView(APIView):
    """API endpoint to resend verification email."""
    
    permission_classes = (AllowAny,)
    
    def post(self, request):
        serializer = ResendVerificationSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        
        # Invalidate old tokens
        EmailVerificationToken.objects.filter(user=user, is_used=False).update(is_used=True)
        
        # Create new token and send email
        token = EmailVerificationToken.objects.create(user=user)
        send_verification_email(user, token)
        
        return Response({
            'message': 'Verification email sent successfully. Please check your inbox.'
        }, status=status.HTTP_200_OK)


class UserLoginView(TokenObtainPairView):
    """API endpoint for user login (JWT token)."""
    
    permission_classes = (AllowAny,)
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        # Check if user is verified
        if response.status_code == 200:
            email = request.data.get('email')
            try:
                user = User.objects.get(email=email)
                if not user.is_verified:
                    return Response({
                        'error': 'Email not verified. Please verify your email before logging in.',
                        'email': email
                    }, status=status.HTTP_403_FORBIDDEN)
            except User.DoesNotExist:
                pass
        
        return response


class UserProfileView(generics.RetrieveAPIView):
    """API endpoint to retrieve user profile."""
    
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user


class UserUpdateView(generics.UpdateAPIView):
    """API endpoint to update user profile."""
    
    permission_classes = (IsAuthenticated,)
    serializer_class = UserUpdateSerializer
    
    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """API endpoint for changing user password."""
    
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            user = request.user
            
            # Check old password
            if not user.check_password(serializer.data.get('old_password')):
                return Response(
                    {'old_password': ['Wrong password.']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Set new password
            user.set_password(serializer.data.get('new_password'))
            user.save()
            
            return Response(
                {'message': 'Password changed successfully.'},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RequestVendorRoleView(APIView):
    """API endpoint to request vendor role upgrade."""
    
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        serializer = VendorRequestCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Create vendor request
        vendor_request = serializer.save(user=request.user)
        
        # Update user status
        user = request.user
        user.vendor_request_pending = True
        user.vendor_request_date = timezone.now()
        user.save()
        
        return Response({
            'message': 'Vendor request submitted successfully. We will review your request shortly.',
            'request': VendorRequestSerializer(vendor_request).data
        }, status=status.HTTP_201_CREATED)


class MyVendorRequestView(generics.RetrieveAPIView):
    """API endpoint to view user's vendor request."""
    
    permission_classes = (IsAuthenticated,)
    serializer_class = VendorRequestSerializer
    
    def get_object(self):
        """Get the latest vendor request for current user."""
        return get_object_or_404(
            VendorRequest,
            user=self.request.user
        )


class VendorRequestListView(generics.ListAPIView):
    """API endpoint to list all vendor requests (Admin only)."""
    
    permission_classes = (IsAuthenticated,)
    serializer_class = VendorRequestSerializer
    
    def get_queryset(self):
        """Return vendor requests based on user role."""
        if not self.request.user.is_staff:
            return VendorRequest.objects.none()
        
        status_filter = self.request.query_params.get('status', None)
        queryset = VendorRequest.objects.all()
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset


class ReviewVendorRequestView(APIView):
    """API endpoint to review vendor request (Admin only)."""
    
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, pk):
        # Check if user is admin
        if not request.user.is_staff:
            return Response(
                {'error': 'Only admins can review vendor requests.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        vendor_request = get_object_or_404(VendorRequest, pk=pk)
        
        # Check if already reviewed
        if vendor_request.status != 'pending':
            return Response(
                {'error': 'This request has already been reviewed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = VendorRequestReviewSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        action = serializer.validated_data['action']
        review_notes = serializer.validated_data.get('review_notes', '')
        
        # Update vendor request
        vendor_request.status = 'approved' if action == 'approve' else 'rejected'
        vendor_request.reviewed_by = request.user
        vendor_request.review_notes = review_notes
        vendor_request.reviewed_at = timezone.now()
        vendor_request.save()
        
        # Update user if approved
        user = vendor_request.user
        if action == 'approve':
            user.role = 'vendor'
            user.vendor_approved_by = request.user
            user.vendor_approved_date = timezone.now()
        
        user.vendor_request_pending = False
        user.save()
        
        message = f'Vendor request {"approved" if action == "approve" else "rejected"} successfully.'
        
        return Response({
            'message': message,
            'request': VendorRequestSerializer(vendor_request).data,
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)