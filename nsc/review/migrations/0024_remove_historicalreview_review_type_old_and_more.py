# Updated migration to clean up review_type field migration safely
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0023_migrate_review_type_to_json'),
    ]

    operations = [
        # Drop the original review_type fields (ArrayField)
        migrations.RemoveField(
            model_name='historicalreview',
            name='review_type',
        ),
        migrations.RemoveField(
            model_name='review',
            name='review_type',
        ),

        # Rename review_type_old (JSONField) to review_type
        migrations.RenameField(
            model_name='historicalreview',
            old_name='review_type_old',
            new_name='review_type',
        ),
        migrations.RenameField(
            model_name='review',
            old_name='review_type_old',
            new_name='review_type',
        ),
    ]
