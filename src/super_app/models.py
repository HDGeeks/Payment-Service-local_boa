from datetime import date, datetime, timedelta
from django.utils import timezone
from dateutil.relativedelta import *
from django.db import models


class Abstarct(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


class Superapp_Payment_info(Abstarct):
    PAYMENT_STATUS = (
        ("PENDING", "Pending"),
        ("COMPLETED", "completed"),
        ("PAYING", "Paying"),
        ("FAILURE", "Failure")

    )
    PAYMENT_TITLE = (
        ("SUBSCRIPTION", "Subscription"),
        ("PURCHASE_ALBUM", "Purchase_album"),
        ("PURCHASE_TRACK", "Purchase_track"),
        ("PURCHASE_GIFT", "Purchase_gift")

    )
    PAYMENT_CURRENCY = (
        ("USD", "USD"),
        ("ETB", "ETB"),
    )
    PAYMENT_METHOD = (
        ("telebirr_superApp", "telebirr_superApp"),

    )
    userId = models.CharField(max_length=255, null=False, blank=True)
    payment_amount = models.IntegerField(null=False, blank=False, default=0)
    payment_method = models.CharField(
        max_length=255, choices=PAYMENT_METHOD, default="SUPERAPP")
    payment_title = models.CharField(
        max_length=255, choices=PAYMENT_TITLE, default="SUBSCRIPTION")
    payment_currency = models.CharField(
        max_length=5, choices=PAYMENT_CURRENCY, default="ETB")
   
    payment_state = models.CharField(max_length=9,
                                     choices=PAYMENT_STATUS,
                                     default="PENDING")
    prepay_id = models.CharField(max_length=255, null=False, blank=True)
    merch_order_id = models.CharField(max_length=255, null=False, blank=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'payment_id = {self.pk} user_id={self.userId}, amount= {self.payment_amount} birr'
