# Generated by Django 2.2.11 on 2021-02-15 14:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("policy", "0003_merge_20210212_1902"),
    ]

    operations = [
        migrations.RemoveField(model_name="historicalpolicy", name="last_review",),
        migrations.RemoveField(model_name="policy", name="last_review",),
    ]