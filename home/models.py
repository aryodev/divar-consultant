from django.db import models
from django.urls import reverse


class Estate(models.Model):
    title = models.CharField(max_length=1000, blank=True,
                             null=True, verbose_name='عنوان')
    size = models.PositiveIntegerField(
        blank=True, null=True, verbose_name='متراژ')
    neighbourhood = models.ForeignKey('neighbourhood', verbose_name='محله',
                                      on_delete=models.CASCADE, related_name='estates', blank=True, null=True)
    link = models.URLField(verbose_name='لینک در دیوار',
                           max_length=2000, unique=True)
    consultant = models.ForeignKey(
        'consultant', on_delete=models.CASCADE, related_name='estates', blank=True, null=True, verbose_name='مشاور',)

    def __str__(self):
        return f'{self.title} - {self.size}'

    class Meta:
        verbose_name = 'ملک'
        verbose_name_plural = 'املاک'


class Consultant(models.Model):
    name = models.CharField(max_length=100, verbose_name='نام')
    phone_number = models.CharField(
        max_length=20, verbose_name='شماره موبایل', blank=True, null=True)
    revenue = models.DecimalField(verbose_name='عملکرد',
                                  decimal_places=2, max_digits=5, blank=True, null=True)

    number_of_ads = models.PositiveIntegerField(
        verbose_name='تعداد اگهی ها', blank=True, null=True)

    size_classification = models.ManyToManyField(
        'SizeClassification', verbose_name='دسته بندی متراژ')

    scope_of_activity = models.ManyToManyField(
        'Neighbourhood', verbose_name='محدوده فعالیت')

    profile = models.CharField(verbose_name='پروفایل',
                               max_length=10000, blank=True, null=True)

    link = models.URLField(max_length=3000, verbose_name='لینک در دیوار')
    agent = models.CharField(max_length=100, unique=True)

    updated = models.DateTimeField(
        auto_now_add=True, verbose_name='اخرین بروزرسانی اطلاعات')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'مشاور'
        verbose_name_plural = 'مشاورین املاک'

    def get_estates(self):
        return ' | '.join(i.title for i in self.estates.all())


class Neighbourhood(models.Model):
    title = models.CharField(verbose_name='عنوان',
                             max_length=1000, unique=True)

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'محله'
        verbose_name_plural = 'محله‌ها'


class SizeClassification(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.title
