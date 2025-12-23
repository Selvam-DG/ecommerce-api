from django.urls import path
from .views import (
    OrderListView,
    OrderDetailView,
    OrderCreateView,
    UpdateOrderStatusView,
    CancelOrderView
)

app_name = 'orders'

urlpatterns = [
    path('', OrderListView.as_view(), name='order_list'),
    path('create/', OrderCreateView.as_view(), name='order_create'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('<int:pk>/status/', UpdateOrderStatusView.as_view(), name='update_order_status'),
    path('<int:pk>/cancel/', CancelOrderView.as_view(), name='cancel_order'),
]