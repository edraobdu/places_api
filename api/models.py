from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

__author__ = 'Bezur'

__all__ = [
    'Country', 'Region', 'City', 'CountryTranslation',
    'RegionTranslation', 'CityTranslation', 'ZipCode',
    'LanguageChoices', 'CurrencyCodeChoices'
]


class CurrencyCodeChoices(models.TextChoices):
    """Currency codes following the standard ISO 4217"""

    PESO_CO = 'COP', _('Colombian Peso')
    EURO = 'EUR', _('Euro')
    DOLLAR = 'USD', _('Dollar')


class LanguageChoices(models.TextChoices):
    """Languages codes following the standard ISO 639-1"""

    # ABKHAZIAN = 'ab', _('Abkhazian')
    # AFAR = 'aa', _('Afar')
    # AFRIKAANS = 'af', _('Afrikaans')
    # AKAN = 'ak', _('Akan')
    # ALBANIAN = 'sq', _('Albanian')
    # AMHARIC = 'am', _('Amharic')
    # ARABIC = 'ar', _('Arabic')
    # ARAGONESE = 'an', _('Aragonese')
    # ARMENIAN = 'hy', _('Armenian')
    # ASSAMESE = 'as', _('Assamese')
    # AVARIC = 'av', _('Avaric')
    # AVESTAN = 'ae', _('Avestan')
    # AYMARA = 'ay', _('Aymara')
    # AZERBAIJANI = 'az', _('Azerbaijani')
    #
    # BAMBARA = 'bm', _('Bambara')
    # BASHKIR = 'ba', _('Bashkir')
    # BASQUE = 'eu', _('Basque')
    # BELARUSIAN = 'be', _('Belarusian')
    # BENGALI = 'bn', _('Bengali')
    # BIHARI = 'bh', _('Bihari')
    # BISLAMA = 'bi', _('Bislama')
    # BOSNIA = 'bs', _('Bosnia')
    # BRETON = 'br', _('Breton')
    # BULGARIAN = 'bg', _('Bulgarian')
    # BURMESE = 'my', _('Burmese')
    #
    # CATALAN = 'ca', _('Catalan')
    # CHAMORRO = 'ch', _('Chamorro')
    # CHECHEN = 'ce', _('Chechen')
    # CHICHEWA = 'ny', _('Chichewa')
    # CHINESE = 'zh', _('Chinese')
    # CHUVASH = 'cv', _('Chuvash')
    # CORNISH = 'kw', _('Cornish')
    # CORSICAN = 'co', _('Corsican')
    # CREE = 'cr', _('Cree')
    # CROATIAN = 'hr', _('Croatian')
    # CZECH = 'cs', _('Czech')
    #
    # DANISH = 'da', _('Danish')
    # DIVEHI = 'dv', _('Divehi')
    # DUTCH = 'nl', _('Dutch')
    # DZONGKHA = 'dz', _('Dzongkha')

    ENGLISH = 'en', _('English')
    # ESPERANTO = 'eo', _('Esperanto')
    # ESTONIAN = 'et', _('Estonian')
    # EWE = 'ee', _('Ewe')
    #
    # FAROESE = 'fo', _('Faroese')
    # FIJIAN = 'fj', _('Fijian')
    # FINNISH = 'fi', _('Finnish')
    # FRENCH = 'fr', _('French')
    # FULAH = 'ff', _('Fulah')
    #
    # GALICIAN = 'gl', _('Galician')
    # GEORGIAN = 'ka', _('Georgian')
    # GERMAN = 'de', _('German')
    # GREEK = 'el', _('Greek')
    # GUARANI = 'gn', _('Guarani')
    # GUJARATI = 'gu', _('Gujarati')
    #
    # HAITIAN = 'ht', _('Haitian')
    # HAUSA = 'ha', _('Hausa')
    # HEBREW = 'he', _('Hebrew')
    # HERERO = 'hz', _('Herero')
    # HINDI = 'hi', _('Hindi')
    # HIRI_MOTU = 'ho', _('Hiri Motu')
    # HUNGARIAN = 'hu', _('Hungarian')
    #
    SPANISH = 'es', _('Spanish')


class AbstractTranslation(models.Model):
    """
    This abstract model will define the translations of any model
    related to a specific language
    """

    language_code = models.code = models.CharField(
        max_length=2,
        choices=LanguageChoices.choices
    )
    name = models.CharField(max_length=250)

    class Meta:
        abstract = True


def flag_path(instance, filename):
    return '{0}_flags/{1}'.format(
        instance.__class__.__name__.lower(),
        filename
    )


class AbstractPlace(models.Model):
    """ By now, models just share the 'flags' attribute"""

    # for Django forms to display this field as non
    # required, we add blank true
    flag = models.ImageField(
        upload_to=flag_path,
        null=True,
        blank=True
    )

    class Meta:
        abstract = True


class Country(AbstractPlace):
    """
    Defines the country object.

    The 'code' will attach to the standard ISO 3166-1, that
    defines a 2 letter code for each country
    """

    code = models.CharField(max_length=2, unique=True)
    currency_code = models.CharField(
        choices=CurrencyCodeChoices.choices,
        max_length=3,
        blank=True
    )

    def __str__(self):
        country_translation = self.country_translations.filter(
            language_code=LanguageChoices.ENGLISH
        )
        return country_translation[0].name if country_translation else self.code


class Region(AbstractPlace):
    """
    Defines the Region object, should belong to a country

    The 'code' will attach to the standard ISO 3166-2:{country code}, that
    defines a 3 letter code for each region within a specific country, e.g
    for colombia we'll look up the ISO 3166-2:CO
    """
    code = models.CharField(max_length=3)
    # Besides the standard, some countries require or emit its own code
    # for every region under its administration
    local_code = models.CharField(max_length=20, blank=True, default='')
    country = models.ForeignKey(
        'Country',
        null=True,
        on_delete=models.SET_NULL,
        related_name='regions'
    )

    def __str__(self):
        region_translation = self.region_translations.filter(
            language_code=LanguageChoices.ENGLISH
        )

        return region_translation[0].name if region_translation else self.code

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['code', 'country'],
                name='unique_country_region'
            )
        ]


class City(AbstractPlace):
    """
    Unfortunately, there's not any standard ISO for cities around the world,
    however, it is possible that every country has it's own standard
    system to identify its cities.

    So, we need to apply a unique constraint for 'country' and 'code'
    """
    code = models.CharField(max_length=10)
    region = models.ForeignKey(
        'Region',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='cities'
    )
    country = models.ForeignKey(
        'Country',
        on_delete=models.CASCADE,
        related_name='cities'
    )

    def __str__(self):
        city_translation = self.city_translations.filter(
            language_code=LanguageChoices.ENGLISH
        )
        return city_translation[0].name if city_translation else self.code

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['code', 'country'],
                name='unique_country_city'
            )
        ]


class ZipCode(models.Model):
    """A simple object that contains the zip code number for cities"""
    city = models.ForeignKey(
        'City',
        on_delete=models.CASCADE,
        related_name='zip_codes'
    )
    zip_code = models.CharField(
        max_length=6,
        validators=[RegexValidator(r'^\d{1,10}$')],
        unique=True
    )

    def __str__(self):
        return self.zip_code


class CountryTranslation(AbstractTranslation):
    country = models.ForeignKey(
        'Country',
        on_delete=models.CASCADE,
        related_name='country_translations'
    )

    def __str__(self):
        return "%s in %s is %s" % (
            self.country,
            LanguageChoices(self.language_code).name,
            self.name
        )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['language_code', 'country'],
                name='unique_language_country'
            )
        ]


class RegionTranslation(AbstractTranslation):
    region = models.ForeignKey(
        'Region',
        on_delete=models.CASCADE,
        related_name='region_translations'
    )

    def __str__(self):
        return "%s in %s is %s" % (
            self.region,
            LanguageChoices(self.language_code).label,
            self.name
        )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['language_code', 'region'],
                name='unique_language_region'
            )
        ]


class CityTranslation(AbstractTranslation):
    city = models.ForeignKey(
        'City',
        on_delete=models.CASCADE,
        related_name='city_translations'
    )

    def __str__(self):
        return "%s in %s is %s" % (
            self.city,
            LanguageChoices(self.language_code).label,
            self.name
        )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['language_code', 'city'],
                name='unique_language_city'
            )
        ]