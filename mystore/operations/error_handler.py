from rest_framework.response import Response


class Handler:

    def success_with_data(self, data):
        return Response({"status": "success", "data": data.values()})

    def success(self):
        return Response({"status": "success"})

    def max_quantity(self, quantity):
        return Response({'error': f'Max quantity of this product {quantity}'})

    def deleted(self):
        return Response({'Deleted': 'Deleted'})

    def indexerror(self):
        return Response({'error': f'Такого товара нет в корзине.'})

    def unrecognized_command(self):
        return Response({'error': 'Unknown command. To change it, '
                                  'you need to use "add" or "reduce" '
                                  'or enter a number of times.'})

    def created(self):
        return Response({'value': 'The product has already been created'})

    def not_enough_balance(self):
        return Response({"status": "error", "message": "Not enough balance"})

    def cart_empty(self):
        return Response({"status": "error", "message": "Cart is empty"})

    def not_purchased_product(self):
        return Response({"status": "error", "message": "Вы не можете оставить отзыв на товар, который еще не заказали"})

    def rating_already_exist(self):
        return Response({"status": "error", "message": "У вас уже есть отзыв на этот товар, вы можете его изменить"})

    def rating_not_exist(self):
        return Response({"status": "error", "message": "Вы не можете менять/удалять рэйтинг, тк еще не поставили его."})

    def feedback_must_be_present(self):
        return Response({"status": "error", "message": "Чтобы поменять комментарий, вы должны указать комментарий"})

    def incorrect_time(self):
        return Response({"status": "error", "message": "Чтобы получить статистику вы должны указать значения времени "
                                                       "для полей start и end"})

    def incorrect_command(self):
        return Response({"status": "error", "message": "Нет такого типа группировки, обратитесь в Swagger"})
