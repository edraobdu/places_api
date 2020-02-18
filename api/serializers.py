from rest_framework import serializers
from .models import *


class CountryTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CountryTranslation
        fields = '__all__'


class CountrySerializer(serializers.ModelSerializer):
    country_translations = CountryTranslationSerializer(many=True)

    class Meta:
        model = Country
        fields = ['iso_code', 'country_translations']


class CityTranslationSerializer(serializers.ModelSerializer):

    class Meta:
        model = CityTranslation
        fields = '__all__'


class ZipCodeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ZipCode
        fields = 'zip_code'


class CitySerializer(serializers.ModelSerializer):
    country = CountrySerializer()
    city_translations = CityTranslationSerializer(many=True)
    zip_codes = serializers.StringRelatedField(many=True)

    class Meta:
        model = City
        fields = ['zip_codes', 'iso_code', 'country', 'city_translations']
