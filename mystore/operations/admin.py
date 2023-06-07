from django.contrib import admin

# Register your models here.
from .models import Product, ProductPhoto, Сategory, Cart, CartProduct

admin.site.register(Product)
admin.site.register(ProductPhoto)
admin.site.register(Сategory)
admin.site.register(Cart)
admin.site.register(CartProduct)

# @admin.register(Cart)
# class CartAdmin(admin.ModelAdmin):
#     filter_horizontal = ['product']

