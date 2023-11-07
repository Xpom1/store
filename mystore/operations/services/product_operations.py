from operations.models import Product
from eav.models import Attribute, Value
from operations.serializers import ProductRetrieveSerializer
import json


class ProductOperation:
    def create_product(self, data):
        name = data.get('name')
        description = data.get('description')
        price = ''.join(data.get('price').split())
        quantity = data.get('quantity')
        category = data.get('category')
        attributes = json.loads(data.get('attributes'))

        prod, created = Product.objects.get_or_create(
            name=name,
            defaults={
                'description': description,
                'price': price,
                'quantity': quantity
            }
        )

        if created:
            if category:
                prod.category.set(category)
            for key, val in attributes.items():
                Attribute.objects.get_or_create(slug=key, name=key, datatype=Attribute.TYPE_JSON)
                prod.eav.__setattr__(key, val)
            prod.save()
            return ProductRetrieveSerializer(prod).data, created
        return None, created

    def update_attributes(self, product, attributes_data):
        attributes = json.loads(attributes_data)
        Value.objects.filter(entity_id=product.eav_values.pk_val).delete()
        for key, val in attributes.items():
            Attribute.objects.get_or_create(slug=key, name=key, datatype=Attribute.TYPE_JSON)
            product.eav.__setattr__(key, val)
        product.save()
        return ProductRetrieveSerializer(product).data
