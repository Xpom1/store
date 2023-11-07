from django.db.models import Sum, F, Avg
from operations.models import Order
import json


class SalesStatsService:
    def __init__(self):
        self.grouping = {
            'category': 'product__category',
            'users': 'customer',
            'time': 'timestamp__date',
            'cost': 'orderproduct__price'
        }
        self.filtering = {
            'category': 'product__category__in',
            'users': 'customer__in',
            'time': 'timestamp__date__range',
            'cost': 'orderproduct__price__range'
        }

    def get_stats(self, type_, filter_, value):
        if filter_:
            value = json.loads(value)
            filter_key = self.filtering.get(filter_)
            group_key = self.grouping.get(type_)
            a = Order.objects.filter(**{filter_key: value}).values(group_key).annotate(
                total_cost_=Sum(F('orderproduct__price') * F('orderproduct__quantity')),
                count_sale=Sum('orderproduct__quantity'),
                Avg_price=Avg('orderproduct__price')
            )
            b = Order.objects.filter(**{filter_key: value}).values(group_key).annotate(
                Avg_rating=Avg('product__rating_feedback__rating')
            )
        else:
            group_key = self.grouping.get(type_)
            a = Order.objects.values(group_key).annotate(
                total_cost_=Sum(F('orderproduct__price') * F('orderproduct__quantity')),
                count_sale=Sum('orderproduct__quantity'),
                Avg_price=Avg('orderproduct__price')
            )
            b = Order.objects.values(group_key).annotate(
                Avg_rating=Avg('product__rating_feedback__rating')
            )

        for i in range(len(a)):
            a[i]['Avg_rating'] = b[i].get('Avg_rating')

        return a
