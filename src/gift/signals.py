from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Gift_Payment_info ,Coin
from rest_framework.response import Response
from rest_framework import status
from .serializers import Coin_info_serializer

@receiver(post_save, sender=Gift_Payment_info)
def add_to_coin(instance, sender, created, **kwargs):
    if created:
        print("---------------------------------------------------Request finished!")
        print(instance.id)
        print(instance.payment_amount)
        print(instance.userId)

        current_amount = Coin.objects.filter(
            userId=instance.userId).values("total_coin")[0]["total_coin"]
        if not current_amount:
            current_amount=0
        print(current_amount)

        new_amount = current_amount + int(instance.payment_amount)
        print(new_amount)

        Coin.objects.filter(userId=instance.userId).update(
            total_coin=new_amount)
        
        result = Coin.objects.filter(
            userId=instance.userId).values()
        print(result)

        return 