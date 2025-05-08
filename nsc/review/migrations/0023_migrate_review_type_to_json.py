from django.db import migrations


def copy_review_type(apps, schema_editor):
    Review = apps.get_model("review", "Review")
    for review in Review.objects.all():
        review.review_type_old = review.review_type
        review.save(update_fields=["review_type_old"])


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0022_alter_historicalreview_options_and_more'),
    ]

    operations = [
        migrations.RunPython(copy_review_type, reverse_code=migrations.RunPython.noop),
    ]
