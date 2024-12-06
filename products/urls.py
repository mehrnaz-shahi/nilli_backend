from django.urls import path
from .views import AddFavoriteView

urlpatterns = [
    path('favorite/<int:product_id>/', AddFavoriteView.as_view(), name='add_favorite'),
]
