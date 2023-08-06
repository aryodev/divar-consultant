# Generated by Django 4.2.2 on 2023-08-03 04:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Consultant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True)),
                ('revenue', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('scope_of_activity', models.CharField(blank=True, max_length=10000, null=True)),
                ('number_of_ads', models.PositiveIntegerField(blank=True, null=True)),
                ('link', models.CharField(max_length=3000)),
                ('agent', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Neighbourhood',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=1000, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Estate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=1000)),
                ('size', models.PositiveIntegerField(blank=True, null=True)),
                ('link', models.CharField(max_length=2000)),
                ('consultant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='estates', to='home.consultant')),
                ('neighbourhood', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='estates', to='home.neighbourhood')),
            ],
        ),
    ]
