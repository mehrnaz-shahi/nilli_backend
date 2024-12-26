from django.contrib import admin
from .models import Category, Attribute, AttributeValue, Product, Favorite, Feature, ProductImage

admin.site.register(Category)
admin.site.register(Attribute)
admin.site.register(AttributeValue)
admin.site.register(Product)
admin.site.register(Favorite)
admin.site.register(Feature)
admin.site.register(ProductImage)
