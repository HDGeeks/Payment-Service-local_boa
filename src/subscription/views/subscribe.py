from datetime import datetime

import environ
from dateutil.relativedelta import *
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from subscription.models import Subscription, Subscription_Payment_info
from subscription.serializers import subscriptionSerializer
from super_app.models import Superapp_Payment_info
from utilities.validate import subs_data

# Initialise environment variables
env = environ.Env()
environ.Env.read_env(DEBUG=(bool, False))


class SubscriptionViewset(ModelViewSet):
    serializer_class = subscriptionSerializer
    queryset = Subscription.objects.all()

    def list(self, request, *args, **kwargs):
        user_id = self.request.query_params.get("user")
        if user_id:
            try:
                # Retrieve the latest subscription for the specified user
                single_user = Subscription.objects.filter(user_id=user_id).latest(
                    "created_at"
                )

                # Check if the subscription is expired
                if (
                    single_user.is_Subscriebed == True
                    and single_user.paid_until < datetime.now()
                ):
                    # Update the subscription and return False
                    Subscription.objects.filter(id=single_user.pk).update(
                        is_Subscriebed=False
                    )
                    # fetch updated user

                    updated_user = Subscription.objects.filter(user_id=user_id).latest(
                        "created_at"
                    )
                    # display the updated user
                    serializer = self.get_serializer(updated_user)
                    return Response(serializer.data)
                elif (
                    single_user.is_Subscriebed == True
                    and single_user.paid_until > datetime.now()
                ):
                    return Response(
                        {
                            "message": f"User with id {user_id} has an active subscription that ends at {single_user.paid_until}.",
                            "user": self.get_serializer(single_user).data,
                        },
                        status=200,
                    )
                elif single_user.is_Subscriebed == False:
                    return Response(
                        {
                            "message": f"User with id {user_id} subscription expired at {single_user.paid_until}.",
                            "user": self.get_serializer(single_user).data,
                        },
                        status=200,
                    )
                else:
                    return Response(single_user)

            except ObjectDoesNotExist:
                # Return an error message if the user is not found
                return Response(
                    {"error": f"User with id {user_id} not found."}, status=404
                )
        else:
            subscriptions = Subscription.objects.all()
            serializer = self.get_serializer(subscriptions, many=True)
            return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        payment_id = request.data["payment_id"]
        payment_id_from_superapp = request.data["payment_id_from_superapp"]

        if payment_id and payment_id_from_superapp:
            return Response(
                "Only one type of payment is supported . Multiple payment provided .",
                status=status.HTTP_400_BAD_REQUEST,
            )
        elif payment_id is None and payment_id_from_superapp is None:
            return Response(
                "Provide one payment Id please .", status=status.HTTP_400_BAD_REQUEST
            )

        if payment_id_from_superapp:
            # check if the payment id already exists in subscription
            verify_payment_id = Subscription.objects.filter(
                payment_id_from_superapp=request.data["payment_id_from_superapp"]
            ).values("payment_id_from_superapp")

            # Verify payment state is complete
            verify_payment_state = Superapp_Payment_info.objects.filter(
                id=request.data["payment_id_from_superapp"]
            ).values("payment_state")[0]["payment_state"]

            # Check if the current requesting user made the payment
            verify_userId = Superapp_Payment_info.objects.filter(
                id=request.data["payment_id_from_superapp"]
            ).values("userId")[0]["userId"]

            # Verify if the payment was made for subscription
            verify_payment_title = Superapp_Payment_info.objects.filter(
                id=request.data["payment_id_from_superapp"]
            ).values("payment_title")[0]["payment_title"]

            if verify_payment_id:
                return Response(
                    {
                        "message": f"This payment id {verify_payment_id} is already used for existing subscription."
                    }
                )
            if verify_userId != request.data["user_id"]:
                return Response(
                    {"message": "This payment provided was not made by this user ."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            elif verify_payment_state.upper() != "COMPLETED":
                return Response(
                    {
                        "message": "The payment status is still pending , cannot be assigned as subscription."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            elif verify_payment_title.upper() != "SUBSCRIPTION":
                return Response(
                    {
                        "message": "The payment reason is not for subscription, cannot be assigned."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # if request.data["sub_type"] == "MONTHLY":
            #     date = datetime.now()
            #     new_paid_until_monthly = date + relativedelta(months=+1)

            #     pay_load = {}
            #     pay_load = {
            #         "user_id": request.data["user_id"],
            #         "payment_id": request.data["payment_id"],
            #         "payment_id_from_superapp": request.data[
            #             "payment_id_from_superapp"
            #         ],
            #         "sub_type": "MONTHLY",
            #         "paid_until": new_paid_until_monthly,
            #         "is_Subscriebed": True,
            #     }
            # else:
            #     # request.data["sub_type"] == "YEARLY"
            #     date = datetime.now()
            #     new_paid_until_yearly = date + relativedelta(months=+12)

            #     pay_load = {}
            #     pay_load = {
            #         "user_id": request.data["user_id"],
            #         "payment_id": request.data["payment_id"],
            #         "payment_id_from_superapp": request.data[
            #             "payment_id_from_superapp"
            #         ],
            #         "sub_type": "YEARLY",
            #         "paid_until": new_paid_until_yearly,
            #         "is_Subscriebed": True,
            #     }
            try:
                subs_data_saved = subs_data(request.data)
            except Exception as e:
                return Response(str(e))

            serializer = subscriptionSerializer(data=subs_data_saved)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            # check if the payment id is already used for subscription ,
            verify_payment_id = Subscription.objects.filter(
                payment_id=request.data["payment_id"]
            ).values("payment_id")

            # make sure payment state is complete in the payment table
            verify_payment_state = Subscription_Payment_info.objects.filter(
                id=request.data["payment_id"]
            ).values("payment_state")[0]["payment_state"]

            # make sure the payment was done by the subscribing user
            verify_userId = Subscription_Payment_info.objects.filter(
                id=request.data["payment_id"]
            ).values("userId")[0]["userId"]

            if verify_payment_id:
                return Response(
                    {
                        "message": f"This payment id {verify_payment_id} is already used for other subscription."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if verify_userId != request.data["user_id"]:
                return Response(
                    {
                        "message": "The user {verify_userId} made the payment , not the current user ."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            elif verify_payment_state.upper() != "COMPLETED":
                return Response(
                    {
                        "message": "The payment status is still pending , cannot be assigned as subscription."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # if request.data["sub_type"] == "MONTHLY":
            #     date = datetime.now()
            #     new_paid_until_monthly = date + relativedelta(months=+1)

            #     pay_load = {}
            #     pay_load = {
            #         "user_id": request.data["user_id"],
            #         "payment_id": request.data["payment_id"],
            #         "payment_id_from_superapp": request.data[
            #             "payment_id_from_superapp"
            #         ],
            #         "sub_type": "MONTHLY",
            #         "paid_until": new_paid_until_monthly,
            #         "is_Subscriebed": True,
            #     }
            # else:
            #     # request.data["sub_type"] == "YEARLY"
            #     date = datetime.now()
            #     new_paid_until_yearly = date + relativedelta(months=+12)

            #     pay_load = {}
            #     pay_load = {
            #         "user_id": request.data["user_id"],
            #         "payment_id": request.data["payment_id"],
            #         "payment_id_from_superapp": request.data[
            #             "payment_id_from_superapp"
            #         ],
            #         "sub_type": "YEARLY",
            #         "paid_until": new_paid_until_yearly,
            #         "is_Subscriebed": True,
            #     }
            try:
                subs_data_saved_normal = subs_data(request.data)
            except Exception as e:
                return Response(str(e))
            serializer = subscriptionSerializer(data=subs_data_saved_normal)

            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
