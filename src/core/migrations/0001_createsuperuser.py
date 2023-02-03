import os

from django.contrib.auth.models import User
from django.db import migrations


def createsuperuser(apps, schema_editor):
    music_admin_password = "playground"
    User.objects.create_superuser("admin", password="playground")


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.RunPython(createsuperuser)
    ]
