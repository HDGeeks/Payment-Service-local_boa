from datetime import date, datetime, timedelta

import environ
from dateutil.relativedelta import *
from rest_framework.decorators import api_view
from rest_framework.response import Response

from subscription.models import Subscription

# Initialise environment variables
env = environ.Env()
environ.Env.read_env(DEBUG=(bool, False))


@api_view(["GET"])
def subscribers_count(request):
    subsecribed_users_count = Subscription.objects.all().count()
    monthly_subsecribed_users_count = Subscription.objects.filter(
        sub_type="MONTHLY"
    ).count()
    yearly_subsecribed_users_count = Subscription.objects.filter(
        sub_type="YEARLY"
    ).count()

    # Today
    today = date.today()
    # This year subscribed users
    this_year_subscribed_users = Subscription.objects.filter(
        created_at__year=today.year
    ).count()
    # This month subscribed users
    this_month_subscribed_users = Subscription.objects.filter(
        created_at__month=today.month
    ).count()
    # Past week
    one_week_ago = datetime.today() - timedelta(days=7)

    this_week_subscribed_users = Subscription.objects.filter(
        created_at__gte=one_week_ago
    ).count()

    return Response(
        {
            "Total_subscribed_users_count": subsecribed_users_count,
            "Monthly_subscribed_users_count": monthly_subsecribed_users_count,
            "Yearly_subscribed_users_count": yearly_subsecribed_users_count,
            "This_year_subscribed_users": this_year_subscribed_users,
            "This_month_subscribed_users": this_month_subscribed_users,
            "This_week_subscribed_users": this_week_subscribed_users,
        }
    )
