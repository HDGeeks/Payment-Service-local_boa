from urllib import response
import requests
import json
from http.client import OK
from django.db import models
from datetime import date
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from django.core.mail import send_mail


# Create your models here.


class Abstarct(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Payment_info(Abstarct):
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


class Purcahsed_track(Abstarct):
    userId = models.CharField(max_length=255, null=False, blank=False)
    trackId = models.CharField(max_length=255, null=False, blank=False)
    isPurcahsed = models.BooleanField(blank=False, null=False, default=False)
    track_price_amount = models.IntegerField(null=False, blank=False, default=0)
    payment_id = models.ForeignKey(Payment_info, on_delete=models.PROTECT)

    class Meta:
        ordering = ["id"]

    def check_userId(
        self,
        userId,
        payment,
    ):
        pass

    def __str__(self):
        return f"{self.userId} {self.isPurcahsed} {self.created_at}"

    def save(self, *args, **kwargs):
        super(Purcahsed_track, self).save(*args, **kwargs)
        try:
            url = "http://music-service.calmgrass-743c6f7f.francecentral.azurecontainerapps.io/webApp/purchasedtrack"
            data = {
                "track_id": self.trackId,
                "user_FUI": self.userId,
            }
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
            #     with open("success_track.txt", "a") as f:
            #         return print(response, file=f)

            # elif response.status_code is not 201:
            #     with open("failure_track.txt", "a") as f:
            #         return print(response, data, file=f)

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


class Purcahsed_album(Abstarct):
    userId = models.CharField(max_length=255, null=False, blank=False)
    albumId = models.CharField(max_length=255, null=False, blank=False)
    isPurcahsed = models.BooleanField(blank=False, null=False, default=False)
    album_price_amount = models.IntegerField(null=False, blank=False, default=0)
    payment_id = models.ForeignKey(Payment_info, on_delete=models.PROTECT)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.userId} {self.isPurcahsed} {self.created_at}"

    def save(self, *args, **kwargs):
        super(Purcahsed_album, self).save(*args, **kwargs)
        try:
            url = "http://music-service.calmgrass-743c6f7f.francecentral.azurecontainerapps.io/webApp/purchasedalbum"
            data = {
                "album_id": self.albumId,
                "user_FUI": self.userId,
            }
            headers = {"Content-type": "application/json", "Accept": "application/json"}

            retry_strategy = Retry(
                total=10,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "OPTIONS"],
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            http = requests.Session()
            http.mount("https://", adapter)
            http.mount("http://", adapter)

            response = http.post(url, json=data, headers=headers)

            # if response.status_code == 201:
            #     with open("success_album.txt", "a") as f:
            #         return print(response, file=f)

            # elif response.status_code is not 201:
            #     with open("failure_album.txt", "a") as f:
            #         return print(response, file=f)
            return response

        except BaseException as e:
            send_mail(
                "couldnt send data",
                data,
                "kinideas.tech@gmail.com",
                ["dannyhd88@gmail.com"],
                fail_silently=False,
            )
            with open("exception_album.txt", "a") as f:
                return print(str(e), file=f)
