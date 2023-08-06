from typing import Any, List, Optional, Tuple
from django.contrib import admin
from django.db.models.query import QuerySet
from .models import Estate, Consultant, Neighbourhood, SizeClassification
from django.contrib.auth.models import Group, User
from django.contrib.admin import SimpleListFilter
from django.db.models import Q
from import_export.admin import ExportActionMixin
from .resources import ConsultantResource


@admin.register(SizeClassification)
class SizeClassificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')


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
        try:
            maximum = model_admin.model.objects.order_by('-size').first().size
        except AttributeError:
            return None

        res = []
        for i in range(maximum // 100 + 1):
            res.append((i, f'{i}00 - {i+1}00'))

        return res

    def queryset(self, request: Any, queryset: QuerySet[Any]) -> QuerySet[Any] | None:
        value = int(self.value()) if self.value() else None
        if value:
            return queryset.filter(
                Q(size__gte=value*100),
                Q(size__lte=(value + 1) * 100),
            )
        return queryset


admin.site.unregister(Group)
admin.site.unregister(User)


class EstateInline(admin.StackedInline):
    model = Estate
    readonly_fields = ('title', 'size', 'link', 'neighbourhood', 'consultant')
    show_change_link = True


@admin.register(Consultant)
class ConsultantAdmin(ExportActionMixin, admin.ModelAdmin):
    resource_classes = [ConsultantResource, ]

    search_fields = ('name', )
    exclude = ('agent',)

    inlines = (EstateInline,)
    list_display = ('name', 'phone_number', 'revenue', 'scop_of_activitie',
                    'number_of_ads', 'profile'
                    )
    list_filter = (RevenueFilter, 'scope_of_activity')
    readonly_fields = ('updated',)
    filter_horizontal = ('scope_of_activity', 'size_classification')

    def scop_of_activitie(self, obj):
        activities = obj.scope_of_activity.all()
        activities_title = [activity.title for activity in activities]
        return f'{", ".join(activities_title)}'


@admin.register(Estate)
class EstateAdmin(admin.ModelAdmin):
    search_fields = ('title', )
    list_display = ('consultant', 'title', 'size')
    list_filter = (SizeFilter, 'consultant')


@admin.register(Neighbourhood)
class NeighbourhoodAdmin(admin.ModelAdmin):
    search_fields = ('title', )
    list_display = ('title',)
    inlines = (EstateInline,)
