from django.urls import path
from .views import (
    CartView,
    AddToCartView,
    UpdateCartItemView,
    RemoveFromCartView,
    ClearCartView
)

app_name = 'cart'

urlpatterns = [
    path('', CartView.as_view(), name='cart'),
    path('add/', AddToCartView.as_view(), name='add_to_cart'),
    path('items/<int:item_id>/update/', UpdateCartItemView.as_view(), name='update_cart_item'),
    path('items/<int:item_id>/remove/', RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('clear/', ClearCartView.as_view(), name='clear_cart'),
]