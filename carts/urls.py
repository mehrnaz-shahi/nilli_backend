from django.urls import path
from .views import AddToCartView, RemoveFromCartView, UpdateCartItemQuantityView, ViewCartView, UpdateCartStatusView

urlpatterns = [
    path('', ViewCartView.as_view(), name='view_cart'),
    path('add/<int:product_id>/', AddToCartView.as_view(), name='add_to_cart'),
    path('remove/<int:product_id>/', RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('update/<int:product_id>/', UpdateCartItemQuantityView.as_view(), name='update_cart_item_quantity'),
    path('status/<int:cart_id>/', UpdateCartStatusView.as_view(), name='update_cart_status'),
]
