# Generated by Django 4.2.2 on 2023-08-03 04:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='consultant',
            old_name='scope_of_activity',
            new_name='scope_of_activity_in_profile',
        ),
        migrations.AddField(
            model_name='consultant',
            name='scope_of_activity_from_advertising',
            field=models.ManyToManyField(to='home.neighbourhood'),
        ),
    ]