from typing import Any, List, Optional, Tuple
from django.contrib import admin
from django.db.models.query import QuerySet
from .models import Estate, Consultant, Neighbourhood, SizeClassification, Agency, Operation
from django.contrib.auth.models import Group, User
from django.contrib.admin import SimpleListFilter, AdminSite
from django.db.models import Q
from import_export.admin import ExportActionMixin
from .resources import ConsultantResource


admin.site.unregister(Group)
admin.site.unregister(User)

admin.site.index_title = 'اطلاعات استخراج شده'
admin.site.site_header = 'اطلاعات مشاورین املاک دیوار'
admin.site.site_title = 'پنل مدیر'


def get_app_list(self, request, app_label=None):
    """
    Return a sorted list of all the installed apps that have been
    registered in this site.
    """
    app_dict = self._build_app_dict(request, app_label)

    # Sort the apps alphabetically.
    app_list = sorted(app_dict.values(), key=lambda x: x["name"].lower())

    # Sort the models alphabetically within each app.
    for app in app_list:
        app["models"].sort(key=lambda x: x["name"])

    try:
        models = app_list[0]['models']
        new_models_list = [models[4], models[0],
                           models[3], models[1], models[2]]
        if len(models) > 5:
            new_models_list.extend(models[5:])
        app_list[0]['models'] = new_models_list
    except:
        pass

    return app_list


admin.AdminSite.get_app_list = get_app_list


@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_time', 'process_time', 'is_error',
                    'number_of_consultants', 'number_of_requests', )

    readonly_fields = ('start_time', 'process_time', 'number_of_requests',
                       'number_of_consultants', 'is_error', 'error', 'message')


# @admin.register(SizeClassification)
# class SizeClassificationAdmin(admin.ModelAdmin):
#     list_display = ('id', 'title')


class ConsultantInline(admin.StackedInline):
    model = Agency.consultants.through
    extra = 0
    verbose_name_plural = 'مشاورین'
    verbose_name = 'مشاور'
    # fields = ('consultant_name', )
    # readonly_fields = ('consultant_name', )

    # def consultant_name(self, obj):
    #     return f'{obj.consultant.name}'


class RevenueFilter(SimpleListFilter):
    title = 'عملکرد'
    parameter_name = 'revenue'

    def lookups(self, request: Any, model_admin: Any) -> List[Tuple[Any, str]]:
        objects = model_admin.model.objects.all()
        return [(1, '0 - 1'), (2, '1 - 2'), (3, '2 - 3'), (4, '3 - 4'), (5, '4 - 5')]

    def queryset(self, request: Any, queryset: QuerySet[Any]) -> QuerySet[Any] | None:
        value = int(self.value()) if self.value() else None
        if value:
            return queryset.filter(Q(revenue__lte=value), Q(revenue__gte=value-1))

        return queryset


class SizeFilter(SimpleListFilter):
    title = 'متراژ'
    parameter_name = 'size'

    def lookups(self, request: Any, model_admin: Any) -> List[Tuple[Any, str]]:
        return [('0', '0 - 150'), ('1', '150 - 250'), ('2', '250 - 500'), ('3', 'بزرگتر از 500')]

    def queryset(self, request: Any, queryset: QuerySet[Any]) -> QuerySet[Any] | None:
        value = int(self.value()) if self.value() else None
        if value:
            if value == 0:
                return queryset.filter(
                    Q(size__gte=0),
                    Q(size__lte=150),
                )
            elif value == 1:
                return queryset.filter(
                    Q(size__gte=150),
                    Q(size__lte=250),
                )
            elif value == 2:
                return queryset.filter(
                    Q(size__gte=250),
                    Q(size__lte=500),
                )
            elif value == 3:
                return queryset.filter(
                    Q(size__gte=500),
                )

        return queryset


class ConsultantSizeFilter(SimpleListFilter):
    title = 'متراژ'
    parameter_name = 'size'

    def lookups(self, request: Any, model_admin: Any) -> List[Tuple[Any, str]]:
        return [('0', '0 - 150'), ('1', '150 - 250'), ('2', '250 - 500'), ('3', 'بزرگتر از 500')]

    def queryset(self, request: Any, queryset: QuerySet[Any]) -> QuerySet[Any] | None:
        value = int(self.value()) if self.value() else None
        if value:
            if value == 0:
                return queryset.filter(
                    size_classification__id=1
                )
            elif value == 1:
                return queryset.filter(
                    size_classification__id=2
                )
            elif value == 2:
                return queryset.filter(
                    size_classification__id=3
                )
            elif value == 3:
                return queryset.filter(
                    size_classification__id__gt=3
                )

        return queryset


class EstateInline(admin.StackedInline):
    model = Estate
    readonly_fields = ('title', 'size', 'link', 'neighbourhood', 'consultant')
    show_change_link = True
    extra = 0


@admin.register(Consultant)
class ConsultantAdmin(ExportActionMixin, admin.ModelAdmin):
    resource_classes = [ConsultantResource, ]

    search_fields = ('name', 'scope_of_activity__title', 'agency__title')
    exclude = ('agent',)

    inlines = (EstateInline,)
    list_display = ('name', 'phone_number', 'revenue', 'scop_of_activities',
                    'number_of_ads', 'profile', 'get_size_classification', 'get_agencies'
                    )
    list_filter = (ConsultantSizeFilter,
                   RevenueFilter, 'agencies', 'scope_of_activity',)
    readonly_fields = ('updated', )
    filter_horizontal = ('scope_of_activity',
                         'size_classification', 'agencies')

    def scop_of_activities(self, obj):
        activities = obj.scope_of_activity.all()
        activities_title = [activity.title for activity in activities]
        return f'{" | ".join(activities_title)}'

    def get_size_classification(self, obj):
        return f'{" | ".join([j.title for j in obj.size_classification.all()])}'

    def get_agencies(self, obj):
        objects = obj.agencies.all()

        a = f'{" | ".join( [ j.title for j in objects ] )}' if objects else None
        return a

    get_agencies.short_description = 'آژانس املاک'
    get_size_classification.short_description = 'دسته بندی متراژ'
    scop_of_activities.short_description = 'محدوده فعالیت'


@admin.register(Estate)
class EstateAdmin(admin.ModelAdmin):
    search_fields = ('title', 'consultant__name', 'agency')
    list_display = ('consultant', 'title', 'size')
    list_filter = (SizeFilter, 'consultant')


@admin.register(Neighbourhood)
class NeighbourhoodAdmin(admin.ModelAdmin):
    search_fields = ('title', )
    list_display = ('title',)
    inlines = (EstateInline,)


@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    inlines = (ConsultantInline, EstateInline)
    list_display = ('title', 'link')
    search_fields = ('title',)
    exclude = ('consultants',)
    filter_horizontal = ('consultants',)
