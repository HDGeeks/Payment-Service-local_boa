from datetime import date, datetime, timedelta, timezone
from dateutil.relativedelta import *
from dateutil.relativedelta import *


def subs_data(data):
    pay_load={}
    date = datetime.now()
    paid_until=None
    if data["sub_type"] == "MONTHLY":
        paid_until = date + relativedelta(months=+1)
    elif data["sub_type"] == "YEARLY":
        paid_until = date + relativedelta(months=+12)
    elif data["sub_type"] == "WEEKLY":
        paid_until = date + relativedelta(weeks=+1)

    elif data["sub_type"] == "DAILY":
        paid_until = date + relativedelta(days=+1)
    pay_load = {
                "user_id": data["user_id"],
                "payment_id":data["payment_id"],
                "payment_id_from_superapp":data[
                    "payment_id_from_superapp"
                ],
                "sub_type": data['sub_type'],
                "paid_until": paid_until,
                "is_Subscriebed": True,
            }
    return pay_load
   
