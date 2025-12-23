from django.urls import path
from .views import (
    CategoryListCreateView,
    CategoryDetailView,
    ProductListCreateView,
    ProductDetailView,
    ProductUpdateView,
    ProductDeleteView
)

app_name = 'products'

urlpatterns = [
    # Categories
    path('categories/', CategoryListCreateView.as_view(), name='category_list_create'),
    path('categories/<slug:slug>/', CategoryDetailView.as_view(), name='category_detail'),
    
    # Products
    path('', ProductListCreateView.as_view(), name='product_list_create'),
    path('<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('<slug:slug>/update/', ProductUpdateView.as_view(), name='product_update'),
    path('<slug:slug>/delete/', ProductDeleteView.as_view(), name='product_delete'),
]