from django.contrib.auth import get_user_model
from django.db import models
from django.conf import settings
from rest_framework.exceptions import ValidationError

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Attribute(models.Model):
    name = models.CharField(max_length=100)
    categories = models.ManyToManyField(Category, related_name='attributes')

    def __str__(self):
        return self.name


class AttributeValue(models.Model):
    attribute = models.ForeignKey(Attribute, related_name='values', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.price}$)"


class Feature(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, related_name='features', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.price}$)"


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_orderable = models.BooleanField(default=True)
    base_weight = models.FloatField(null=True, blank=True)
    user_text = models.CharField(max_length=1000, null=True, blank=True)
    packaging_cost = models.FloatField(default=0)
    max_weight = models.FloatField(null=True, blank=True)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    attributes = models.ManyToManyField(AttributeValue, related_name='products', blank=True)
    features = models.ManyToManyField(Feature, related_name='products', blank=True)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='static/products/product_images/')

    def __str__(self):
        return f"Image for {self.product.name}"


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='favorites', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='favorites', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
