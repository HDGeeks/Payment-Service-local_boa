from http.client import OK
from django.db import models
from datetime import date

# Create your models here.


class Abstarct(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class Gift_Payment_info(Abstarct):
    PAYMENT_STATUS = (("PENDING", "PENDING"), ("COMPLETED", "COMPLETED"))
    userId = models.CharField(max_length=255)
    payment_amount = models.IntegerField(null=False, blank=False, default=0)
    payment_method = models.CharField(max_length=255, null=False, blank=True)
    outTradeNo = models.CharField(max_length=255, null=False, blank=True)
    msisdn = models.CharField(max_length=255, null=False, blank=True)
    tradeNo = models.CharField(max_length=255, null=False, blank=True)
    transactionNo = models.CharField(max_length=255, null=False, blank=True)
    payment_state = models.CharField(
        max_length=9, choices=PAYMENT_STATUS, default="PENDING"
    )

    class Meta:
        # ordering = []
        verbose_name = "Gift_Payments"

    def __str__(self):
        return f"gift-id = {self.pk} user_id={self.userId}, amount= {self.payment_amount} birr"


class Coin(Abstarct):
    userId = models.CharField(max_length=255, blank=True, null=False, primary_key=True)
    total_coin = models.IntegerField(null=False, blank=False, default=0)

    class Meta:
        verbose_name = "Coin_Amount"

    def __str__(self):
        return f" The user {self.userId} has total coin {self.total_coin}"


class Gift_Info(Abstarct):
    ArtistId = models.CharField(max_length=255, null=False, blank=False)
    gift_amount = models.IntegerField(null=False, blank=False, default=0)
    userId = models.CharField(max_length=255, blank=True, null=False)

    class Meta:
        # ordering = [-1]
        verbose_name = "Gift_Informations"

    def __str__(self):
        return f"{self.userId} gifted to  {self.ArtistId} at {self.created_at}"
