from django.utils.translation import gettext_lazy as _
from django.db.models import Prefetch
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.models import *
from api.serializers import CitySerializer



@api_view(['GET'])
def cities_list(request, language):

    if request.method == 'GET':

        # Limiting the list so we don't overload the database
        limit = request.GET.get('limit', 50)
        if limit > 200:
            limit = 200

        if language not in LanguageChoices.values:
            return Response(
                {
                    'error': _('We currently do not support the \'%s\''
                               ' language, or that is not a'
                               ' valid code') % language
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        prefetch = [
            Prefetch(
                'city_translations',
                queryset=CityTranslation.objects.filter(
                    language_code=language
                )
            ),
            Prefetch(
                'country__country_translations',
                queryset=CountryTranslation.objects.filter(
                    language_code=language
                )
            ),
            Prefetch(
               'zip_codes',
            )
        ]

        city_query = request.GET.get('city', '')
        zip_code_query = request.GET.get('zip_code', '')
        country_query = request.GET.get('country', '')

        if city_query:
            city_list = City.objects.prefetch_related(*prefetch).filter(
                city_translations__language_code=language,
                city_translations__name__istartswith=city_query
            )[:limit]
        elif zip_code_query:
            city_list = City.objects.prefetch_related(*prefetch).filter(
                zip_codes__zip_code=zip_code_query
            )[:limit]
        elif country_query:
            city_list = City.objects.prefetch_related(*prefetch).filter(
                country__country_translations__language_code=language,
                country__country_translations__name__istartswith=country_query
            )[:limit]
        else:
            city_list = City.objects.prefetch_related(*prefetch).filter(
                city_translations__language_code=language,
            )[:limit]
        serializer = CitySerializer(city_list, many=True)
        return Response(serializer.data)

