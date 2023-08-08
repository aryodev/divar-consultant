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

    agency = models.ForeignKey(
        'Agency',
        verbose_name='آژانس املاک',
        on_delete=models.SET_NULL, related_name='estates', blank=True, null=True)

    def __str__(self):
        return f'{self.title} - {self.size}'

    class Meta:
        verbose_name = 'آگهی'
        verbose_name_plural = 'آگهی ها'


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

    agencies = models.ManyToManyField('Agency', verbose_name='آزانس املاک')

    link = models.URLField(max_length=3000, verbose_name='لینک در دیوار')
    agent = models.CharField(max_length=100, unique=True)

    updated = models.DateTimeField(
        auto_now=True, verbose_name='اخرین بروزرسانی اطلاعات')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'مشاور'
        verbose_name_plural = 'مشاورین املاک'
        ordering = ('-updated',)

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
    title = models.CharField(max_length=100, verbose_name='دسته بندی متراژ')

    def __str__(self) -> str:
        return f'{self.title}'


class Agency(models.Model):
    title = models.CharField(max_length=1000, blank=True,
                             null=True, verbose_name='عنوان')
    link = models.URLField(max_length=2000, unique=True, verbose_name='لینک')
    consultants = models.ManyToManyField(Consultant, verbose_name='مشاور')

    class Meta:
        verbose_name = 'اژانس املاک'
        verbose_name_plural = 'آژانس های املاک'

    def __str__(self):
        return f"{self.title}"


class Operation(models.Model):
    start_time = models.DateTimeField(
        null=True, default=False, verbose_name='زمان شروع')

    process_time = models.CharField(
        max_length=1000, blank=True, null=True, verbose_name='زمان پردازش')

    number_of_consultants = models.PositiveIntegerField(
        blank=True, null=True, verbose_name='تعداد مشاورین')

    number_of_requests = models.PositiveSmallIntegerField(
        blank=True, null=True, verbose_name='تعداد درخواست ها')

    error = models.TextField(blank=True, null=True, verbose_name='خطا')

    is_error = models.BooleanField(
        blank=True, null=True, default=True, verbose_name='بدون خطا')

    message = models.TextField(blank=True, null=True, verbose_name='پیام')

    class Meta:
        ordering = ('-start_time',)
        verbose_name = 'عملیات'
        verbose_name_plural = 'عملیات ها'

    def __str__(self):
        return f'{self.id}'
