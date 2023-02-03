from django.contrib import admin
from .models import Purcahsed_album, Purcahsed_track, Payment_info


@admin.register(Purcahsed_album, Purcahsed_track, Payment_info)
class PaymentAdmin(admin.ModelAdmin):
    pass
