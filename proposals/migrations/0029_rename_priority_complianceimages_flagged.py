# Generated by Django 4.2 on 2023-06-01 22:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("proposals", "0028_complianceimages_priority"),
    ]

    operations = [
        migrations.RenameField(
            model_name="complianceimages",
            old_name="priority",
            new_name="flagged",
        ),
    ]
