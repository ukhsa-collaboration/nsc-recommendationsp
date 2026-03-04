from django.db import migrations


def rename_anaemia_policy(apps, schema_editor):
    Policy = apps.get_model("policy", "Policy")
    Policy.objects.filter(slug="anaemia").update(
        name="Iron deficiency anaemia (pregnancy)",
        slug="iron-deficiency-anaemia-pregnancy",
    )


def reverse_rename_anaemia_policy(apps, schema_editor):
    Policy = apps.get_model("policy", "Policy")
    Policy.objects.filter(slug="iron-deficiency-anaemia-pregnancy").update(
        name="Anaemia",
        slug="anaemia",
    )


class Migration(migrations.Migration):

    dependencies = [
        ("policy", "0007_alter_historicalpolicy_recommendation_and_more"),
    ]

    operations = [
        migrations.RunPython(
            rename_anaemia_policy,
            reverse_code=reverse_rename_anaemia_policy,
        ),
    ]
