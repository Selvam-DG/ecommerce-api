import stripe
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from .models import Payment, Refund

# Initialize Stripe with API key
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')


class StripePaymentService:
    """Service for handling Stripe payments."""
    
    @staticmethod
    def create_payment_intent(order, user):
        """Create a Stripe payment intent."""
        try:
            # Convert amount to cents (Stripe uses smallest currency unit)
            amount_cents = int(order.total * 100)
            
            # Create or get Stripe customer
            customer = StripePaymentService._get_or_create_customer(user)
            
            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency='usd',
                customer=customer.id,
                metadata={
                    'order_id': order.id,
                    'order_number': order.order_number,
                    'user_id': user.id,
                }
            )
            
            # Create payment record
            payment = Payment.objects.create(
                order=order,
                user=user,
                payment_method='stripe',
                status='pending',
                amount=order.total,
                currency='usd',
                stripe_payment_intent_id=intent.id,
                stripe_customer_id=customer.id,
            )
            
            return {
                'success': True,
                'payment_id': payment.id,
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id,
            }
        
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e),
            }
    
    @staticmethod
    def confirm_payment(payment_intent_id):
        """Confirm and retrieve payment intent from Stripe."""
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            # Get payment record
            payment = Payment.objects.get(stripe_payment_intent_id=payment_intent_id)
            
            if intent.status == 'succeeded':
                payment.status = 'completed'
                payment.paid_at = timezone.now()
                payment.transaction_id = intent.id
                
                # Update order status
                payment.order.status = 'processing'
                payment.order.save()
            elif intent.status == 'processing':
                payment.status = 'processing'
            elif intent.status in ['canceled', 'failed']:
                payment.status = 'failed'
                payment.failure_reason = intent.last_payment_error.message if intent.last_payment_error else 'Payment failed'
            
            payment.save()
            
            return {
                'success': True,
                'payment': payment,
                'status': intent.status,
            }
        
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e),
            }
        except Payment.DoesNotExist:
            return {
                'success': False,
                'error': 'Payment not found',
            }
    
    @staticmethod
    def create_refund(payment, amount, reason):
        """Create a refund for a payment."""
        try:
            # Convert amount to cents
            amount_cents = int(amount * 100)
            
            # Create refund in Stripe
            refund = stripe.Refund.create(
                payment_intent=payment.stripe_payment_intent_id,
                amount=amount_cents,
                reason='requested_by_customer',
                metadata={
                    'order_id': payment.order.id,
                    'refund_reason': reason,
                }
            )
            
            # Create refund record
            refund_obj = Refund.objects.create(
                payment=payment,
                amount=amount,
                reason=reason,
                status='processing',
                stripe_refund_id=refund.id,
            )
            
            # Update status if refund succeeded immediately
            if refund.status == 'succeeded':
                refund_obj.status = 'completed'
                refund_obj.processed_at = timezone.now()
                refund_obj.save()
                
                # Update payment status if fully refunded
                total_refunded = sum(
                    r.amount for r in payment.refunds.filter(status='completed')
                )
                if total_refunded >= payment.amount:
                    payment.status = 'refunded'
                    payment.save()
            
            return {
                'success': True,
                'refund': refund_obj,
            }
        
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e),
            }
    
    @staticmethod
    def _get_or_create_customer(user):
        """Get or create Stripe customer for user."""
        # Check if user already has a Stripe customer ID
        existing_payment = Payment.objects.filter(
            user=user,
            stripe_customer_id__isnull=False
        ).first()
        
        if existing_payment and existing_payment.stripe_customer_id:
            try:
                return stripe.Customer.retrieve(existing_payment.stripe_customer_id)
            except stripe.error.StripeError:
                pass
        
        # Create new customer
        customer = stripe.Customer.create(
            email=user.email,
            name=user.get_full_name(),
            metadata={
                'user_id': user.id,
            }
        )
        
        return customer
    
    @staticmethod
    def handle_webhook(event_type, payload):
        """Handle Stripe webhook events."""
        try:
            if event_type == 'payment_intent.succeeded':
                payment_intent = payload.get('data', {}).get('object', {})
                payment_intent_id = payment_intent.get('id')
                
                if payment_intent_id:
                    return StripePaymentService.confirm_payment(payment_intent_id)
            
            elif event_type == 'payment_intent.payment_failed':
                payment_intent = payload.get('data', {}).get('object', {})
                payment_intent_id = payment_intent.get('id')
                
                try:
                    payment = Payment.objects.get(stripe_payment_intent_id=payment_intent_id)
                    payment.status = 'failed'
                    payment.failure_reason = payment_intent.get('last_payment_error', {}).get('message', 'Payment failed')
                    payment.save()
                except Payment.DoesNotExist:
                    pass
            
            return {'success': True}
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
            }