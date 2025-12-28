from django.contrib import admin
from django.utils.html import format_html
from .models import Review, ReviewHelpful, ReviewReport, VendorResponse


class VendorResponseInline(admin.StackedInline):
    """Inline admin for vendor responses."""
    model = VendorResponse
    extra = 0
    readonly_fields = ('vendor', 'created_at', 'updated_at')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin configuration for Review model."""
    
    list_display = (
        'id', 'product', 'user', 'rating_stars', 'is_verified_purchase',
        'is_approved', 'helpful_count', 'created_at'
    )
    list_filter = ('rating', 'is_verified_purchase', 'is_approved', 'created_at')
    search_fields = ('product__name', 'user__email', 'title', 'comment')
    readonly_fields = ('user', 'product', 'order', 'helpful_count', 'created_at', 'updated_at')
    list_editable = ('is_approved',)
    ordering = ('-created_at',)
    inlines = [VendorResponseInline]
    
    fieldsets = (
        ('Review Information', {
            'fields': ('product', 'user', 'order', 'rating', 'title', 'comment')
        }),
        ('Status', {
            'fields': ('is_verified_purchase', 'is_approved', 'helpful_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def rating_stars(self, obj):
        """Display rating as stars."""
        stars = '⭐' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="font-size: 16px;">{}</span>', stars)
    rating_stars.short_description = 'Rating'
    
    actions = ['approve_reviews', 'disapprove_reviews']
    
    def approve_reviews(self, request, queryset):
        """Bulk approve reviews."""
        count = queryset.update(is_approved=True)
        self.message_user(request, f'{count} review(s) approved.')
    approve_reviews.short_description = 'Approve selected reviews'
    
    def disapprove_reviews(self, request, queryset):
        """Bulk disapprove reviews."""
        count = queryset.update(is_approved=False)
        self.message_user(request, f'{count} review(s) disapproved.')
    disapprove_reviews.short_description = 'Disapprove selected reviews'


@admin.register(ReviewHelpful)
class ReviewHelpfulAdmin(admin.ModelAdmin):
    """Admin configuration for ReviewHelpful model."""
    
    list_display = ('review', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('review__product__name', 'user__email')
    readonly_fields = ('review', 'user', 'created_at')


@admin.register(ReviewReport)
class ReviewReportAdmin(admin.ModelAdmin):
    """Admin configuration for ReviewReport model."""
    
    list_display = (
        'id', 'review', 'reported_by', 'reason', 'status',
        'created_at', 'reviewed_at'
    )
    list_filter = ('reason', 'status', 'created_at')
    search_fields = ('review__product__name', 'reported_by__email', 'description')
    readonly_fields = ('review', 'reported_by', 'created_at')
    list_editable = ('status',)
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Report Information', {
            'fields': ('review', 'reported_by', 'reason', 'description', 'status')
        }),
        ('Admin Review', {
            'fields': ('reviewed_by', 'admin_notes', 'reviewed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_reviewed', 'mark_dismissed', 'mark_action_taken']
    
    def mark_reviewed(self, request, queryset):
        """Mark reports as reviewed."""
        from django.utils import timezone
        count = queryset.update(
            status='reviewed',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'{count} report(s) marked as reviewed.')
    mark_reviewed.short_description = 'Mark as reviewed'
    
    def mark_dismissed(self, request, queryset):
        """Mark reports as dismissed."""
        from django.utils import timezone
        count = queryset.update(
            status='dismissed',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'{count} report(s) dismissed.')
    mark_dismissed.short_description = 'Dismiss reports'
    
    def mark_action_taken(self, request, queryset):
        """Mark reports as action taken."""
        from django.utils import timezone
        count = queryset.update(
            status='action_taken',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'Action taken on {count} report(s).')
    mark_action_taken.short_description = 'Mark action taken'


@admin.register(VendorResponse)
class VendorResponseAdmin(admin.ModelAdmin):
    """Admin configuration for VendorResponse model."""
    
    list_display = ('review', 'vendor', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('review__product__name', 'vendor__email', 'response')
    readonly_fields = ('review', 'vendor', 'created_at', 'updated_at')