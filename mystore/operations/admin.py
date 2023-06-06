from django.contrib import admin

# Register your models here.
from .models import Product, ProductPhoto, Сategory, Cart_Product

admin.site.register(Product)
admin.site.register(ProductPhoto)
admin.site.register(Сategory)
admin.site.register(Cart_Product)


# @admin.register(Cart)
# class CartAdmin(admin.ModelAdmin):
#     filter_horizontal = ['product']

