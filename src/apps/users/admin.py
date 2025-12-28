from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from .models import EmailVerificationToken, VendorRequest, Address

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for custom User model."""
    
    list_display = (
        'email', 'first_name', 'last_name', 'role', 'is_active', 
        'is_verified', 'vendor_request_pending', 'date_joined'
    )
    list_filter = (
        'role', 'is_active', 'is_verified', 'vendor_request_pending', 
        'is_staff', 'date_joined'
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone')}),
        ('Role & Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 
                      'is_verified', 'groups', 'user_permissions')
        }),
        ('Vendor Info', {
            'fields': ('vendor_request_pending', 'vendor_request_date', 
                      'vendor_approved_by', 'vendor_approved_date'),
            'classes': ('collapse',)
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'role'),
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login', 'vendor_request_date', 'vendor_approved_date')
    
    def get_readonly_fields(self, request, obj=None):
        """Make vendor_approved_by readonly after it's set."""
        readonly = list(self.readonly_fields)
        if obj and obj.vendor_approved_by:
            readonly.append('vendor_approved_by')
        return readonly


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    """Admin configuration for EmailVerificationToken model."""
    
    list_display = ('user', 'token', 'created_at', 'expires_at', 'is_used', 'is_valid_status')
    list_filter = ('is_used', 'created_at', 'expires_at')
    search_fields = ('user__email', 'token')
    readonly_fields = ('token', 'created_at', 'expires_at', 'is_valid_status')
    ordering = ('-created_at',)
    
    def is_valid_status(self, obj):
        """Display whether token is valid."""
        if obj.is_valid():
            return format_html('<span style="color: green;">✓ Valid</span>')
        return format_html('<span style="color: red;">✗ Invalid/Expired</span>')
    is_valid_status.short_description = 'Status'
    
    def has_add_permission(self, request):
        """Disable manual token creation."""
        return False


@admin.register(VendorRequest)
class VendorRequestAdmin(admin.ModelAdmin):
    """Admin configuration for VendorRequest model."""
    
    list_display = (
        'user', 'business_name', 'status', 'created_at', 'reviewed_by', 'reviewed_at'
    )
    list_filter = ('status', 'created_at', 'reviewed_at')
    search_fields = ('user__email', 'business_name', 'business_description')
    readonly_fields = ('user', 'created_at', 'updated_at', 'reviewed_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Request Information', {
            'fields': ('user', 'business_name', 'business_description', 
                      'business_address', 'tax_id', 'status')
        }),
        ('Review Information', {
            'fields': ('reviewed_by', 'review_notes', 'reviewed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_requests', 'reject_requests']
    
    def approve_requests(self, request, queryset):
        """Bulk approve vendor requests."""
        from django.utils import timezone
        
        count = 0
        for vendor_request in queryset.filter(status='pending'):
            vendor_request.status = 'approved'
            vendor_request.reviewed_by = request.user
            vendor_request.reviewed_at = timezone.now()
            vendor_request.save()
            
            # Update user role
            user = vendor_request.user
            user.role = 'vendor'
            user.vendor_approved_by = request.user
            user.vendor_approved_date = timezone.now()
            user.vendor_request_pending = False
            user.save()
            
            count += 1
        
        self.message_user(request, f'{count} vendor request(s) approved successfully.')
    approve_requests.short_description = 'Approve selected vendor requests'
    
    def reject_requests(self, request, queryset):
        """Bulk reject vendor requests."""
        from django.utils import timezone
        
        count = 0
        for vendor_request in queryset.filter(status='pending'):
            vendor_request.status = 'rejected'
            vendor_request.reviewed_by = request.user
            vendor_request.reviewed_at = timezone.now()
            vendor_request.save()
            
            # Update user status
            user = vendor_request.user
            user.vendor_request_pending = False
            user.save()
            
            count += 1
        
        self.message_user(request, f'{count} vendor request(s) rejected.')
    reject_requests.short_description = 'Reject selected vendor requests'
    
    
