from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Gift_Payment_info, Coin
from rest_framework.response import Response
from rest_framework import status
from .serializers import Coin_info_serializer


@receiver(post_save, sender=Gift_Payment_info)
def add_to_coin(instance, sender, created, **kwargs):
    if created:
        check_for_user = current_amount = Coin.objects.filter(userId=instance.userId)
        if check_for_user:
            current_amount = check_for_user.values("total_coin")[0]["total_coin"]
            new_amount = current_amount + int(instance.payment_amount)

            Coin.objects.filter(userId=instance.userId).update(total_coin=new_amount)

        else:
            new_record = Coin(
                userId=instance.userId, total_coin=instance.payment_amount
            )
            new_record.save()

    return True
