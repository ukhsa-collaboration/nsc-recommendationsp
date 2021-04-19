# Generated by Django 2.2.11 on 2021-02-18 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("policy", "0005_auto_20210217_1657"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalpolicy",
            name="condition_type",
            field=models.CharField(
                choices=[("general", "General Population"), ("targeted", "Targeted")],
                max_length=8,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="policy",
            name="condition_type",
            field=models.CharField(
                choices=[("general", "General Population"), ("targeted", "Targeted")],
                max_length=8,
                null=True,
            ),
        ),
    ]
