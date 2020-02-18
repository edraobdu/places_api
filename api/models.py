from django.db import models
from django.utils.translation import gettext_lazy as _

__author__ = 'Bezur'

__all__ = [
    'Language', 'Country',
    'Region', 'City',
    'LanguageTranslation', 'CountryTranslation',
    'RegionTranslation', 'CityTranslation',
    'LanguageChoices'
]


class LanguageChoices(models.TextChoices):
    """Languages codes following the standard ISO 639-1"""

    ENGLISH = 'en', _('English')
    SPANISH = 'es', _('Spanish')


class Translation(models.Model):
    """This abstract model will define the translations of any model
    related to a specific language"""

    language_code = models.code = models.CharField(
        max_length=2,
        choices=LanguageChoices.choices
    )
    name = models.CharField(max_length=250)

    class Meta:
        abstract = True


class Language(models.Model):
    """Defines a language object, it won't be used for relationships"""
    iso_code = models.CharField(
        max_length=2,
        choices=LanguageChoices.choices,
        unique=True
    )

    def __str__(self):
        return str(LanguageChoices(self.iso_code).label)


class Country(models.Model):
    """Defines the country object"""
    iso_code = models.CharField(max_length=2, unique=True)

    def __str__(self):
        country_translation = self.country_translations.filter(
            language_code=LanguageChoices.ENGLISH
        )
        return country_translation[0].name if country_translation else self.iso_code


class Region(models.Model):
    """Defines the Region object, should belong to a country"""
    iso_code = models.CharField(max_length=3)
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

        return region_translation[0].name if region_translation else self.iso_code

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['iso_code', 'country'],
                name='unique_country_region'
            )
        ]


class City(models.Model):
    zip_code = models.CharField(
        max_length=6, blank=True
    )
    iso_code = models.CharField(max_length=3)
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
        return city_translation[0].name if city_translation else self.iso_code

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['iso_code', 'country'],
                name='unique_country_city'
            )
        ]


# TRANSLATIONS
class LanguageTranslation(Translation):
    language = models.ForeignKey(
        'Language',
        on_delete=models.CASCADE,
        related_name='language_translations'
    )

    def __str__(self):
        return "%s in %s is %s" % (
            self.language,
            LanguageChoices(self.language_code).label,
            self.name
        )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['language_code', 'language'],
                name='unique_language_language'
            )
        ]


class CountryTranslation(Translation):
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


class RegionTranslation(Translation):
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


class CityTranslation(Translation):
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
