# Generated by Django 2.2.11 on 2021-02-08 16:11

from django.db import migrations, models
import django_extensions.db.fields
import nsc.notify.models


class Migration(migrations.Migration):

    dependencies = [
        ("notify", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ReceiptUserToken",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, verbose_name="created"
                    ),
                ),
                (
                    "modified",
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, verbose_name="modified"
                    ),
                ),
                (
                    "token",
                    models.CharField(
                        default=nsc.notify.models.generate_token, max_length=50
                    ),
                ),
            ],
            options={
                "ordering": ("-modified", "-created"),
                "get_latest_by": "modified",
                "abstract": False,
            },
        ),
        migrations.AlterField(
            model_name="email",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("sending", "Sending"),
                    ("delivered", "Delivered"),
                    ("permanent-failure", "Permanent Failure"),
                    ("temporary-failure", "Temporary Failure"),
                    ("technical-failure", "Technical Failure"),
                ],
                default="pending",
                max_length=17,
            ),
        ),
    ]
