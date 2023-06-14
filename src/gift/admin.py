from django.contrib import admin
from .models import Gift_Payment_info, Gift_Info


@admin.register(Gift_Payment_info, Gift_Info)
class PaymentAdmin(admin.ModelAdmin):
    pass
