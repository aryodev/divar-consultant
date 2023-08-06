# Generated by Django 4.2.2 on 2023-08-06 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0014_remove_consultant_scope_of_activity_string'),
    ]

    operations = [
        migrations.CreateModel(
            name='SizeClassification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='consultant',
            name='size_classification',
            field=models.ManyToManyField(to='home.sizeclassification'),
        ),
    ]
