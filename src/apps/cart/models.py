from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from apps.products.models import Product


class Cart(models.Model):
    """Shopping cart model."""
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'carts'
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'
    
    def __str__(self):
        return f"Cart of {self.user.email}"
    
    @property
    def total_items(self):
        """Return total number of items in cart."""
        return sum(item.quantity for item in self.items.all())
    
    @property
    def total_price(self):
        """Calculate total price of all items in cart."""
        return sum(item.subtotal for item in self.items.all())


class CartItem(models.Model):
    """Cart item model."""
    
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cart_items'
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ('cart', 'product')
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
    
    @property
    def subtotal(self):
        """Calculate subtotal for this item."""
        return self.product.price * self.quantity
    
    def clean(self):
        """Validate that quantity doesn't exceed stock."""
        from django.core.exceptions import ValidationError
        if self.quantity > self.product.stock:
            raise ValidationError(f'Only {self.product.stock} items available in stock.')
    
    def save(self, *args, **kwargs):
        """Validate before saving."""
        self.clean()
        super().save(*args, **kwargs)