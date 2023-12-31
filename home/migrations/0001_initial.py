# Generated by Django 4.2.4 on 2023-08-08 11:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Agency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=1000, null=True, verbose_name='عنوان')),
                ('link', models.URLField(max_length=2000, unique=True, verbose_name='لینک')),
            ],
            options={
                'verbose_name': 'اژانس املاک',
                'verbose_name_plural': 'آژانس های املاک',
            },
        ),
        migrations.CreateModel(
            name='Consultant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='نام')),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True, verbose_name='شماره موبایل')),
                ('revenue', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='عملکرد')),
                ('number_of_ads', models.PositiveIntegerField(blank=True, null=True, verbose_name='تعداد اگهی ها')),
                ('profile', models.CharField(blank=True, max_length=10000, null=True, verbose_name='پروفایل')),
                ('link', models.URLField(max_length=3000, verbose_name='لینک در دیوار')),
                ('agent', models.CharField(max_length=100, unique=True)),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='اخرین بروزرسانی اطلاعات')),
                ('agencies', models.ManyToManyField(to='home.agency', verbose_name='آزانس املاک')),
            ],
            options={
                'verbose_name': 'مشاور',
                'verbose_name_plural': 'مشاورین املاک',
                'ordering': ('-updated',),
            },
        ),
        migrations.CreateModel(
            name='Neighbourhood',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=1000, unique=True, verbose_name='عنوان')),
            ],
            options={
                'verbose_name': 'محله',
                'verbose_name_plural': 'محله\u200cها',
            },
        ),
        migrations.CreateModel(
            name='Operation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(default=False, null=True, verbose_name='زمان شروع')),
                ('process_time', models.CharField(blank=True, max_length=1000, null=True, verbose_name='زمان پردازش')),
                ('number_of_consultants', models.PositiveIntegerField(blank=True, null=True, verbose_name='تعداد مشاورین')),
                ('number_of_requests', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='تعداد درخواست ها')),
                ('error', models.TextField(blank=True, null=True, verbose_name='خطا')),
                ('is_error', models.BooleanField(blank=True, default=True, null=True, verbose_name='بدون خطا')),
                ('message', models.TextField(blank=True, null=True, verbose_name='پیام')),
            ],
            options={
                'verbose_name': 'عملیات',
                'verbose_name_plural': 'عملیات ها',
                'ordering': ('-start_time',),
            },
        ),
        migrations.CreateModel(
            name='SizeClassification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='دسته بندی متراژ')),
            ],
        ),
        migrations.CreateModel(
            name='Estate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=1000, null=True, verbose_name='عنوان')),
                ('size', models.PositiveIntegerField(blank=True, null=True, verbose_name='متراژ')),
                ('link', models.URLField(max_length=2000, unique=True, verbose_name='لینک در دیوار')),
                ('agency', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='estates', to='home.agency', verbose_name='آژانس املاک')),
                ('consultant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='estates', to='home.consultant', verbose_name='مشاور')),
                ('neighbourhood', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='estates', to='home.neighbourhood', verbose_name='محله')),
            ],
            options={
                'verbose_name': 'آگهی',
                'verbose_name_plural': 'آگهی ها',
            },
        ),
        migrations.AddField(
            model_name='consultant',
            name='scope_of_activity',
            field=models.ManyToManyField(to='home.neighbourhood', verbose_name='محدوده فعالیت'),
        ),
        migrations.AddField(
            model_name='consultant',
            name='size_classification',
            field=models.ManyToManyField(to='home.sizeclassification', verbose_name='دسته بندی متراژ'),
        ),
        migrations.AddField(
            model_name='agency',
            name='consultants',
            field=models.ManyToManyField(to='home.consultant', verbose_name='مشاور'),
        ),
    ]
