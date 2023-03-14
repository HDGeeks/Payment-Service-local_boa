from utilities.telebirrApi import Telebirr
import environ
from rest_framework.response import Response
# Initialise environment variables
env = environ.Env()
environ.Env.read_env()


def send_to_telebirr(amount, nonce, outtrade, notify_type):

    notify_url = ''
    gift_notify_url = "https://payment-service.calmgrass-743c6f7f.francecentral.azurecontainerapps.io/gift/notify-url"
    sub_notify_url = "https://payment-service.calmgrass-743c6f7f.francecentral.azurecontainerapps.io/subscription/subscribe-notify-url"
    purchase_notify_url = "https://payment-service.calmgrass-743c6f7f.francecentral.azurecontainerapps.io/payment/payment-notify-url"

    if notify_type == "purchase":
        notify_url = purchase_notify_url
    elif notify_type == "gift":
        notify_url = gift_notify_url
    elif notify_type == "subs":
        notify_url = sub_notify_url
    else:
        return Response("No notify url provided for this operation .")

    print(notify_url)
    print(type(notify_type))

    telebirr = Telebirr(
        app_id=env("App_ID"),
        app_key=env("App_Key"),
        public_key=env("Public_Key"),
        notify_url=notify_url,
        receive_name="Zema Multimedia PLC ",
        return_url="https://zemamultimedia.com",
        short_code=env("Short_Code"),
        subject="Media content",
        timeout_express="30",
        total_amount=amount,
        nonce=nonce,
        out_trade_no=outtrade,
    )

    return telebirr.send_request()
