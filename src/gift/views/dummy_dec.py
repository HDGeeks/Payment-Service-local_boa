import environ

from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view
from rest_framework.response import Response


from utilities.telebirrApi import Telebirr


# Initialise environment variables
env = environ.Env()
environ.Env.read_env()


@api_view(["GET", "POST"])
@csrf_exempt
def dummy_dec(request):
    # Initialise environment variables
    env = environ.Env()
    environ.Env.read_env()
    if request.method == "POST" or request.method == "GET":
        payload = request.body
        # payload = json.loads(request.data)
        try:
            decrypted_data = Telebirr.decrypt(
                public_key=env("Public_Key"), payload=payload
            )
        except Exception as e:
            return Response(str(e))
        else:
            return Response(
                {
                    "Decrypted_Data": decrypted_data,
                }
            )
