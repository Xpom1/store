from mystore.celery import app
from operations.models import Product, ProductPriceInfo


@app.task
def load_data(data):
    per = Product.objects.bulk_create([Product(**i) for i in data])
    product_info = [{'product_id': i.id, 'price': i.price} for i in per]
    ProductPriceInfo.objects.bulk_create([ProductPriceInfo(**i) for i in product_info])
