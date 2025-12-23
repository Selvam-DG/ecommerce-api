from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Order, OrderItem
from apps.cart.models import Cart
from .serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    OrderListSerializer,
    UpdateOrderStatusSerializer
)


class OrderListView(generics.ListAPIView):
    """API endpoint to list user's orders."""
    
    serializer_class = OrderListSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        """Return orders for current user."""
        return Order.objects.filter(user=self.request.user)


class OrderDetailView(generics.RetrieveAPIView):
    """API endpoint to retrieve order details."""
    
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        """Return orders for current user."""
        return Order.objects.filter(user=self.request.user)


class OrderCreateView(APIView):
    """API endpoint to create an order from cart."""
    
    permission_classes = (IsAuthenticated,)
    
    @transaction.atomic
    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Get user's cart
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response(
                {'error': 'Cart is empty.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if cart has items
        if not cart.items.exists():
            return Response(
                {'error': 'Cart is empty.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate stock availability
        for item in cart.items.all():
            if item.quantity > item.product.stock:
                return Response(
                    {'error': f'Insufficient stock for {item.product.name}. Only {item.product.stock} available.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Calculate order totals
        subtotal = cart.total_price
        shipping_cost = 10.00  # Fixed shipping cost for now
        tax = subtotal * 0.10  # 10% tax
        total = subtotal + shipping_cost + tax
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            tax=tax,
            total=total,
            **serializer.validated_data
        )
        
        # Create order items and update product stock
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                product_name=cart_item.product.name,
                product_price=cart_item.product.price,
                quantity=cart_item.quantity
            )
            
            # Update product stock
            product = cart_item.product
            product.stock -= cart_item.quantity
            product.save()
        
        # Clear cart
        cart.items.all().delete()
        
        return Response(
            {
                'message': 'Order created successfully.',
                'order': OrderSerializer(order).data
            },
            status=status.HTTP_201_CREATED
        )


class UpdateOrderStatusView(APIView):
    """API endpoint to update order status (admin only)."""
    
    permission_classes = (IsAuthenticated,)
    
    def patch(self, request, pk):
        # Check if user is admin
        if not request.user.is_staff:
            return Response(
                {'error': 'Only admins can update order status.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        order = get_object_or_404(Order, pk=pk)
        
        serializer = UpdateOrderStatusSerializer(
            data=request.data,
            context={'order': order}
        )
        
        if serializer.is_valid():
            order.status = serializer.validated_data['status']
            order.save()
            
            return Response(
                {
                    'message': 'Order status updated successfully.',
                    'order': OrderSerializer(order).data
                },
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CancelOrderView(APIView):
    """API endpoint to cancel an order."""
    
    permission_classes = (IsAuthenticated,)
    
    @transaction.atomic
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)
        
        # Check if order can be cancelled
        if order.status not in ['pending', 'processing']:
            return Response(
                {'error': f'Cannot cancel order with status: {order.status}.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Restore product stock
        for item in order.items.all():
            product = item.product
            product.stock += item.quantity
            product.save()
        
        # Update order status
        order.status = 'cancelled'
        order.save()
        
        return Response(
            {
                'message': 'Order cancelled successfully.',
                'order': OrderSerializer(order).data
            },
            status=status.HTTP_200_OK
        )