from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.conf import settings
import stripe
import json

from .models import Payment, Refund
from apps.orders.models import Order
from .serializers import (
    PaymentSerializer,
    CreatePaymentIntentSerializer,
    ConfirmPaymentSerializer,
    CashOnDeliverySerializer,
    RefundSerializer,
    CreateRefundSerializer,
)
from .services import StripePaymentService


class PaymentListView(generics.ListAPIView):
    """API endpoint to list user's payments."""
    
    serializer_class = PaymentSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        """Return payments for current user."""
        return Payment.objects.filter(user=self.request.user)


class PaymentDetailView(generics.RetrieveAPIView):
    """API endpoint to retrieve payment details."""
    
    serializer_class = PaymentSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        """Return payments for current user."""
        return Payment.objects.filter(user=self.request.user)


class CreatePaymentIntentView(APIView):
    """API endpoint to create a payment intent."""
    
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        serializer = CreatePaymentIntentSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        order_id = serializer.validated_data['order_id']
        payment_method = serializer.validated_data['payment_method']
        
        # Get order
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        # Check if order is in valid state for payment
        if order.status not in ['pending']:
            return Response(
                {'error': 'Order cannot be paid at this stage.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if payment_method == 'stripe':
            # Create Stripe payment intent
            result = StripePaymentService.create_payment_intent(order, request.user)
            
            if result['success']:
                return Response({
                    'message': 'Payment intent created successfully.',
                    'payment_id': result['payment_id'],
                    'client_secret': result['client_secret'],
                    'payment_intent_id': result['payment_intent_id'],
                }, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {'error': result['error']},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        elif payment_method == 'cash':
            # Handle cash on delivery
            return Response(
                {'error': 'Use cash-on-delivery endpoint for this payment method.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        else:
            return Response(
                {'error': 'Payment method not supported yet.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ConfirmPaymentView(APIView):
    """API endpoint to confirm payment."""
    
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        serializer = ConfirmPaymentSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        payment_intent_id = serializer.validated_data['payment_intent_id']
        
        # Confirm payment with Stripe
        result = StripePaymentService.confirm_payment(payment_intent_id)
        
        if result['success']:
            return Response({
                'message': 'Payment confirmed successfully.',
                'payment': PaymentSerializer(result['payment']).data,
                'status': result['status'],
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': result['error']},
                status=status.HTTP_400_BAD_REQUEST
            )


class CashOnDeliveryView(APIView):
    """API endpoint for cash on delivery payment."""
    
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        serializer = CashOnDeliverySerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        order_id = serializer.validated_data['order_id']
        
        # Get order
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        # Check if order is in valid state
        if order.status != 'pending':
            return Response(
                {'error': 'Order cannot be paid at this stage.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create payment record for cash on delivery
        payment = Payment.objects.create(
            order=order,
            user=request.user,
            payment_method='cash',
            status='pending',
            amount=order.total,
            currency='USD',
        )
        
        # Update order status
        order.status = 'processing'
        order.save()
        
        return Response({
            'message': 'Order confirmed with cash on delivery.',
            'payment': PaymentSerializer(payment).data,
        }, status=status.HTTP_201_CREATED)


class CreateRefundView(APIView):
    """API endpoint to create a refund."""
    
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        serializer = CreateRefundSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        payment_id = serializer.validated_data['payment_id']
        amount = serializer.validated_data['amount']
        reason = serializer.validated_data['reason']
        
        # Get payment
        payment = get_object_or_404(Payment, id=payment_id, user=request.user)
        
        # Create refund based on payment method
        if payment.payment_method == 'stripe':
            result = StripePaymentService.create_refund(payment, amount, reason)
            
            if result['success']:
                return Response({
                    'message': 'Refund created successfully.',
                    'refund': RefundSerializer(result['refund']).data,
                }, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {'error': result['error']},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        elif payment.payment_method == 'cash':
            # Create manual refund record
            refund = Refund.objects.create(
                payment=payment,
                amount=amount,
                reason=reason,
                status='pending',
            )
            
            return Response({
                'message': 'Refund request created. Please contact support for processing.',
                'refund': RefundSerializer(refund).data,
            }, status=status.HTTP_201_CREATED)
        
        else:
            return Response(
                {'error': 'Refund not supported for this payment method.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class StripeWebhookView(APIView):
    """API endpoint to handle Stripe webhooks."""
    
    permission_classes = (AllowAny,)
    
    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')
        
        try:
            # Verify webhook signature
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError:
            return Response({'error': 'Invalid payload'}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError:
            return Response({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Handle the event
        event_type = event['type']
        result = StripePaymentService.handle_webhook(event_type, event)
        
        if result['success']:
            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': result.get('error', 'Unknown error')}, status=status.HTTP_400_BAD_REQUEST)


class RefundListView(generics.ListAPIView):
    """API endpoint to list refunds."""
    
    serializer_class = RefundSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        """Return refunds for current user's payments."""
        return Refund.objects.filter(payment__user=self.request.user)