# Generated by Django 4.2 on 2023-05-28 23:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("proposals", "0025_alter_proposal_proposal_link"),
    ]

    operations = [
        migrations.AddField(
            model_name="proposal",
            name="proposal_id",
            field=models.CharField(blank=True, default="", max_length=500, null=True),
        ),
    ]
