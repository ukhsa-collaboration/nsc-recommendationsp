# Generated by Django 2.2.20 on 2021-04-30 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notify", "0004_auto_20210426_1239"),
    ]

    operations = [
        migrations.AlterField(
            model_name="email",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("created", "Created"),
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
