# Generated by Django 4.0 on 2023-02-28 08:48

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Coin",
            fields=[
                ("created_at", models.DateTimeField(auto_now=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "userId",
                    models.CharField(
                        blank=True, max_length=255, primary_key=True, serialize=False
                    ),
                ),
                ("total_coin", models.IntegerField(default=0)),
            ],
            options={
                "verbose_name": "Coin_Amount",
            },
        ),
        migrations.CreateModel(
            name="Gift_Info",
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
                ("ArtistId", models.CharField(max_length=255)),
                ("gift_amount", models.IntegerField(default=0)),
                ("userId", models.CharField(blank=True, max_length=255)),
            ],
            options={
                "verbose_name": "Gift_Informations",
            },
        ),
        migrations.CreateModel(
            name="Gift_Payment_info",
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
                ("userId", models.CharField(max_length=255)),
                ("payment_amount", models.IntegerField(default=0)),
                ("payment_method", models.CharField(blank=True, max_length=255)),
                ("outTradeNo", models.CharField(blank=True, max_length=255)),
                ("msisdn", models.CharField(blank=True, max_length=255)),
                ("tradeNo", models.CharField(blank=True, max_length=255)),
                ("transactionNo", models.CharField(blank=True, max_length=255)),
                (
                    "payment_state",
                    models.CharField(
                        choices=[("PENDING", "PENDING"), ("COMPLETED", "COMPLETED")],
                        default="PENDING",
                        max_length=9,
                    ),
                ),
            ],
            options={
                "verbose_name": "Gift_Payments",
            },
        ),
    ]
