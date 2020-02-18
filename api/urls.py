from django.urls import path, include
from .views import cities_list

urlpatterns = [
    path('cities/<str:language>/', cities_list),
]
