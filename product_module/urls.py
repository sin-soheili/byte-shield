from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

app_name = "products"

router = DefaultRouter()
router.register(r'products', views.ProductViewSet)
router.register(r'categories', views.ProductCategoryViewSet)

urlpatterns = [
    path('', views.ProductView.as_view(), name="products_list"),
    path('<slug:product_id>', views.ProductDetailView.as_view(), name="products_detail"),
    path('cut/<str:category>', views.ProductView.as_view(), name="products_list_category"),
    path('api/', include(router.urls)),
    path('api/products/slug/<slug:slug>/', views.ProductViewSet.as_view({'get': 'get_product_by_slug'}), name='product-by-slug'),
]
