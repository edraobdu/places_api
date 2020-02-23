from django.urls import path, include
from . import views

urlpatterns = [
    path('cities/<str:language>/', views.cities_list, name='cities-list'),
    path('upload-countries/', views.upload_country, name='upload-countries'),
    path('download-countries/<int:empty>/', views.download_countries, name='download-countries')
]
