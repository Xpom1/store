from operations.models import Product, Rating_Feedback, OrderProduct


class RatingFeedbackService:
    def __init__(self, user):
        self.user = user

    def create_rating_feedback(self, product_id, rating, feedback, parent_id=None):
        product = Product.objects.get(id=product_id)
        if parent_id:
            Rating_Feedback.objects.create(feedback=feedback, user=self.user, parent_id=parent_id)
            return 'success', None
        else:
            if not Rating_Feedback.objects.filter(user=self.user, product_id=product).exists():
                if OrderProduct.objects.filter(order_id__customer=self.user, product_id=product).exists():
                    Rating_Feedback.objects.create(user=self.user, product=product, rating=rating, feedback=feedback)
                    return 'success', None
                return 'not_purchased', None
            return 'rating_exists', None

    def update_rating_feedback(self, rating_feedback_id, feedback, product_id):
        if rating_feedback_id:
            Rating_Feedback.objects.filter(id=rating_feedback_id).update(feedback=feedback)
            return 'success', None
        else:
            rating = Rating_Feedback.objects.filter(user=self.user, product_id=product_id)
            if rating:
                rating.update(rating=rating, feedback=feedback)
                return 'success', None
            return 'rating_not_exist', None

    def delete_rating_feedback(self, rating_feedback_id, product_id):
        if rating_feedback_id:
            Rating_Feedback.objects.filter(id=rating_feedback_id).delete()
            return 'success', None
        else:
            rating = Rating_Feedback.objects.filter(user=self.user, product_id=product_id)
            if rating:
                rating.delete()
                return 'success', None
            return 'rating_not_exist', None
