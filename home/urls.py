from django.urls import path
from . import views
import re

app_name = 'home'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('unlimited-search-start/', views.EnterSearchCommand.as_view(),
         name='unlimited-search-start'),
    path('unlimited-search-stop/', views.EnterStopSearchCommand.as_view(),
         name='unlimited-search-stop'),

    path('unlimited-search/', views.UnlimitedSearchView.as_view(),
         name='unlimited-search'),
]
