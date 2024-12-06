from django.contrib.auth import get_user_model
from django.db import models
from products.models import Product

User = get_user_model()


class Cart(models.Model):
    PENDING = 'pending'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    PAID = 'paid'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
        (PAID, 'Paid'),
    ]

    user = models.ForeignKey(User, related_name='cart', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=PENDING
    )

    def __str__(self):
        return f"Cart {self.id} - User {self.user.username} - Status {self.get_status_display()}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='cart_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"

    @property
    def total_price(self):
        return self.product.price * self.quantity
