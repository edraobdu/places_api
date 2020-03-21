from rest_framework import serializers
from .models import *


class CountryTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CountryTranslation
        fields = ['language_code', 'name']


class CountrySerializer(serializers.ModelSerializer):
    country_translations = CountryTranslationSerializer(many=True)

    class Meta:
        model = Country
        fields = ['code', 'country_translations', 'flag']


class RegionTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegionTranslation
        fields = ['language_code', 'name']


class RegionSerializer(serializers.ModelSerializer):
    region_translations = RegionTranslationSerializer(many=True)

    class Meta:
        model = Region
        fields = ['code', 'local_code', 'region_translations', 'flag']


class CityTranslationSerializer(serializers.ModelSerializer):

    class Meta:
        model = CityTranslation
        fields = ['language_code', 'name']


class ZipCodeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ZipCode
        fields = 'zip_code'


class CitySerializer(serializers.ModelSerializer):
    country = CountrySerializer()
    region = RegionSerializer()
    city_translations = CityTranslationSerializer(many=True)
    zip_codes = serializers.StringRelatedField(many=True)

    class Meta:
        model = City
        fields = ['id', 'zip_codes', 'code', 'country', 'region', 'city_translations', 'flag']
