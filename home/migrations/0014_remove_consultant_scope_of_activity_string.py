# Generated by Django 4.2.2 on 2023-08-06 01:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0013_alter_consultant_options_alter_estate_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='consultant',
            name='scope_of_activity_string',
        ),
    ]
