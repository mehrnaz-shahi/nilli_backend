from django.urls import path
from .views import ToggleFavoriteView, ProductListAPIView, ProductFilteredByCategoryAPIView, ProductDetailAPIView

urlpatterns = [
    path('favorite/<int:product_id>/', ToggleFavoriteView.as_view(), name='add_favorite'),
    path('all/', ProductListAPIView.as_view(), name='product_list'),
    path('', ProductFilteredByCategoryAPIView.as_view(), name='products_by_category'),
    path('<int:id>/', ProductDetailAPIView.as_view(), name='product_detail'),
]
