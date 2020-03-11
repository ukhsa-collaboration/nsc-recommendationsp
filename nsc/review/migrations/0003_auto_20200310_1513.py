# Generated by Django 2.2.9 on 2020-03-10 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("review", "0002_auto_20200228_0902")]

    operations = [
        migrations.RemoveField(model_name="historicalreview", name="discussion_date"),
        migrations.RemoveField(model_name="review", name="discussion_date"),
        migrations.AddField(
            model_name="historicalreview",
            name="nsc_meeting_date",
            field=models.DateField(
                blank=True, null=True, verbose_name="NSC meeting date"
            ),
        ),
        migrations.AddField(
            model_name="review",
            name="nsc_meeting_date",
            field=models.DateField(
                blank=True, null=True, verbose_name="NSC meeting date"
            ),
        ),
    ]