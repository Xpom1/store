from django.contrib import admin

# Register your models here.
from .models import Cart, Product, ProductPhoto

# admin.site.register(Cart)
admin.site.register(Product)
admin.site.register(ProductPhoto)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    filter_horizontal = ['product']
