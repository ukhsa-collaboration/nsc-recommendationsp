# Generated by Django 2.2.19 on 2021-04-16 09:20

import django.core.validators
from django.db import migrations, models
import nsc.document.models


class Migration(migrations.Migration):

    dependencies = [
        ("document", "0006_merge_20210212_1902"),
    ]

    operations = [
        migrations.AlterField(
            model_name="document",
            name="upload",
            field=models.FileField(
                max_length=256,
                upload_to=nsc.document.models.document_path,
                validators=[
                    django.core.validators.FileExtensionValidator(
                        allowed_extensions=["pdf"]
                    )
                ],
                verbose_name="upload",
            ),
        ),
        migrations.AlterField(
            model_name="historicaldocument",
            name="upload",
            field=models.TextField(
                max_length=256,
                validators=[
                    django.core.validators.FileExtensionValidator(
                        allowed_extensions=["pdf"]
                    )
                ],
                verbose_name="upload",
            ),
        ),
    ]
