from django.contrib import admin
from .models import Payment, Refund


class RefundInline(admin.TabularInline):
    """Inline admin for refunds."""
    model = Refund
    extra = 0
    readonly_fields = ('amount', 'reason', 'status', 'created_at', 'processed_at')
    can_delete = False


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin configuration for Payment model."""
    
    list_display = (
        'id', 'order', 'user', 'payment_method', 'status', 
        'amount', 'currency', 'is_successful', 'created_at'
    )
    list_filter = ('payment_method', 'status', 'currency', 'created_at')
    search_fields = (
        'order__order_number', 'user__email', 'transaction_id',
        'stripe_payment_intent_id', 'paypal_order_id'
    )
    readonly_fields = (
        'order', 'user', 'amount', 'currency', 'transaction_id',
        'stripe_payment_intent_id', 'stripe_charge_id', 'stripe_customer_id',
        'paypal_order_id', 'paypal_payer_id', 'transaction_fee',
        'created_at', 'updated_at', 'paid_at', 'is_successful'
    )
    list_editable = ('status',)
    ordering = ('-created_at',)
    inlines = [RefundInline]
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('order', 'user', 'payment_method', 'status', 'amount', 'currency')
        }),
        ('Stripe Details', {
            'fields': (
                'stripe_payment_intent_id', 'stripe_charge_id', 'stripe_customer_id'
            ),
            'classes': ('collapse',)
        }),
        ('PayPal Details', {
            'fields': ('paypal_order_id', 'paypal_payer_id'),
            'classes': ('collapse',)
        }),
        ('Transaction Details', {
            'fields': ('transaction_id', 'transaction_fee', 'failure_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'paid_at')
        }),
    )
    
    def is_successful(self, obj):
        """Display whether payment was successful."""
        return obj.is_successful
    is_successful.boolean = True
    is_successful.short_description = 'Successful'


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    """Admin configuration for Refund model."""
    
    list_display = (
        'id', 'payment', 'amount', 'status', 'created_at', 'processed_at'
    )
    list_filter = ('status', 'created_at')
    search_fields = ('payment__order__order_number', 'payment__user__email', 'stripe_refund_id')
    readonly_fields = (
        'payment', 'amount', 'reason', 'stripe_refund_id',
        'created_at', 'updated_at', 'processed_at'
    )
    list_editable = ('status',)
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Refund Information', {
            'fields': ('payment', 'amount', 'reason', 'status')
        }),
        ('Stripe Details', {
            'fields': ('stripe_refund_id',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'processed_at')
        }),
    )