# Generated by Django 2.2.11 on 2021-02-04 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("review", "0007_reviewphecommsnotification"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalreview",
            name="dates_confirmed",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="review",
            name="dates_confirmed",
            field=models.BooleanField(default=False),
        ),
    ]
