# Generated by Django 4.2.2 on 2023-08-03 05:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_rename_scope_of_activity_in_profile_consultant_scope_of_activity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consultant',
            name='agent',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='consultant',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='estate',
            name='link',
            field=models.CharField(max_length=2000, unique=True),
        ),
    ]
