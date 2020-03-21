from django.utils.translation import gettext_lazy as _
from api.models import (
    Country, Region, City,
    CountryTranslation, RegionTranslation, CityTranslation,
    LanguageChoices, CurrencyCodeChoices
)


def handle_uploaded_countries(file):
    """ Handle the file with the countries' information"""
    errors = []
    array = file.get_array()
    headers = array[0]
    countries = array[1:]

    language_codes = headers[2:]
    if not set(language_codes).issubset(set(LanguageChoices.values)):
        errors.append(
            _("You're trying to upload translations with a "
              "language codes that are not specified in the standard "
              "ISO 639-1, please check the language headers in your file")
        )

    # Remove all duplicated currency codes
    currency_codes = list(dict.fromkeys([x[1] for x in countries if x[1].strip() != '']))
    if not set(currency_codes).issubset(set(CurrencyCodeChoices.values)):
        errors.append(
            _("You're trying to upload countries with currency codes that "
              "are not specified in the standard ISO 4217, please check "
              "the currency code's column in your file")
        )

    if not errors:
        for country_array in countries:
            if country_array[0].strip() != '':
                country, country_created = Country.objects.get_or_create(
                    code=country_array[0]
                )
                country.currency_code = country_array[1]

                country.save()

                for language in range(2, len(headers)):
                    translation, translation_created = CountryTranslation.objects.get_or_create(
                        language_code=headers[language],
                        country=country
                    )

                    translation.name = country_array[language]

                    translation.save()
        return
    return errors


def handle_uploaded_regions(file, country_code):
    """ Handle the file with the regions' information"""
    errors = []
    array = file.get_array()
    headers = array[0]
    regions = array[1:]

    language_codes = headers[3:]
    if not set(language_codes).issubset(set(LanguageChoices.values)):
        errors.append(
            _("You're trying to upload translations with a "
              "language codes that are not specified in the standard "
              "ISO 639-1, please check the language headers in your file")
        )

    countries_codes = list(dict.fromkeys([x[2] for x in regions if x[2].strip() != '']))
    if country_code:
        if len(countries_codes) > 1 or (len(countries_codes) == 1 and countries_codes[0] != country_code):
            errors.append(
                _("You downloaded the file intending to upload regions for a "
                  "specific country, now, you're uploading either more than one "
                  "country code, or a code different that the one you wanted to "
                  "upload at first")
            )
    else:
        errors.append(_("You need to specify a country you want to upload the regions for"))

    countries_instances_created = {}
    for c in countries_codes:
        try:
            countries_instances_created[c] = Country.objects.get(code=c)
        except Country.DoesNotExist:
            errors.append(_("The country with code %s does not exist") % c)
            break

    if not errors:
        # when creating countries instances, we can store here which of those
        # have been already instantiated, so we don't create an instance for
        # every specific region
        for region_array in regions:
            if region_array[0].strip() != '':
                region, region_created = Region.objects.get_or_create(
                    code=region_array[0],
                    country=countries_instances_created[region_array[2]]
                )
                region.local_code = region_array[1]
                region.save()

                for language in range(3, len(headers)):
                    translation, translation_created = RegionTranslation.objects.get_or_create(
                        language_code=headers[language],
                        region=region
                    )

                    translation.name = region_array[language]
                    translation.save()
        return
    return errors


def handle_uploaded_cities(file, country_code):
    """ Handle the file with the cities' information"""
    errors = []
    array = file.get_array()
    headers = array[0]
    cities = array[1:]

    language_codes = headers[3:]
    if not set(language_codes).issubset(set(LanguageChoices.values)):
        errors.append(
            _("You're trying to upload translations with a "
              "language codes that are not specified in the standard "
              "ISO 639-1, please check the language headers in your file")
        )

    countries_codes = list(dict.fromkeys([x[2] for x in cities if x[2].strip() != '']))
    regions_codes = list(dict.fromkeys([x[1] for x in cities if x[1].strip() != '']))
    if country_code:
        if len(countries_codes) > 1 or (len(countries_codes) == 1 and countries_codes[0] != country_code):
            errors.append(
                _("You downloaded the file intending to upload cities for a "
                  "specific country, now, you're uploading either more than one "
                  "country code, or a code different that the one you wanted to "
                  "upload at first")
            )
    else:
        errors.append(_("You need to specify a country you want to upload the cities for"))

    countries_instances_created = {}
    for c in countries_codes:
        try:
            countries_instances_created[c] = Country.objects.get(code=c)
        except Country.DoesNotExist:
            errors.append(_("The country with code %s does not exist") % c)
            break

    regions_instances_created = {}
    for r in regions_codes:
        try:
            regions_instances_created[r] = Region.objects.get(code=r)
        except Region.DoesNotExist:
            errors.append(_("The region with code %s does not exist") % r)
            break

    if not errors:
        # when creating countries instances, we can store here which of those
        # have been already instantiated, so we don't create an instance for
        # every specific region
        for city_array in cities:
            if city_array[0].strip() != '':
                city, city_created = City.objects.get_or_create(
                    code=city_array[0],
                    region=regions_instances_created[city_array[1]],
                    country=countries_instances_created[city_array[2]]
                )

                for language in range(3, len(headers)):
                    translation, translation_created = CityTranslation.objects.get_or_create(
                        language_code=headers[language],
                        city=city
                    )
                    translation.name = city_array[language]
                    translation.save()
        return
    return errors
