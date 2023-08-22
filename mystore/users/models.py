from django.db import models
from django.contrib.auth.models import User
from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserBalanceInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    deposit = models.FloatField()
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.deposit}'


class UserBalance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.FloatField(default=0)

    def add_balance(self, value: float):
        user_ = self.user
        user_.userbalance.balance = F('balance') + value
        user_.save()
        user_.refresh_from_db()
        UserBalanceInfo.objects.create(user=user_, deposit=value)
        return user_.userbalance.balance

    def remove_balance(self, value: float):
        user_ = self.user
        user_.userbalance.balance = F('balance') - value
        user_.save()
        user_.refresh_from_db()
        UserBalanceInfo.objects.create(user=user_, deposit=-value)
        return user_.userbalance.balance

    def __str__(self):
        return f'{self.user.username}'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserBalance.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userbalance.save()
