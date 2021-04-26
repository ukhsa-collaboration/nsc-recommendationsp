# Generated by Django 2.2.20 on 2021-04-26 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0002_user_last_session_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="username",
            field=models.CharField(
                error_messages={"unique": "A user with that username already exists."},
                max_length=150,
                unique=True,
                verbose_name="username",
            ),
        ),
    ]