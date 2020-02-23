from django.utils.translation import gettext_lazy as _
from django.db.models import Prefetch, Q
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
                'region__region_translations',
                queryset=RegionTranslation.objects.filter(
                    language_code=language
                )
            ),
            Prefetch(
               'zip_codes',
            )
        ]

        q = request.GET.get('q', None)

        # We can get a sequence of queries separated by semi-colons
        # with this order: City, Region (or Country), Country
        # if only one section is passed, that will always be the city,
        # the second section could be either the region or the country, and,
        # if a third section is passed, that will always be the country

        city_query = None
        region_query = None
        country_query = None
        if q:
            queries = list(map(lambda x: x.strip(), q.split(',', 2)))
            # Should always exists if 'q' is passed
            print(len(queries))
            city_query = queries[0]
            if len(queries) >= 2:
                region_query = queries[1]
            if len(queries) >= 3:
                country_query = queries[2]

        city_list = City.objects.prefetch_related(*prefetch).all()

        if city_query:
            city_list = city_list.filter(
                Q(city_translations__name__istartswith=city_query) & Q(city_translations__language_code=language)
                | Q(zip_codes__zip_code=city_query)
                | Q(code=city_query)
            )
        if region_query and not country_query:
            city_list = city_list.filter(
                Q(region__region_translations__name__istartswith=region_query) & Q(region__region_translations__language_code=language)
                | Q(region__code__iexact=region_query)
                | Q(country__country_translations__name__istartswith=region_query) & Q(country__country_translations__language_code=language)
                | Q(country__code__iexact=region_query)
            )
        else:
            if region_query and country_query:
                city_list = city_list.filter(
                    Q(region__region_translations__name__istartswith=region_query) & Q(region__region_translations__language_code=language)
                    | Q(region__code__iexact=region_query),
                    Q(country__country_translations__name__istartswith=country_query) & Q(country__country_translations__language_code=language)
                    | Q(country__code__iexact=country_query)
                )
            if country_query and not region_query:
                city_list = city_list.filter(
                    Q(country__country_translations__name__istartswith=country_query) & Q(country__country_translations__language_code=language)
                    | Q(country__code__iexact=country_query)
                )

        city_list = city_list.distinct()[:limit]
        serializer = CitySerializer(city_list, many=True)
        return Response(serializer.data)

