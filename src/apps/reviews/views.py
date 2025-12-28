from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from .models import Review, ReviewHelpful, ReviewReport, VendorResponse
from apps.products.models import Product
from .serializers import (
    ReviewSerializer,
    ReviewCreateSerializer,
    ReviewListSerializer,
    ReviewReportSerializer,
    VendorResponseCreateSerializer,
    MarkHelpfulSerializer,
)


class ProductReviewListView(generics.ListAPIView):
    """API endpoint to list reviews for a product."""
    
    serializer_class = ReviewListSerializer
    permission_classes = (AllowAny,)
    
    def get_queryset(self):
        """Return approved reviews for the product."""
        product_id = self.kwargs.get('product_id')
        return Review.objects.filter(
            product_id=product_id,
            is_approved=True
        ).select_related('user')


class ProductReviewStatsView(APIView):
    """API endpoint to get review statistics for a product."""
    
    permission_classes = (AllowAny,)
    
    def get(self, request, product_id):
        reviews = Review.objects.filter(product_id=product_id, is_approved=True)
        
        stats = {
            'total_reviews': reviews.count(),
            'average_rating': reviews.aggregate(Avg('rating'))['rating__avg'] or 0,
            'rating_distribution': {
                '5': reviews.filter(rating=5).count(),
                '4': reviews.filter(rating=4).count(),
                '3': reviews.filter(rating=3).count(),
                '2': reviews.filter(rating=2).count(),
                '1': reviews.filter(rating=1).count(),
            },
            'verified_purchases': reviews.filter(is_verified_purchase=True).count(),
        }
        
        return Response(stats)


class MyReviewListView(generics.ListAPIView):
    """API endpoint to list current user's reviews."""
    
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        return Review.objects.filter(user=self.request.user).select_related('product', 'user')


class ReviewCreateView(generics.CreateAPIView):
    """API endpoint to create a review."""
    
    serializer_class = ReviewCreateSerializer
    permission_classes = (IsAuthenticated,)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint to retrieve, update or delete a review."""
    
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        """User can only access their own reviews."""
        return Review.objects.filter(user=self.request.user)


class MarkReviewHelpfulView(APIView):
    """API endpoint to mark a review as helpful or unhelpful."""
    
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, review_id):
        serializer = MarkHelpfulSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        review = get_object_or_404(Review, id=review_id, is_approved=True)
        helpful = serializer.validated_data['helpful']
        
        if helpful:
            # Mark as helpful
            obj, created = ReviewHelpful.objects.get_or_create(
                review=review,
                user=request.user
            )
            message = 'Review marked as helpful' if created else 'Already marked as helpful'
        else:
            # Remove helpful mark
            deleted_count = ReviewHelpful.objects.filter(
                review=review,
                user=request.user
            ).delete()[0]
            message = 'Helpful mark removed' if deleted_count > 0 else 'Was not marked as helpful'
        
        # Get updated helpful count
        review.refresh_from_db()
        
        return Response({
            'message': message,
            'helpful_count': review.helpful_count
        })


class ReportReviewView(generics.CreateAPIView):
    """API endpoint to report a review."""
    
    serializer_class = ReviewReportSerializer
    permission_classes = (IsAuthenticated,)
    
    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)


class ReviewReportListView(generics.ListAPIView):
    """API endpoint to list review reports (admin only)."""
    
    serializer_class = ReviewReportSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        """Only admins can view reports."""
        if not self.request.user.is_staff:
            return ReviewReport.objects.none()
        
        status_filter = self.request.query_params.get('status', 'pending')
        return ReviewReport.objects.filter(status=status_filter).select_related(
            'review', 'reported_by', 'reviewed_by'
        )


class ReviewReportDetailView(generics.RetrieveUpdateAPIView):
    """API endpoint to review and update a report (admin only)."""
    
    serializer_class = ReviewReportSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        """Only admins can access."""
        if not self.request.user.is_staff:
            return ReviewReport.objects.none()
        return ReviewReport.objects.all()


class VendorResponseCreateView(APIView):
    """API endpoint for vendor to respond to a review."""
    
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, review_id):
        review = get_object_or_404(Review, id=review_id, is_approved=True)
        
        serializer = VendorResponseCreateSerializer(
            data=request.data,
            context={'request': request, 'review': review}
        )
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        vendor_response = serializer.save(
            review=review,
            vendor=request.user
        )
        
        return Response(
            VendorResponseCreateSerializer(vendor_response).data,
            status=status.HTTP_201_CREATED
        )


class VendorResponseUpdateView(generics.UpdateAPIView):
    """API endpoint for vendor to update their response."""
    
    serializer_class = VendorResponseCreateSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        """Vendor can only update their own responses."""
        return VendorResponse.objects.filter(vendor=self.request.user)


class ApproveReviewView(APIView):
    """API endpoint to approve/disapprove a review (admin only)."""
    
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, review_id):
        if not request.user.is_staff:
            return Response(
                {'error': 'Only admins can approve reviews.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        review = get_object_or_404(Review, id=review_id)
        approve = request.data.get('approve', True)
        
        review.is_approved = approve
        review.save()
        
        return Response({
            'message': f'Review {"approved" if approve else "disapproved"} successfully.',
            'review': ReviewSerializer(review, context={'request': request}).data
        })