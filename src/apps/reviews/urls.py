from django.urls import path
from .views import (
    ProductReviewListView,
    ProductReviewStatsView,
    MyReviewListView,
    ReviewCreateView,
    ReviewDetailView,
    MarkReviewHelpfulView,
    ReportReviewView,
    ReviewReportListView,
    ReviewReportDetailView,
    VendorResponseCreateView,
    VendorResponseUpdateView,
    ApproveReviewView,
)

app_name = 'reviews'

urlpatterns = [
    # Product Reviews
    path('products/<int:product_id>/reviews/', ProductReviewListView.as_view(), name='product_reviews'),
    path('products/<int:product_id>/stats/', ProductReviewStatsView.as_view(), name='product_review_stats'),
    
    # User Reviews
    path('my-reviews/', MyReviewListView.as_view(), name='my_reviews'),
    path('create/', ReviewCreateView.as_view(), name='review_create'),
    path('<int:pk>/', ReviewDetailView.as_view(), name='review_detail'),
    
    # Helpful
    path('<int:review_id>/helpful/', MarkReviewHelpfulView.as_view(), name='mark_helpful'),
    
    # Reports
    path('report/', ReportReviewView.as_view(), name='report_review'),
    path('reports/', ReviewReportListView.as_view(), name='review_reports'),
    path('reports/<int:pk>/', ReviewReportDetailView.as_view(), name='review_report_detail'),
    
    # Vendor Responses
    path('<int:review_id>/respond/', VendorResponseCreateView.as_view(), name='vendor_respond'),
    path('responses/<int:pk>/update/', VendorResponseUpdateView.as_view(), name='vendor_response_update'),
    
    # Admin
    path('<int:review_id>/approve/', ApproveReviewView.as_view(), name='approve_review'),
]