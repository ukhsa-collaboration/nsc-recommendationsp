# Generated by Django 2.2.20 on 2021-09-17 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0003_auto_20210426_1554"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="sub_claim",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
    ]
