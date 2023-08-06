from import_export.resources import ModelResource
from .models import Estate, Neighbourhood, Consultant, SizeClassification
from import_export.fields import Field, widgets


class ConsultantResource(ModelResource):
    name = Field('name', 'نام')
    phone_number = Field('phone_number', 'شماره موبایل')
    revenue = Field('revenue', 'عملکرد')
    number_of_ads = Field('number_of_ads', 'تعداد اگهی ها')
    scope_of_activity = Field(
        column_name='محدوده فعالیت',
        attribute='scope_of_activity',
        widget=widgets.ManyToManyWidget(
            Neighbourhood, field='title', separator=' | ')
    )
    size_classification = Field(
        column_name='دسته بندی متراژ',
        attribute='size_classification',
        widget=widgets.ManyToManyWidget(
            SizeClassification, field='title', separator=' | ')
    )
    estates = Field(
        column_name='املاک',
        attribute='get_estates')

    profile = Field('profile', 'پروفایل')
    link = Field('link', 'لینک در دیوار')

    class Meta:
        model = Consultant
        exclude = ('id', 'agent', 'updated')
