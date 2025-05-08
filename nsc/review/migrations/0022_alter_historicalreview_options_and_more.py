from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0021_auto_20210323_1518'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='historicalreview',
            options={
                'get_latest_by': ('history_date', 'history_id'),
                'ordering': ('-history_date', '-history_id'),
                'verbose_name': 'historical review',
                'verbose_name_plural': 'historical reviews',
            },
        ),
        migrations.AddField(
            model_name='historicalreview',
            name='review_type_old',
            field=models.JSONField(blank=True, null=True, verbose_name='legacy type of review'),
        ),
        migrations.AddField(
            model_name='review',
            name='review_type_old',
            field=models.JSONField(blank=True, null=True, verbose_name='legacy type of review'),
        ),
        migrations.AlterField(
            model_name='historicalreview',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalreview',
            name='published',
            field=models.BooleanField(null=True),
        ),
        # Comment out the unsafe field change below!
        # migrations.AlterField(
        #     model_name='historicalreview',
        #     name='review_type',
        #     field=models.JSONField(default=list, verbose_name='type of review'),
        # ),
        migrations.AlterField(
            model_name='review',
            name='published',
            field=models.BooleanField(null=True),
        ),
        migrations.AlterField(
            model_name='reviewrecommendation',
            name='recommendation',
            field=models.BooleanField(null=True),
        ),
    ]
