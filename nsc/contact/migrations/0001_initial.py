# Generated by Django 2.2.11 on 2021-01-26 12:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields
import simple_history.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("stakeholder", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="HistoricalContact",
            fields=[
                (
                    "id",
                    models.IntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
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
                ("name", models.CharField(max_length=256, verbose_name="name")),
                ("email", models.EmailField(max_length=254, verbose_name="email")),
                (
                    "phone",
                    models.CharField(
                        blank=True, max_length=50, verbose_name="phone number"
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        blank=True,
                        default="",
                        max_length=50,
                        verbose_name="phone number",
                    ),
                ),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField()),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "stakeholder",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="stakeholder.Stakeholder",
                        verbose_name="stakeholder",
                    ),
                ),
            ],
            options={
                "verbose_name": "historical contact",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": "history_date",
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="Contact",
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
                ("name", models.CharField(max_length=256, verbose_name="name")),
                ("email", models.EmailField(max_length=254, verbose_name="email")),
                (
                    "phone",
                    models.CharField(
                        blank=True, max_length=50, verbose_name="phone number"
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        blank=True,
                        default="",
                        max_length=50,
                        verbose_name="phone number",
                    ),
                ),
                (
                    "stakeholder",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="contacts",
                        to="stakeholder.Stakeholder",
                        verbose_name="stakeholder",
                    ),
                ),
            ],
            options={"verbose_name_plural": "contacts", "ordering": ("name", "pk"),},
        ),
    ]
