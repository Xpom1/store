from django.contrib import admin

# Register your models here.
from .models import Cart, Product, Product_photo

# admin.site.register(Cart)
admin.site.register(Product)
admin.site.register(Product_photo)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    filter_horizontal = ['product_id']
