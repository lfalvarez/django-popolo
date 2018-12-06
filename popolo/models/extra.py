# -*- coding: utf-8 -*-
from model_utils import Choices

from popolo.behaviors.models import Permalinkable, Timestampable, Dateframeable
from popolo.models.mixins import LinkShortcutsMixin, SourceShortcutsMixin, IdentifierShortcutsMixin
from popolo.querysets import ElectoralResultQuerySet, KeyEventQuerySet
from popolo.validators import validate_percentage

try:
    from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
except ImportError:
    # This fallback import is the version that was deprecated in
    # Django 1.7 and is removed in 1.9:
    from django.contrib.contenttypes.generic import GenericRelation, GenericForeignKey

try:
    # PassTrhroughManager was removed in django-model-utils 2.4
    # see issue #22 at https://github.com/openpolis/django-popolo/issues/22
    from model_utils.managers import PassThroughManager
except ImportError:
    pass

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


@python_2_unicode_compatible
class Language(models.Model):
    """
    Maps languages, with names and 2-char iso 639-1 codes.
    Taken from http://dbpedia.org, using a sparql query
    """

    name = models.CharField(_("name"), max_length=128, help_text=_("English name of the language"))

    iso639_1_code = models.CharField(
        _("iso639_1 code"), max_length=2, unique=True, help_text=_("ISO 639_1 code, ex: en, it, de, fr, es, ...")
    )

    dbpedia_resource = models.CharField(
        _("dbpedia resource"),
        max_length=255,
        blank=True,
        null=True,
        help_text=_("DbPedia URI of the resource"),
        unique=True,
    )

    class Meta:
        verbose_name = _("Language")
        verbose_name_plural = _("Languages")

    def __str__(self):
        return u"{0} ({1})".format(self.name, self.iso639_1_code)


@python_2_unicode_compatible
class AreaI18Name(models.Model):
    """
    Internationalized name for an Area.
    Contains references to language and area.
    """

    area = models.ForeignKey("Area", related_name="i18n_names", on_delete=models.CASCADE,)

    language = models.ForeignKey("Language", verbose_name=_("Language"), on_delete=models.CASCADE)

    name = models.CharField(_("name"), max_length=255)

    def __str__(self):
        return "{0} - {1}".format(self.language, self.name)

    class Meta:
        verbose_name = _("I18N Name")
        verbose_name_plural = _("I18N Names")
        unique_together = ("area", "language", "name")


@python_2_unicode_compatible
class OriginalProfession(models.Model):
    """
    Profession of a Person, according to the original source
    """

    name = models.CharField(_("name"), max_length=512, unique=True, help_text=_("The original profession name"))

    normalized_profession = models.ForeignKey(
        "Profession",
        null=True,
        blank=True,
        related_name="original_professions",
        help_text=_("The normalized profession"),
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("Original profession")
        verbose_name_plural = _("Original professions")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Upgrade persons professions when the normalized profession is changed

        :param args:
        :param kwargs:
        :return:
        """
        super(OriginalProfession, self).save(*args, **kwargs)
        if self.normalized_profession:
            self.persons_with_this_original_profession.exclude(profession=self.normalized_profession).update(
                profession=self.normalized_profession
            )


@python_2_unicode_compatible
class Profession(IdentifierShortcutsMixin, models.Model):
    """
    Profession of a Person, as a controlled vocabulary
    """

    name = models.CharField(_("name"), max_length=512, unique=True, help_text=_("Normalized profession name"))

    # array of items referencing
    # "http://popoloproject.com/schemas/identifier.json#"
    identifiers = GenericRelation("Identifier", help_text=_("Other identifiers for this profession (ISTAT code)"))

    class Meta:
        verbose_name = _("Normalized profession")
        verbose_name_plural = _("Normalized professions")

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class OriginalEducationLevel(models.Model):
    """
    Non-normalized education level, as received from sources
    With identifiers (ICSED).
    """

    name = models.CharField(_("name"), max_length=512, unique=True, help_text=_("Education level name"))

    normalized_education_level = models.ForeignKey(
        "EducationLevel",
        null=True,
        blank=True,
        related_name="original_education_levels",
        help_text=_("The normalized education_level"),
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("Original education level")
        verbose_name_plural = _("Original education levels")

    def __str__(self):
        return u"{0} ({1})".format(self.name, self.normalized_education_level)

    def save(self, *args, **kwargs):
        """Upgrade persons education_levels when the normalized education_level is changed

        :param args:
        :param kwargs:
        :return:
        """
        super(OriginalEducationLevel, self).save(*args, **kwargs)
        if self.normalized_education_level:
            self.persons_with_this_original_education_level.exclude(
                education_level=self.normalized_education_level
            ).update(education_level=self.normalized_education_level)


@python_2_unicode_compatible
class EducationLevel(IdentifierShortcutsMixin, models.Model):
    """
    Normalized education level
    With identifiers (ICSED).
    """

    name = models.CharField(_("name"), max_length=256, unique=True, help_text=_("Education level name"))

    # array of items referencing
    # "http://popoloproject.com/schemas/identifier.json#"
    identifiers = GenericRelation("Identifier", help_text=_("Other identifiers for this education level (ICSED code)"))

    class Meta:
        verbose_name = _("Normalized education level")
        verbose_name_plural = _("Normalized education level")

    def __str__(self):
        return u"{0}".format(self.name)


@python_2_unicode_compatible
class KeyEvent(Permalinkable, Dateframeable, Timestampable, models.Model):
    """
    An electoral event generically describes an electoral session.

    It is used mainly to group all electoral results.

    This is an extension of the Popolo schema
    """

    @property
    def slug_source(self):
        return u"{0} {1}".format(self.name, self.get_event_type_display())

    name = models.CharField(
        _("name"),
        max_length=256,
        blank=True,
        null=True,
        help_text=_("A primary, generic name, e.g.: Local elections 2016"),
    )

    # TODO: transform into an external table, so that new event_types can be added by non-coders
    EVENT_TYPES = Choices(
        ("ELE", "election", _("Election round")),
        ("ELE-POL", "pol_election", _("National election")),
        ("ELE-EU", "eu_election", _("European election")),
        ("ELE-REG", "reg_election", _("Regional election")),
        ("ELE-METRO", "metro_election", _("Metropolitan election")),
        ("ELE-PROV", "prov_election", _("Provincial election")),
        ("ELE-COM", "com_election", _("Comunal election")),
        ("ITL", "it_legislature", _("IT legislature")),
        ("EUL", "eu_legislature", _("EU legislature")),
        ("XAD", "externaladm", _("External administration")),
    )
    event_type = models.CharField(
        _("event type"),
        default="ELE",
        max_length=12,
        choices=EVENT_TYPES,
        help_text=_("The electoral type, e.g.: election, legislature, ..."),
    )

    identifier = models.CharField(
        _("identifier"), max_length=512, blank=True, null=True, help_text=_("An issued identifier")
    )

    url_name = "keyevent-detail"

    try:
        # PassTrhroughManager was removed in django-model-utils 2.4,
        # see issue #22
        objects = PassThroughManager.for_queryset_class(KeyEventQuerySet)()
    except:
        objects = KeyEventQuerySet.as_manager()

    class Meta:
        verbose_name = _("Key event")
        verbose_name_plural = _("Key events")
        unique_together = ("start_date", "event_type")

    def add_result(self, **electoral_result):
        self.results.create(**electoral_result)

    def __str__(self):
        return u"{0}".format(self.name)


@python_2_unicode_compatible
class ElectoralResult(SourceShortcutsMixin, LinkShortcutsMixin, Permalinkable, Timestampable, models.Model):
    """
    An electoral result is a set of numbers and percentages, describing
    a general, list or personal outcome within an electoral session.

    It regards a single Organization (usually an institution).
    It may regard a certain constituency (Area).
    It may regard an electoral list (Organization).
    It may regard a candidate (Person).

    It is always the child of an KeyEvent (session).

    When it's related to a general result, then generic values are
    populated.
    When it's related to a list number and percentage of votes of the list
    are also populated.
    When it's related to a person (candidate), then the flag `is_elected` is
    populated.

    When a result is not related to a constituency (Area), then it means
    the numbers refer to the total for all constituencies involved.

    This is an extension of the Popolo schema
    """

    @property
    def slug_source(self):

        fields = [self.event, self.organization]
        if self.constituency is None:
            fields.append(self.constituency)

        if self.list:
            fields.append(self.list)

        if self.candidate:
            fields.append(self.candidate)

        return " ".join(map(str, fields))

    event = models.ForeignKey(
        "KeyEvent",
        limit_choices_to={"event_type": "ELE"},
        related_name="results",
        verbose_name=_("Electoral event"),
        help_text=_("The generating electoral event"),
        on_delete=models.CASCADE,
    )

    constituency = models.ForeignKey(
        "Area",
        blank=True,
        null=True,
        related_name="electoral_results",
        verbose_name=_("Electoral constituency"),
        help_text=_("The electoral constituency these electoral data are referred to"),
        on_delete=models.CASCADE,
    )

    organization = models.ForeignKey(
        "Organization",
        related_name="general_electoral_results",
        verbose_name=_("Institution"),
        help_text=_("The institution these electoral data are referred to"),
        on_delete=models.CASCADE,
    )

    list = models.ForeignKey(
        "Organization",
        blank=True,
        null=True,
        related_name="list_electoral_results",
        verbose_name=_("Electoral list"),
        help_text=_("The electoral list these electoral data are referred to"),
        on_delete=models.CASCADE,
    )

    candidate = models.ForeignKey(
        "Person",
        blank=True,
        null=True,
        related_name="electoral_results",
        verbose_name=_("Candidate"),
        help_text=_("The candidate in the election these data are referred to"),
        on_delete=models.CASCADE,
    )

    # array of items referencing "http://popoloproject.com/schemas/source.json#"
    sources = GenericRelation("SourceRel", help_text=_("URLs to sources about the electoral result"))

    # array of items referencing "http://popoloproject.com/schemas/link.json#"
    links = GenericRelation("LinkRel", help_text=_("URLs to documents referring to the electoral result"))

    n_eligible_voters = models.PositiveIntegerField(
        _("Total number of eligible voters"), blank=True, null=True, help_text=_("The total number of eligible voter")
    )

    n_ballots = models.PositiveIntegerField(
        _("Total number of ballots casted"), blank=True, null=True, help_text=_("The total number of ballots casted")
    )

    perc_turnout = models.FloatField(
        _("Voter turnout"),
        blank=True,
        null=True,
        validators=[validate_percentage],
        help_text=_("The percentage of eligible voters that casted a ballot"),
    )

    perc_valid_votes = models.FloatField(
        _("Valid votes perc."),
        blank=True,
        null=True,
        validators=[validate_percentage],
        help_text=_("The percentage of valid votes among those cast"),
    )

    perc_null_votes = models.FloatField(
        _("Null votes perc."),
        blank=True,
        null=True,
        validators=[validate_percentage],
        help_text=_("The percentage of null votes among those cast"),
    )

    perc_blank_votes = models.FloatField(
        _("Blank votes perc."),
        blank=True,
        null=True,
        validators=[validate_percentage],
        help_text=_("The percentage of blank votes among those cast"),
    )

    n_preferences = models.PositiveIntegerField(
        _("Total number of preferences"),
        blank=True,
        null=True,
        help_text=_("The total number of preferences expressed for the list/candidate"),
    )

    perc_preferences = models.FloatField(
        _("Preference perc."),
        blank=True,
        null=True,
        validators=[validate_percentage],
        help_text=_("The percentage of preferences expressed for the list/candidate"),
    )

    is_elected = models.NullBooleanField(
        _("Is elected"), blank=True, null=True, help_text=_("If the candidate has been elected with the result")
    )

    url_name = "electoral-result-detail"

    try:
        # PassTrhroughManager was removed in django-model-utils 2.4,
        # see issue #22
        objects = PassThroughManager.for_queryset_class(ElectoralResultQuerySet)()
    except:
        objects = ElectoralResultQuerySet.as_manager()

    class Meta:
        verbose_name = _("Electoral result")
        verbose_name_plural = _("Electoral results")

    def __str__(self):
        return self.slug_source
