# -*- coding: utf-8 -*-
from popolo.models.mixins import SourceShortcutsMixin
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
from model_utils import Choices

from popolo.behaviors.models import Timestampable, Dateframeable, GenericRelatable, Permalinkable
from popolo.querysets import (
    AreaRelationshipQuerySet,
    OwnershipQuerySet,
    PersonalRelationshipQuerySet,
)


@python_2_unicode_compatible
class AreaRelationship(SourceShortcutsMixin, Dateframeable, Timestampable, models.Model):
    """
    A relationship between two areas.
    Must be defined by a classification (type, ex: other_parent, previosly_in, ...)

    This is an **extension** to the popolo schema
    """

    source_area = models.ForeignKey(
        "Area",
        related_name="from_relationships",
        verbose_name=_("Source area"),
        help_text=_("The Area the relation starts from"),
        on_delete=models.CASCADE,
    )

    dest_area = models.ForeignKey(
        "Area",
        related_name="to_relationships",
        verbose_name=_("Destination area"),
        help_text=_("The Area the relationship ends to"),
        on_delete=models.CASCADE,
    )

    CLASSIFICATION_TYPES = Choices(
        ("FIP", "former_istat_parent", _("Former ISTAT parent")),
        ("AMP", "alternate_mountain_community_parent", _("Alternate mountain community parent")),
        ("ACP", "alternate_consortium_parent", _("Alternate consortium of municipality parent")),
    )
    classification = models.CharField(
        max_length=3,
        choices=CLASSIFICATION_TYPES,
        help_text=_("The relationship classification, ex: Former ISTAT parent, ..."),
    )

    note = models.TextField(blank=True, null=True, help_text=_("Additional info about the relationship"))

    # array of items referencing "http://popoloproject.com/schemas/link.json#"
    sources = GenericRelation("SourceRel", help_text=_("URLs to source documents about the relationship"))

    class Meta:
        verbose_name = _("Area relationship")
        verbose_name_plural = _("Area relationships")

    try:
        # PassTrhroughManager was removed in django-model-utils 2.4,
        # see issue #22
        objects = PassThroughManager.for_queryset_class(AreaRelationshipQuerySet)()
    except:
        objects = AreaRelationshipQuerySet.as_manager()

    def __str__(self):
        if self.classification:
            return "{0} -[{1} ({3} -> {4})]-> {2}".format(
                self.source_area.name,
                self.get_classification_display(),
                self.dest_area.name,
                self.start_date,
                self.end_date,
            )
        else:
            return "{0} -[({2} -> {3})]-> {1}".format(
                self.source_area.name, self.dest_area.name, self.start_date, self.end_date
            )


@python_2_unicode_compatible
class PersonalRelationship(SourceShortcutsMixin, Dateframeable, Timestampable, models.Model):
    """
    A relationship between two persons.
    Must be defined by a classification (type, ex: friendship, family, ...)

    This is an **extension** to the popolo schema
    """

    # person or organization that is a member of the organization

    source_person = models.ForeignKey(
        "Person",
        related_name="to_relationships",
        verbose_name=_("Source person"),
        help_text=_("The Person the relation starts from"),
        on_delete=models.CASCADE,
    )

    # reference to "http://popoloproject.com/schemas/person.json#"
    dest_person = models.ForeignKey(
        "Person",
        related_name="from_relationships",
        verbose_name=_("Destination person"),
        help_text=_("The Person the relationship ends to"),
        on_delete=models.CASCADE,
    )

    WEIGHTS = Choices(
        (-1, "strongly_negative", _("Strongly negative")),
        (-2, "negative", _("Negative")),
        (0, "neutral", _("Neutral")),
        (1, "positive", _("Positive")),
        (2, "strongly_positive", _("Strongly positive")),
    )
    weight = models.IntegerField(
        _("weight"),
        default=0,
        choices=WEIGHTS,
        help_text=_("The relationship weight, " "from strongly negative, to strongly positive"),
    )

    classification = models.CharField(
        max_length=255, help_text=_("The relationship classification, ex: friendship, family, ...")
    )

    # array of items referencing "http://popoloproject.com/schemas/source.json#"
    sources = GenericRelation("SourceRel", help_text=_("URLs to source documents about the relationship"))

    class Meta:
        verbose_name = _("Personal relationship")
        verbose_name_plural = _("Personal relationships")

    try:
        # PassTrhroughManager was removed in django-model-utils 2.4,
        # see issue #22
        objects = PassThroughManager.for_queryset_class(PersonalRelationshipQuerySet)()
    except:
        objects = PersonalRelationshipQuerySet.as_manager()

    def __str__(self):
        if self.label:
            return "{0} -[{1} ({2}]> {3}".format(
                self.source_person.name, self.classification, self.get_weight_display(), self.dest_person.name
            )


@python_2_unicode_compatible
class ClassificationRel(GenericRelatable, Dateframeable, models.Model):
    """
    The relation between a generic object and a Classification
    """

    classification = models.ForeignKey(
        "Classification",
        related_name="related_objects",
        help_text=_("A Classification instance assigned to this object"),
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return "{0} - {1}".format(self.content_object, self.classification)


@python_2_unicode_compatible
class Ownership(SourceShortcutsMixin, Dateframeable, Timestampable, Permalinkable, models.Model):
    """
    A relationship between an organization and an owner
    (be it a Person or another Organization), that indicates
    an ownership and quantifies it.

    This is an **extension** to the popolo schema
    """

    @property
    def slug_source(self):
        return u"{0} {1} ({2}%)".format(self.owner.name, self.organization.name, self.percentage * 100)

    # person or organization that is a member of the organization
    organization = models.ForeignKey(
        "Organization",
        related_name="owned_organizations",
        verbose_name=_("Person"),
        help_text=_("The organization that is owned"),
        on_delete=models.CASCADE,
    )

    # reference to "http://popoloproject.com/schemas/person.json#"
    owner_person = models.ForeignKey(
        "Person",
        blank=True,
        null=True,
        related_name="ownerships",
        verbose_name=_("Person"),
        help_text=_("An owner of the organization, when it is a Person"),
        on_delete=models.CASCADE,
    )

    # reference to "http://popoloproject.com/schemas/organization.json#"
    owner_organization = models.ForeignKey(
        "Organization",
        blank=True,
        null=True,
        related_name="ownerships",
        verbose_name=_("Organization"),
        help_text=_("An owner of the organization, when it is an Organization"),
        on_delete=models.CASCADE,
    )

    percentage = models.FloatField(
        _("percentage ownership"),
        validators=[validate_percentage],
        help_text=_("The *required* percentage ownership, expressed as a floating " "number, from 0 to 1"),
    )
    # array of items referencing "http://popoloproject.com/schemas/source.json#"
    sources = GenericRelation("SourceRel", help_text=_("URLs to source documents about the ownership"))

    @property
    def owner(self):
        if self.owner_organization:
            return self.owner_organization
        else:
            return self.owner_person

    url_name = "ownership-detail"

    class Meta:
        verbose_name = _("Ownership")
        verbose_name_plural = _("Ownerships")

    try:
        # PassTrhroughManager was removed in django-model-utils 2.4,
        # see issue #22
        objects = PassThroughManager.for_queryset_class(OwnershipQuerySet)()
    except:
        objects = OwnershipQuerySet.as_manager()

    def __str__(self):
        if self.label:
            return "{0} -[owns {1}% of]> {2}".format(
                getattr(self.owner, "name"), self.percentage, self.organization.name
            )


@python_2_unicode_compatible
class LinkRel(GenericRelatable, models.Model):
    """
    The relation between a generic object and a Source
    """

    link = models.ForeignKey(
        "Link",
        related_name="related_objects",
        help_text=_("A relation to a Link instance assigned to this object"),
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return "{0} - {1}".format(self.content_object, self.link)


@python_2_unicode_compatible
class SourceRel(GenericRelatable, models.Model):
    """
    The relation between a generic object and a Source
    """

    source = models.ForeignKey(
        "Source",
        related_name="related_objects",
        help_text=_("A Source instance assigned to this object"),
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return "{0} - {1}".format(self.content_object, self.source)


@python_2_unicode_compatible
class KeyEventRel(GenericRelatable, models.Model):
    """
    The relation between a generic object and a KeyEvent
    """

    key_event = models.ForeignKey(
        "KeyEvent",
        related_name="related_objects",
        help_text=_("A relation to a KeyEvent instance assigned to this object"),
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return "{0} - {1}".format(self.content_object, self.key_event)
