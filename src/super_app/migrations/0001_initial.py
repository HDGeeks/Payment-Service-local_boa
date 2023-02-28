# Generated by Django 4.0 on 2023-02-28 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Superapp_Payment_info',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('userId', models.CharField(blank=True, max_length=255)),
                ('payment_amount', models.IntegerField(default=0)),
                ('payment_method', models.CharField(choices=[('telebirr_superApp', 'telebirr_superApp')], default='SUPERAPP', max_length=255)),
                ('payment_title', models.CharField(choices=[('SUBSCRIPTION', 'Subscription'), ('PURCHASE_ALBUM', 'Purchase_album'), ('PURCHASE_TRACK', 'Purchase_track'), ('PURCHASE_GIFT', 'Purchase_gift')], default='SUBSCRIPTION', max_length=255)),
                ('payment_currency', models.CharField(choices=[('USD', 'USD'), ('ETB', 'ETB')], default='ETB', max_length=5)),
                ('payment_state', models.CharField(choices=[('PENDING', 'Pending'), ('COMPLETED', 'completed'), ('PAYING', 'Paying'), ('FAILURE', 'Failure')], default='PENDING', max_length=9)),
                ('prepay_id', models.CharField(blank=True, max_length=255)),
                ('merch_order_id', models.CharField(blank=True, max_length=255)),
            ],
            options={
                'ordering': ['id'],
            },
        ),
    ]
