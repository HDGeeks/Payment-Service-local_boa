from dateutil.relativedelta import *
from django.db import models
from django.forms import ValidationError
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from django.core.mail import send_mail
from super_app.models import Superapp_Payment_info


class Abstarct(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class SubscriptionFee(Abstarct):
    monthly_subscription_fee = models.IntegerField(null=False, blank=False, default=0)
    yearly_subscription_fee = models.IntegerField(null=False, blank=False, default=0)

    def __str__(self) -> str:
        return f"Monthly fee : {self.monthly_subscription_fee} , Yearly_fee : {self.yearly_subscription_fee}"


class Subscription_Payment_info(Abstarct):
    PAYMENT_STATUS = (("PENDING", "pending"), ("COMPLETED", "completed"))
    userId = models.CharField(max_length=255, null=False, blank=True)
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
        ordering = ["id"]

    def __str__(self):
        return f"payment_id = {self.pk} user_id={self.userId}, amount= {self.payment_amount} birr"


class Subscription(Abstarct):
    SUBSCRIPTION_TYPE = (
        ("DAILY", "daily"),
        ("WEEKLY", "weekly"),
        ("MONTHLY", "monthly"),
        ("YEARLY", "yearly"),
    )
    user_id = models.CharField(max_length=255, blank=False, null=True)
    payment_id = models.ForeignKey(
        Subscription_Payment_info, on_delete=models.PROTECT, null=True
    )
    payment_id_from_superapp = models.ForeignKey(
        Superapp_Payment_info, on_delete=models.PROTECT, null=True
    )

    subscription_date = models.DateTimeField(auto_now=True)
    paid_until = models.DateTimeField(null=False, blank=True)

    is_Subscriebed = models.BooleanField(blank=False, null=False, default=False)

    sub_type = models.CharField(
        max_length=50, choices=SUBSCRIPTION_TYPE, default="MONTHLY"
    )

    def clean(self):
        if self.payment_id is not None and self.payment_id_from_superapp is not None:
            raise ValidationError("Both foreign keys cannot have value.")
        elif self.payment_id is None and self.payment_id_from_superapp is None:
            raise ValidationError("At least one foreign key must have a value.")

    def __str__(self):
        return self.user_id

    def save(self, *args, **kwargs):
        super(Subscription, self).save(*args, **kwargs)

        try:
            url = "https://kinideas-profile-dev-vdzflryflq-ew.a.run.app/subscribedUsers"
            data = {"user_id": self.user_id, "subscription_type": self.sub_type}

            headers = {"Content-type": "application/json", "Accept": "application/json"}

            retry_strategy = Retry(
                total=5,
                backoff_factor=0.5,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "OPTIONS"],
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            http = requests.Session()
            http.mount("https://", adapter)
            http.mount("http://", adapter)

            response = http.post(url, json=data, headers=headers)
            return response

            # if response.status_code == 201:
            #        return response("hurray")

        except BaseException as e:
            send_mail(
                "couldnt send data",
                data,
                "kinideas.tech@gmail.com",
                ["dannyhd88@gmail.com"],
                fail_silently=False,
            )
            with open("exception_track.txt", "a") as f:
                return print(str(e), data, file=f)
