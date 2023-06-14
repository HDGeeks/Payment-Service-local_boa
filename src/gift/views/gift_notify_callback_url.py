import environ

from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view
from rest_framework.response import Response

from gift.models import Coin, Gift_Payment_info


from utilities.telebirrApi import Telebirr


# Initialise environment variables
env = environ.Env()
environ.Env.read_env()


@api_view(["GET", "POST"])
@csrf_exempt
def notify(request):
    if request.method == "POST" or request.method == "GET":
        if not request.body:
            return Response("The request object (request.body) is empty .")
        else:
            payload = request.body
            # decrypt data
            decrypted_data = Telebirr.decrypt(
                public_key=env("Public_Key"), payload=payload
            )

            # get current amount using outtade
            current = Gift_Payment_info.objects.filter(
                outTradeNo=decrypted_data["outTradeNo"]
            )
            current_user = current.values("userId")[0]["userId"]
            # capture the existing amount
            if current.exists():
                current_amount = current.values("payment_amount")[0]["payment_amount"]

                # perform addition of the current amount with total amount
                new_amount = current_amount + int(decrypted_data["totalAmount"])

                # update the row with new info
                update_data = Gift_Payment_info.objects.filter(
                    outTradeNo=decrypted_data["outTradeNo"]
                ).update(
                    msisdn=decrypted_data["msisdn"],
                    tradeNo=decrypted_data["tradeNo"],
                    transactionNo=decrypted_data["transactionNo"],
                    payment_amount=new_amount,
                    payment_state="completed",
                )

                # fetch the row for display
                updated_data = Gift_Payment_info.objects.filter(
                    outTradeNo=decrypted_data["outTradeNo"]
                ).values()

                # find the  existing coin per user
                current_coin = Coin.objects.filter(userId=current_user).values(
                    "total_coin"
                )[0]["total_coin"]
                # calculate the new coin
                new_coin = current_coin + int(decrypted_data["totalAmount"])
                # update the new amount
                Coin.objects.filter(userId=current_user).update(total_coin=new_coin)

                # return Response({"Decrypted_Data": decrypted_data, "Updated_Data": updated_data})
                return Response({"code": 0, "msg": "success"})
            else:
                return Response("The outtrade number doesn't exist .")
    else:
        return Response(" only methods get and post allowed .")
