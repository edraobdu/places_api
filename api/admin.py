from django.contrib import admin
from .models import *


admin.site.register(Language)
admin.site.register(LanguageTranslation)
admin.site.register(Country)
admin.site.register(CountryTranslation)
admin.site.register(RegionTranslation)
admin.site.register(Region)
admin.site.register(City)
admin.site.register(CityTranslation)
admin.site.register(ZipCode)
