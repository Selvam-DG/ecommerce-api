from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.products.models import Product
from apps.orders.models import Order


class Review(models.Model):
    """Product review model."""
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    order = models.ForeignKey(
        Order, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='reviews',
        help_text='Order from which this review was made (for verified purchase)'
    )
    
    # Review content
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Rating from 1 to 5 stars'
    )
    title = models.CharField(max_length=200)
    comment = models.TextField()
    
    # Review metadata
    is_verified_purchase = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    
    # Helpful tracking
    helpful_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reviews'
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-created_at']
        unique_together = ('product', 'user', 'order')
        indexes = [
            models.Index(fields=['product', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"Review by {self.user.get_full_name()} for {self.product.name} - {self.rating}★"
    
    def save(self, *args, **kwargs):
        """Set verified purchase status based on order."""
        if self.order:
            # Check if order is delivered
            if self.order.status == 'delivered':
                self.is_verified_purchase = True
        super().save(*args, **kwargs)


class ReviewHelpful(models.Model):
    """Track which users found a review helpful."""
    
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='helpful_votes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'review_helpful'
        verbose_name = 'Review Helpful Vote'
        verbose_name_plural = 'Review Helpful Votes'
        unique_together = ('review', 'user')
    
    def __str__(self):
        return f"{self.user.email} found review #{self.review.id} helpful"
    
    def save(self, *args, **kwargs):
        """Increment helpful count on review."""
        super().save(*args, **kwargs)
        self.review.helpful_count = self.review.helpful_votes.count()
        self.review.save(update_fields=['helpful_count'])
    
    def delete(self, *args, **kwargs):
        """Decrement helpful count on review."""
        super().delete(*args, **kwargs)
        self.review.helpful_count = self.review.helpful_votes.count()
        self.review.save(update_fields=['helpful_count'])


class ReviewReport(models.Model):
    """Model for reporting inappropriate reviews."""
    
    REPORT_REASON_CHOICES = [
        ('spam', 'Spam'),
        ('offensive', 'Offensive Language'),
        ('fake', 'Fake Review'),
        ('irrelevant', 'Irrelevant Content'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('dismissed', 'Dismissed'),
        ('action_taken', 'Action Taken'),
    ]
    
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='reports')
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reason = models.CharField(max_length=20, choices=REPORT_REASON_CHOICES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Admin response
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_reports'
    )
    admin_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'review_reports'
        verbose_name = 'Review Report'
        verbose_name_plural = 'Review Reports'
        ordering = ['-created_at']
        unique_together = ('review', 'reported_by')
    
    def __str__(self):
        return f"Report for review #{self.review.id} - {self.reason}"


class VendorResponse(models.Model):
    """Vendor response to a review."""
    
    review = models.OneToOneField(Review, on_delete=models.CASCADE, related_name='vendor_response')
    vendor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'vendor_responses'
        verbose_name = 'Vendor Response'
        verbose_name_plural = 'Vendor Responses'
    
    def __str__(self):
        return f"Response to review #{self.review.id} by {self.vendor.email}"