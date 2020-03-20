from django.urls import path, include
from . import views

urlpatterns = [
    # Api urls
    path('cities/<str:language>/', views.cities_list, name='cities-list'),

    # Upload
    path('upload-countries/', views.upload_country, name='upload-countries'),
    path('download-countries/<int:empty>/', views.download_countries, name='download-countries'),
    path('upload-regions/', views.upload_regions, name='upload-regions'),
    path('download-regions/<int:empty>/', views.download_regions, name='download-regions'),
]
