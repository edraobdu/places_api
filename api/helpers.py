from django.utils.translation import gettext_lazy as _
from api.models import Country, CountryTranslation, LanguageChoices, CurrencyCodeChoices


def handle_uploaded_countries(file):
    """ Handle the file with the countries' information"""

    errors = []
    array = file.get_array()
    headers = array[0]
    countries = array[1:]

    language_codes = headers[2:]
    if language_codes != LanguageChoices.values:
        errors.append(
            _("You're trying to upload translations with a "
              "language codes that are not specified in the standard "
              "ISO 639-1, please check the language headers in your file")
        )

    currency_codes = list(map(lambda x: x[1], countries))
    if currency_codes != CurrencyCodeChoices.values:
        errors.append(
            _("You're trying to upload countries with currency codes that "
              "are not specified in the standard ISO 4217, please check "
              "the currency code's column in your file")
        )

    if not errors:
        for country_array in countries:
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
