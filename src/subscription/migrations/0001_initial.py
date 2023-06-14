# Generated by Django 4.0 on 2023-04-06 11:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("super_app", "__first__"),
    ]

    operations = [
        migrations.CreateModel(
            name="Subscription_Payment_info",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("userId", models.CharField(blank=True, max_length=255)),
                ("payment_amount", models.IntegerField(default=0)),
                ("payment_method", models.CharField(blank=True, max_length=255)),
                ("outTradeNo", models.CharField(blank=True, max_length=255)),
                ("msisdn", models.CharField(blank=True, max_length=255)),
                ("tradeNo", models.CharField(blank=True, max_length=255)),
                ("transactionNo", models.CharField(blank=True, max_length=255)),
                (
                    "payment_state",
                    models.CharField(
                        choices=[("PENDING", "pending"), ("COMPLETED", "completed")],
                        default="PENDING",
                        max_length=9,
                    ),
                ),
            ],
            options={
                "ordering": ["id"],
            },
        ),
        migrations.CreateModel(
            name="SubscriptionFee",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("monthly_subscription_fee", models.IntegerField(default=0)),
                ("yearly_subscription_fee", models.IntegerField(default=0)),
            ],
            options={
                "ordering": ["-created_at"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Subscription",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user_id", models.CharField(max_length=255, null=True)),
                ("subscription_date", models.DateTimeField(auto_now=True)),
                ("paid_until", models.DateTimeField(blank=True)),
                ("is_Subscriebed", models.BooleanField(default=False)),
                (
                    "sub_type",
                    models.CharField(
                        choices=[("MONTHLY", "monthly"), ("YEARLY", "yearly")],
                        default="MONTHLY",
                        max_length=50,
                    ),
                ),
                (
                    "payment_id",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="subscription.subscription_payment_info",
                    ),
                ),
                (
                    "payment_id_from_superapp",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="super_app.superapp_payment_info",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "abstract": False,
            },
        ),
    ]
