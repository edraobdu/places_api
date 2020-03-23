import django_excel

from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models import Prefetch, Q
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views.decorators.cache import cache_page
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from api.models import *
from api.serializers import CitySerializer
from api.forms import UploadFile
from api.helpers import (
    handle_uploaded_countries, handle_uploaded_regions, handle_uploaded_cities
)


CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


@cache_page(CACHE_TTL)
@api_view(['GET'])
def api_cities_list(request, language):
    """
    This view will show a list fo cities with all its related
    information, like region and country it belongs to, with their respective
    translations, the zip_codes if there is any, currency code and flag of
    the country.
    """
    if request.method == 'GET':

        q = request.GET.get('q', None)
        # We ensure 2 characters at least for a searching query
        if q and len(q) <= 2:
            q = None
        extra_lang = request.GET.get('extra_lang', language)

        # Limiting the list so we don't overload the database
        limit = request.GET.get('limit', 20)
        if limit > 50:
            limit = 50

        if language not in LanguageChoices.values:
            return Response(
                {
                    'error': _('We currently do not support the \'%s\''
                               ' language, or that is not a'
                               ' valid code') % language
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if extra_lang or extra_lang == language or extra_lang not in LanguageChoices.values:
            extra_lang = None

        # Query sets to prefetch the data, we don't have to apply distinct in
        # here because we already checked whether extra_lang was different
        # than language or not
        cities_translations_queryset = CityTranslation.objects.filter(language_code=language)
        regions_translations_queryset = RegionTranslation.objects.filter(language_code=language)
        countries_translations_queryset = CountryTranslation.objects.filter(language_code=language)
        if extra_lang:
            cities_translations_queryset = CityTranslation.objects.filter(
                Q(language_code=language) | Q(language_code=extra_lang)
            )
            regions_translations_queryset = RegionTranslation.objects.filter(
                Q(language_code=language) | Q(language_code=extra_lang)
            )
            countries_translations_queryset = CountryTranslation.objects.filter(
                Q(language_code=language) | Q(language_code=extra_lang)
            )

        prefetch = [
            Prefetch(
                'city_translations',
                queryset=cities_translations_queryset
            ),
            Prefetch(
                'country__country_translations',
                queryset=countries_translations_queryset
            ),
            Prefetch(
                'region__region_translations',
                queryset=regions_translations_queryset
            ),
            Prefetch(
               'zip_codes',
            )
        ]

        if q:
            # We can get a sequence of queries separated by semi-colons
            # with this order: City, Region (or Country), Country
            # if only one section is passed, that will always be the city,
            # the second section could be either the region or the country, and,
            # if a third section is passed, that will always be the country
            region_query = None
            country_query = None
            queries = list(map(lambda x: x.strip(), q.split(',', 2)))
            # Should always exists if 'q' is passed
            city_query = queries[0]
            if len(queries) >= 2:
                region_query = queries[1]
            if len(queries) >= 3:
                country_query = queries[2]

            city_list = City.objects.prefetch_related(*prefetch).all()
            if city_query:
                city_list = city_list.filter(
                    # Q(city_translations__name__unaccent__istartswith=city_query)
                    Q(city_translations__name__icontains=city_query)
                    & Q(city_translations__language_code=language)
                    | Q(zip_codes__zip_code=city_query)
                    | Q(code=city_query)
                )
            if region_query and not country_query:
                city_list = city_list.filter(
                    # Q(region__region_translations__name__unaccent__istartswith=region_query)
                    Q(region__region_translations__name__icontains=region_query)
                    & Q(region__region_translations__language_code=language)
                    | Q(region__code__iexact=region_query)
                    # | Q(country__country_translations__name__unaccent__istartswith=region_query)
                    | Q(country__country_translations__name__icontains=region_query)
                    & Q(country__country_translations__language_code=language)
                    | Q(country__code__iexact=region_query)
                )
            else:
                if region_query and country_query:
                    city_list = city_list.filter(
                        # Q(region__region_translations__name__unaccent__istartswith=region_query)
                        Q(region__region_translations__name__icontains=region_query)
                        & Q(region__region_translations__language_code=language)
                        | Q(region__code__iexact=region_query),
                        # Q(country__country_translations__name__unaccent__istartswith=country_query)
                        Q(country__country_translations__name__icontains=country_query)
                        & Q(country__country_translations__language_code=language)
                        | Q(country__code__iexact=country_query)
                    )
                if country_query and not region_query:
                    city_list = city_list.filter(
                        # Q(country__country_translations__name__unaccent__istartswith=country_query)
                        Q(country__country_translations__name__icontains=country_query)
                        & Q(country__country_translations__language_code=language)
                        | Q(country__code__iexact=country_query)
                    )

            city_list = city_list.distinct()[:limit]
            serializer = CitySerializer(city_list, many=True)
            return Response(serializer.data)
        else:
            return Response([])


@login_required
def upload_country(request):
    """
    Uploads the countries information and translations via a plain text file,
    say an xls aor ods file
    """
    if request.method == 'POST':
        file = UploadFile(request.POST, request.FILES)
        if file.is_valid():
            errors = handle_uploaded_countries(request.FILES['file'])
            if errors:
                return render(request, 'UploadCountries.html', {
                    "file": file,
                    "errors": errors
                })
            else:
                return HttpResponseRedirect(
                    reverse('cities-list', kwargs={'language': 'en'})
                )
    else:
        file = UploadFile()

    return render(request, 'UploadCountries.html', {
        "file": file
    })


@login_required
def download_countries(request, empty):
    """
    Downloads the file for uploading later the countries' information. It could
    be a filled file, with all the information already in the database, or an
    and empty file, only with the required file schema
    """
    countries = Country.objects.prefetch_related(
        'country_translations'
    ).all()
    headers = ['code', 'currency_code']

    language_choices = LanguageChoices.values
    language_choices.sort()
    for language_code in language_choices:
        headers.append(language_code)

    countries_list = [headers]
    if not empty:
        for country in countries:
            country_row = [country.code, country.currency_code]
            for translation in country.country_translations.all().order_by('language_code'):
                country_row.append(translation.name)
            countries_list.append(country_row)
    return django_excel.make_response_from_array(
        countries_list,
        'xls',
        file_name="Countries - %(date)s" % {
            "date": timezone.now().strftime("%d-%M-%Y")
        }
    )


@login_required
def upload_regions(request):

    all_countries = CountryTranslation.objects.filter(language_code='en')

    if request.method == 'POST':
        country_code = request.POST.get('country', '')
        file = UploadFile(request.POST, request.FILES)
        if file.is_valid():
            errors = handle_uploaded_regions(request.FILES['file'], country_code)
            if errors:
                return render(request, 'UploadRegions.html', {
                    "file": file,
                    "errors": errors,
                    'countries': all_countries
                })
            else:
                return HttpResponseRedirect(
                    reverse('cities-list', kwargs={'language': 'en'})
                )
    else:
        file = UploadFile()

    return render(request, 'UploadRegions.html', {
        "file": file,
        'countries': all_countries
    })


@login_required
def download_regions(request, empty):

    country_code = request.GET.get('country', '')
    if country_code:
        regions = Region.objects.prefetch_related(
            'region_translations', 'country'
        ).filter(country__code=country_code)

        headers = ['code', 'local_code', 'country_code']

        language_choices = LanguageChoices.values
        language_choices.sort()
        for language_code in language_choices:
            headers.append(language_code)

        regions_list = [headers]
        if not empty:
            for region in regions:
                region_row = [region.code, region.local_code, region.country.code]
                for translation in region.region_translations.all().order_by('language_code'):
                    region_row.append(translation.name)
                regions_list.append(region_row)

        file_name = "Regions%(country)s - %(date)s" % {
            'date': timezone.now().strftime("%d-%m-%Y"),
            'country': " - %s" % country_code if country_code else ''
        }
        return django_excel.make_response_from_array(
            regions_list,
            'xls',
            file_name=file_name
        )
    return HttpResponse(_('You must specify the regions\' country'))


@login_required
def upload_cities(request):

    all_countries = CountryTranslation.objects.filter(language_code='en')

    if request.method == 'POST':
        country_code = request.POST.get('country', '')
        file = UploadFile(request.POST, request.FILES)
        if file.is_valid():
            errors = handle_uploaded_cities(request.FILES['file'], country_code)
            if errors:
                return render(request, 'UploadCities.html', {
                    "file": file,
                    "errors": errors,
                    'countries': all_countries,
                })
            else:
                return HttpResponseRedirect(
                    reverse('cities-list', kwargs={'language': 'en'})
                )
    else:
        file = UploadFile()

    return render(request, 'UploadCities.html', {
        "file": file,
        'countries': all_countries
    })


@login_required
def download_cities(request, empty):

    country_code = request.GET.get('country', '')
    if country_code:
        cities = City.objects.prefetch_related(
            'city_translations', 'region', 'country'
        ).filter(country__code=country_code)

        headers = ['code', 'region_code', 'country_code']

        language_choices = LanguageChoices.values
        language_choices.sort()
        for language_code in language_choices:
            headers.append(language_code)

        cities_list = [headers]
        if not empty:
            for city in cities:
                city_row = [city.code, city.region.code, city.country.code]
                for translation in city.city_translations.all().order_by('language_code'):
                    city_row.append(translation.name)
                cities_list.append(city_row)

        file_name = "Cities%(country)s - %(date)s" % {
            'date': timezone.now().strftime("%d-%m-%Y"),
            'country': " - %s" % country_code if country_code else ''
        }
        return django_excel.make_response_from_array(
            cities_list,
            'xls',
            file_name=file_name
        )
    return HttpResponse(_('You must specify the cities\' country'))

