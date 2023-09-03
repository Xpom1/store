from mystore.celery import app
from operations.models import Product


@app.task
def load_data(data):
    Product.objects.bulk_create([Product(**i) for i in data])
