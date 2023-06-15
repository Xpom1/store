from django.db import connection


class SimpleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        print(f'Execution time: {sum([float(i.get("time")) for i in connection.queries])}'
              f'\nNumber of queries: {len(connection.queries)}')
        return response
