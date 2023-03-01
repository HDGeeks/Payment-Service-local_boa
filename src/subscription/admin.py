from django.contrib import admin
from .models import Subscription, Subscription_Payment_info


@admin.register(Subscription, Subscription_Payment_info)
class Subscription_admin(admin.ModelAdmin):
    pass
