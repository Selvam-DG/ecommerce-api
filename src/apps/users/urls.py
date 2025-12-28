from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegistrationView,
    UserLoginView,
    VerifyEmailView,
    ResendVerificationEmailView,
    UserProfileView,
    UserUpdateView,
    ChangePasswordView,
    RequestVendorRoleView,
    MyVendorRequestView,
    VendorRequestListView,
    ReviewVendorRequestView,
    AddressListCreateView,
    AddressDetailView,
)

app_name = 'users'

urlpatterns = [
    # Authentication
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Email Verification
    path('verify-email/', VerifyEmailView.as_view(), name='verify_email'),
    path('resend-verification/', ResendVerificationEmailView.as_view(), name='resend_verification'),
    
    # User Profile
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/update/', UserUpdateView.as_view(), name='profile_update'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    
    # Addresses
    path('addresses/', AddressListCreateView.as_view(), name='address_list_create'),
    path('addresses/<int:pk>/', AddressDetailView.as_view(), name='address_detail'),
    
    # Vendor Role Management
    path('request-vendor-role/', RequestVendorRoleView.as_view(), name='request_vendor_role'),
    path('my-vendor-request/', MyVendorRequestView.as_view(), name='my_vendor_request'),
    path('vendor-requests/', VendorRequestListView.as_view(), name='vendor_request_list'),
    path('vendor-requests/<int:pk>/review/', ReviewVendorRequestView.as_view(), name='review_vendor_request'),
]