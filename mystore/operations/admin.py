from django.contrib import admin

# Register your models here.
from .models import Product, ProductPhoto, Сategory, Cart, CartProduct, Rating_Feedback
from mptt.admin import MPTTModelAdmin

admin.site.register(Product)
admin.site.register(ProductPhoto)
admin.site.register(Сategory)
admin.site.register(Cart)
admin.site.register(CartProduct)
admin.site.register(Rating_Feedback, MPTTModelAdmin)

