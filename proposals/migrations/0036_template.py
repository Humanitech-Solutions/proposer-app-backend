# Generated by Django 4.2 on 2024-01-23 16:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("proposals", "0035_remove_proposal_country_alter_proposal_assigned"),
    ]

    operations = [
        migrations.CreateModel(
            name="Template",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("checklist", models.JSONField(default={})),
            ],
        ),
    ]
