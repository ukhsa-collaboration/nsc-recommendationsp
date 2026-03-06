from django.db import migrations


def rename_anaemia_to_iron_deficiency_anaemia_pregnancy(apps, schema_editor):
    Policy = apps.get_model("policy", "Policy")
    try:
        policy = Policy.objects.get(slug="anaemia")
        policy.name = "Iron deficiency anaemia (pregnancy)"
        policy.slug = "iron-deficiency-anaemia-pregnancy"
        policy.save()
    except Policy.DoesNotExist:
        print("Anaemia policy not found, skipping migration")


class Migration(migrations.Migration):

    dependencies = [
        ("policy", "0009_alter_historicalpolicy_options_and_more"),
    ]

    operations = [
        migrations.RunPython(rename_anaemia_to_iron_deficiency_anaemia_pregnancy),
    ]
