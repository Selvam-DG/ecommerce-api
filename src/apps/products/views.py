from rest_framework import generics, filters, status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductListSerializer,
    ProductCreateUpdateSerializer
)
from .permissions import IsAdminOrVendor


class CategoryListCreateView(generics.ListCreateAPIView):
    """API endpoint to list all categories or create a new one."""
    
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    
    def perform_create(self, serializer):
        """Only admins can create categories."""
        if not self.request.user.is_staff:
            return Response(
                {'error': 'Only admins can create categories.'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save()


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint to retrieve, update or delete a category."""
    
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    lookup_field = 'slug'


class ProductListCreateView(generics.ListCreateAPIView):
    """API endpoint to list all products or create a new one."""
    
    queryset = Product.objects.filter(is_active=True).select_related('category', 'created_by')
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_featured']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'name']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.request.method == 'POST':
            return ProductCreateUpdateSerializer
        return ProductListSerializer
    
    def perform_create(self, serializer):
        """Save the product with the current user as creator."""
        serializer.save(created_by=self.request.user)


class ProductDetailView(generics.RetrieveAPIView):
    """API endpoint to retrieve product details."""
    
    queryset = Product.objects.filter(is_active=True).select_related('category', 'created_by')
    serializer_class = ProductSerializer
    permission_classes = (AllowAny,)
    lookup_field = 'slug'


class ProductUpdateView(generics.UpdateAPIView):
    """API endpoint to update a product."""
    
    queryset = Product.objects.all()
    serializer_class = ProductCreateUpdateSerializer
    permission_classes = (IsAuthenticated, IsAdminOrVendor)
    lookup_field = 'slug'
    
    def get_queryset(self):
        """Filter products based on user role."""
        user = self.request.user
        if user.is_staff:
            return Product.objects.all()
        return Product.objects.filter(created_by=user)


class ProductDeleteView(generics.DestroyAPIView):
    """API endpoint to delete a product."""
    
    queryset = Product.objects.all()
    permission_classes = (IsAuthenticated, IsAdminOrVendor)
    lookup_field = 'slug'
    
    def get_queryset(self):
        """Filter products based on user role."""
        user = self.request.user
        if user.is_staff:
            return Product.objects.all()
        return Product.objects.filter(created_by=user)