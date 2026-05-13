from datetime import date, timedelta
from django.db import migrations

def set_iron_deficiency_anaemia_post_consultation(apps, schema_editor):
    Policy = apps.get_model("policy", "Policy")

    try:
        policy = Policy.objects.get(slug="iron-deficiency-anaemia-pregnancy")
    except Policy.DoesNotExist:
        print("Iron deficiency anaemia (pregnancy) policy not found, skipping")
        return

    today = date.today()
    in_progress_reviews = policy.reviews.exclude(published=True)

    if not in_progress_reviews.exists():
        print(
            "No in-progress reviews found for Iron deficiency anaemia (pregnancy), skipping"
        )
        return

    for review in in_progress_reviews:
        if (
            review.dates_confirmed
            and review.consultation_end
            and review.consultation_end < today
        ):
            continue

        if not review.consultation_end or review.consultation_end >= today:
            review.consultation_end = today - timedelta(days=30)

        if not review.consultation_start:
            review.consultation_start = review.consultation_end - timedelta(days=90)

        review.dates_confirmed = True
        review.save()


class Migration(migrations.Migration):
    dependencies = [
        ("policy", "0010_rename_anaemia_to_iron_deficiency_anaemia_pregnancy"),
        ("review", "0022_alter_historicalreview_options_and_more"),
    ]

    operations = [
        migrations.RunPython(
            set_iron_deficiency_anaemia_post_consultation,
            migrations.RunPython.noop,
        ),
    ]