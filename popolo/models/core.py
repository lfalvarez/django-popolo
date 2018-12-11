# -*- coding: utf-8 -*-

from popolo.models.extra import Language, KeyEvent
from popolo.models.mixins import (
    SourceShortcutsMixin,
    LinkShortcutsMixin,
    IdentifierShortcutsMixin,
    OtherNamesShortcutsMixin,
    ContactDetailsShortcutsMixin,
    ClassificationShortcutsMixin,
)
from popolo.models.relations import (
    AreaRelationship,
    Ownership,
    PersonalRelationship,
)

try:
    from django.contrib.contenttypes.fields import (
        GenericRelation,
        GenericForeignKey,
    )
except ImportError:
    # This fallback import is the version that was deprecated in
    # Django 1.7 and is removed in 1.9:
    from django.contrib.contenttypes.generic import (
        GenericRelation,
        GenericForeignKey,
    )

try:
    # PassTrhroughManager was removed in django-model-utils 2.4
    # see issue #22 at https://github.com/openpolis/django-popolo/issues/22
    from model_utils.managers import PassThroughManager
except ImportError:
    pass

# -*- coding: utf-8 -*-
from datetime import datetime
from django.db.models import Q, Index

from popolo.utils import PartialDatesInterval, PartialDate

try:
    from django.contrib.contenttypes.fields import (
        GenericRelation,
        GenericForeignKey,
    )
except ImportError:
    # This fallback import is the version that was deprecated in
    # Django 1.7 and is removed in 1.9:
    from django.contrib.contenttypes.generic import (
        GenericRelation,
        GenericForeignKey,
    )

try:
    # PassTrhroughManager was removed in django-model-utils 2.4
    # see issue #22 at https://github.com/openpolis/django-popolo/issues/22
    from model_utils.managers import PassThroughManager
except ImportError:
    pass

from django.core.validators import RegexValidator
from django.contrib.gis.db import models
from model_utils import Choices
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from popolo.behaviors.models import (
    Permalinkable,
    Timestampable,
    Dateframeable,
    GenericRelatable,
)
from popolo.querysets import (
    PostQuerySet,
    OtherNameQuerySet,
    ContactDetailQuerySet,
    MembershipQuerySet,
    OrganizationQuerySet,
    PersonQuerySet,
    AreaQuerySet,
    IdentifierQuerySet,
    ClassificationQuerySet,
)


@python_2_unicode_compatible
class Person(
    ContactDetailsShortcutsMixin,
    OtherNamesShortcutsMixin,
    IdentifierShortcutsMixin,
    LinkShortcutsMixin,
    SourceShortcutsMixin,
    Dateframeable,
    Timestampable,
    Permalinkable,
    models.Model,
):
    """
    A real person, alive or dead
    see schema at http://popoloproject.com/schemas/person.json#
    """

    json_ld_context = "http://popoloproject.com/contexts/person.jsonld"
    json_ld_type = "http://www.w3.org/ns/person#Person"

    @property
    def slug_source(self):
        return u"{0} {1}".format(self.name, self.birth_date)

    name = models.CharField(
        _("name"),
        max_length=512,
        blank=True,
        null=True,
        db_index=True,
        help_text=_("A person's preferred full name"),
    )

    # array of items referencing
    # "http://popoloproject.com/schemas/other_name.json#"
    other_names = GenericRelation(
        "OtherName", help_text=_("Alternate or former names")
    )

    # array of items referencing
    # "http://popoloproject.com/schemas/identifier.json#"
    identifiers = GenericRelation(
        "Identifier", help_text=_("Issued identifiers")
    )

    family_name = models.CharField(
        _("family name"),
        max_length=128,
        blank=True,
        null=True,
        db_index=True,
        help_text=_("One or more family names"),
    )

    given_name = models.CharField(
        _("given name"),
        max_length=128,
        blank=True,
        null=True,
        db_index=True,
        help_text=_("One or more primary given names"),
    )

    additional_name = models.CharField(
        _("additional name"),
        max_length=128,
        blank=True,
        null=True,
        help_text=_("One or more secondary given names"),
    )

    honorific_prefix = models.CharField(
        _("honorific prefix"),
        max_length=32,
        blank=True,
        null=True,
        help_text=_("One or more honorifics preceding a person's name"),
    )

    honorific_suffix = models.CharField(
        _("honorific suffix"),
        max_length=32,
        blank=True,
        null=True,
        help_text=_("One or more honorifics following a person's name"),
    )

    patronymic_name = models.CharField(
        _("patronymic name"),
        max_length=128,
        blank=True,
        null=True,
        help_text=_("One or more patronymic names"),
    )

    sort_name = models.CharField(
        _("sort name"),
        max_length=128,
        blank=True,
        null=True,
        db_index=True,
        help_text=_("A name to use in an lexicographically " "ordered list"),
    )

    email = models.EmailField(
        _("email"),
        blank=True,
        null=True,
        help_text=_("A preferred email address"),
    )

    gender = models.CharField(
        _("gender"),
        max_length=32,
        blank=True,
        null=True,
        db_index=True,
        help_text=_("A gender"),
    )

    birth_date = models.CharField(
        _("birth date"),
        max_length=10,
        blank=True,
        null=True,
        db_index=True,
        help_text=_("A date of birth"),
    )

    birth_location = models.CharField(
        _("birth location"),
        max_length=128,
        blank=True,
        null=True,
        help_text=_("Birth location as a string"),
    )

    birth_location_area = models.ForeignKey(
        "Area",
        blank=True,
        null=True,
        related_name="persons_born_here",
        verbose_name=_("birth location Area"),
        help_text=_(
            "The geographic area corresponding " "to the birth location"
        ),
        on_delete=models.CASCADE,
    )

    death_date = models.CharField(
        _("death date"),
        max_length=10,
        blank=True,
        null=True,
        db_index=True,
        help_text=_("A date of death"),
    )

    image = models.URLField(
        _("image"), blank=True, null=True, help_text=_("A URL of a head shot")
    )

    summary = models.CharField(
        _("summary"),
        max_length=1024,
        blank=True,
        null=True,
        help_text=_("A one-line account of a person's life"),
    )

    biography = models.TextField(
        _("biography"),
        blank=True,
        null=True,
        help_text=_("An extended account of a person's life"),
    )

    national_identity = models.CharField(
        _("national identity"),
        max_length=128,
        blank=True,
        null=True,
        help_text=_("A national identity"),
    )

    original_profession = models.ForeignKey(
        "OriginalProfession",
        blank=True,
        null=True,
        related_name="persons_with_this_original_profession",
        verbose_name=_("Non normalized profession"),
        help_text=_("The profession of this person, non normalized"),
        on_delete=models.CASCADE,
    )

    profession = models.ForeignKey(
        "Profession",
        blank=True,
        null=True,
        related_name="persons_with_this_profession",
        verbose_name=_("Normalized profession"),
        help_text=_("The profession of this person"),
        on_delete=models.CASCADE,
    )

    original_education_level = models.ForeignKey(
        "OriginalEducationLevel",
        blank=True,
        null=True,
        related_name="persons_with_this_original_education_level",
        verbose_name=_("Non normalized education level"),
        help_text=_("The education level of this person, non normalized"),
        on_delete=models.CASCADE,
    )

    education_level = models.ForeignKey(
        "EducationLevel",
        blank=True,
        null=True,
        related_name="persons_with_this_education_level",
        verbose_name=_("Normalized education level"),
        help_text=_("The education level of this person"),
        on_delete=models.CASCADE,
    )

    # array of items referencing
    # "http://popoloproject.com/schemas/contact_detail.json#"
    contact_details = GenericRelation(
        "ContactDetail", help_text="Means of contacting the person"
    )

    # array of items referencing "http://popoloproject.com/schemas/link.json#"
    links = GenericRelation(
        "LinkRel", help_text="URLs to documents related to the person"
    )

    # array of items referencing "http://popoloproject.com/schemas/source.json#"
    sources = GenericRelation(
        "SourceRel", help_text="URLs to source documents about the person"
    )

    related_persons = models.ManyToManyField(
        "self",
        through="PersonalRelationship",
        through_fields=("source_person", "dest_person"),
        symmetrical=False,
    )
    url_name = "person-detail"

    class Meta:
        verbose_name = _("Person")
        verbose_name_plural = _("People")

    try:
        # PassTrhroughManager was removed in django-model-utils 2.4,
        # see issue #22
        objects = PassThroughManager.for_queryset_class(PersonQuerySet)()
    except:
        objects = PersonQuerySet.as_manager()

    def add_membership(self, organization, **kwargs):
        """Add person's membership to an Organization

        Multiple memberships to the same organization can be added
        only if direct (no post) and if dates are not overlapping.

        :param organization: Organization instance
        :param kwargs: membership parameters
        :return: Membership, if just created
        """

        # new  dates interval as PartialDatesInterval instance
        new_int = PartialDatesInterval(
            start=kwargs.get("start_date", None),
            end=kwargs.get("end_date", None),
        )

        is_overlapping = False

        allow_overlap = kwargs.pop("allow_overlap", False)

        # loop over memberships to the same org
        same_org_memberships = self.memberships.filter(
            organization=organization, post__isnull=True
        )
        for i in same_org_memberships:

            # existing identifier interval as PartialDatesInterval instance
            i_int = PartialDatesInterval(start=i.start_date, end=i.end_date)

            # compute overlap days
            #  > 0 means crossing
            # == 0 means touching (considered non overlapping)
            #  < 0 meand not overlapping
            overlap = PartialDate.intervals_overlap(new_int, i_int)

            if overlap > 0:
                is_overlapping = True

        if not is_overlapping or allow_overlap:
            m = self.memberships.create(organization=organization, **kwargs)
            return m

    def add_memberships(self, memberships):
        """Add multiple *blank* memberships to person.

        :param memberships: list of Membership dicts
        :return: None
        """
        for m in memberships:
            self.add_membership(**m)

    def add_role(self, post, **kwargs):
        """add person's role (membership through post) in an Organization

        A *role* is identified by the Membership to a given Post in an
        Organization.

        If the organization is specified in the kwargs parameters, then
        the Post needs to be a *generic* one (not linked to a specific
        organization).

        If no organization is specified in kwargs, then the Post needs
        to be linked to a specific organization.

        Multiple roles to the same post and organization can only be added
        if dates are not overlapping

        :param post: the post fullfilled
        :return: the Membership to rhe role
        """

        # read special kwarg that indicates whether to check label or not
        check_label = kwargs.pop("check_label", False)

        if not "organization" in kwargs:
            if post.organization is None:
                raise Exception(
                    "Post needs to be specific, "
                    "i.e. linked to an organization"
                )
            org = post.organization
        else:
            if post.organization is not None:
                raise Exception(
                    "Post needs to be generic, "
                    "i.e. not linked to an organization"
                )
            org = kwargs.pop("organization")

        # new  dates interval as PartialDatesInterval instance
        new_int = PartialDatesInterval(
            start=kwargs.get("start_date", None),
            end=kwargs.get("end_date", None),
        )

        is_overlapping = False

        allow_overlap = kwargs.pop("allow_overlap", False)

        # loop over memberships to the same org and post
        # consider labels, too, if not None, and if specified with the check_label arg
        # for role as Ministro, Assessore, Sottosegretario
        label = kwargs.get("label", None)
        if label and check_label:
            same_org_post_memberships = self.memberships.filter(
                organization=org, post=post, label=label
            )
        else:
            same_org_post_memberships = self.memberships.filter(
                organization=org, post=post
            )

        for i in same_org_post_memberships:

            # existing identifier interval as PartialDatesInterval instance
            i_int = PartialDatesInterval(start=i.start_date, end=i.end_date)

            # compute overlap days
            #  > 0 means crossing
            # == 0 means touching (end date == start date)
            #  < 0 means not touching
            # dates only overlap if crossing
            overlap = PartialDate.intervals_overlap(new_int, i_int)

            if overlap > 0:
                is_overlapping = True

        if not is_overlapping or allow_overlap:
            m = self.memberships.create(post=post, organization=org, **kwargs)

            return m

    def add_roles(self, roles):
        """Add multiple roles to person.

        :param memberships: list of Role dicts
        :return: None
        """
        for r in roles:
            self.add_role(**r)

    def add_role_on_behalf_of(self, post, behalf_organization, **kwargs):
        """add a role (post) in an Organization on behhalf of the given
        Organization

        :param post: the post fullfilled
        :param behalf_organiazione: the organization on behalf of which the Post
        is fullfilled
        :return: the Membership to rhe role
        """
        return self.add_role(post, on_behalf_of=behalf_organization, **kwargs)

    def add_ownership(self, organization, **kwargs):
        """add this person as owner to the given `organization`

        :param organization: the organization this one will be a owner of
        :param kwargs: ownership parameters
        :return: the added Ownership
        """
        o = Ownership(organization=organization, owner_person=self, **kwargs)
        o.save()
        return o

    def add_relationship(self, dest_person, **kwargs):
        """add a personal relaationship to dest_person
        with parameters kwargs

        :param dest_person:
        :param kwargs:
        :return:
        """
        r = PersonalRelationship(
            source_person=self, dest_person=dest_person, **kwargs
        )
        r.save()
        return r

    def organizations_has_role_in(self):
        """get all organizations the person has a role in

        :return:
        """
        return Organization.objects.filter(
            posts__in=Post.objects.filter(memberships__person=self)
        )

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Organization(
    ContactDetailsShortcutsMixin,
    OtherNamesShortcutsMixin,
    IdentifierShortcutsMixin,
    ClassificationShortcutsMixin,
    LinkShortcutsMixin,
    SourceShortcutsMixin,
    Dateframeable,
    Timestampable,
    Permalinkable,
    models.Model,
):
    """
    A group with a common purpose or reason for existence that goes beyond
    the set of people belonging to it
    see schema at http://popoloproject.com/schemas/organization.json#
    """

    @property
    def slug_source(self):
        return "{0} {1} {2}".format(self.name, self.identifier, self.start_date)

    name = models.CharField(
        _("name"),
        max_length=512,
        help_text=_("A primary name, e.g. a legally recognized name"),
    )

    identifier = models.CharField(
        _("identifier"),
        max_length=128,
        blank=True,
        null=True,
        help_text=_(
            "The main issued identifier, or fiscal code, for organization"
        ),
    )

    classification = models.CharField(
        _("classification"),
        max_length=256,
        blank=True,
        null=True,
        help_text=_("The nature of the organization, legal form in many cases"),
    )

    thematic_classification = models.CharField(
        _("thematic classification"),
        max_length=256,
        blank=True,
        null=True,
        help_text=_("What the organization does, in what fields, ..."),
    )

    classifications = GenericRelation(
        "ClassificationRel",
        help_text=_(
            "ATECO, Legal Form and all other available classifications"
        ),
    )

    # array of items referencing
    # "http://popoloproject.com/schemas/other_name.json#"
    other_names = GenericRelation(
        "OtherName", help_text=_("Alternate or former names")
    )

    # array of items referencing
    # "http://popoloproject.com/schemas/identifier.json#"
    identifiers = GenericRelation(
        "Identifier", help_text=_("Issued identifiers")
    )

    # reference to "http://popoloproject.com/schemas/organization.json#"
    parent = models.ForeignKey(
        "Organization",
        blank=True,
        null=True,
        related_name="children",
        verbose_name=_("Parent"),
        help_text=_("The organization that contains this " "organization"),
        on_delete=models.CASCADE,
    )

    # reference to "http://popoloproject.com/schemas/area.json#"
    area = models.ForeignKey(
        "Area",
        blank=True,
        null=True,
        related_name="organizations",
        help_text=_(
            "The geographic area to which this " "organization is related"
        ),
        on_delete=models.CASCADE,
    )

    abstract = models.CharField(
        _("abstract"),
        max_length=256,
        blank=True,
        null=True,
        help_text=_("A one-line description of an organization"),
    )

    description = models.TextField(
        _("biography"),
        blank=True,
        null=True,
        help_text=_("An extended description of an organization"),
    )

    founding_date = models.CharField(
        _("founding date"),
        max_length=10,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                regex="^[0-9]{4}(-[0-9]{2}){0,2}$",
                message="founding date must follow the given pattern: ^[0-9]{"
                "4}(-[0-9]{2}){0,2}$",
                code="invalid_founding_date",
            )
        ],
        help_text=_("A date of founding"),
    )

    dissolution_date = models.CharField(
        _("dissolution date"),
        max_length=10,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                regex="^[0-9]{4}(-[0-9]{2}){0,2}$",
                message="dissolution date must follow the given pattern: ^["
                "0-9]{4}(-[0-9]{2}){0,2}$",
                code="invalid_dissolution_date",
            )
        ],
        help_text=_("A date of dissolution"),
    )

    image = models.URLField(
        _("image"),
        max_length=255,
        blank=True,
        null=True,
        help_text=_("A URL of an image, to identify the organization visually"),
    )

    new_orgs = models.ManyToManyField(
        "Organization",
        blank=True,
        related_name="old_orgs",
        symmetrical=False,
        help_text=_(
            "Link to organization(s) after dissolution_date, "
            "needed to track mergers, acquisition, splits."
        ),
    )

    # array of items referencing
    # "http://popoloproject.com/schemas/contact_detail.json#"
    contact_details = GenericRelation(
        "ContactDetail", help_text=_("Means of contacting the organization")
    )

    # array of references to KeyEvent instances related to this Organization
    key_events = GenericRelation(
        "KeyEventRel", help_text=_("KeyEvents related to this organization")
    )

    # array of items referencing "http://popoloproject.com/schemas/link.json#"
    links = GenericRelation(
        "LinkRel", help_text=_("URLs to documents about the organization")
    )

    # array of items referencing "http://popoloproject.com/schemas/source.json#"
    sources = GenericRelation(
        "SourceRel",
        help_text=_("URLs to source documents about the organization"),
    )

    person_members = models.ManyToManyField(
        "Person",
        through="Membership",
        through_fields=("organization", "person"),
        related_name="organizations_memberships",
    )

    organization_members = models.ManyToManyField(
        "Organization",
        through="Membership",
        through_fields=("organization", "member_organization"),
        related_name="organizations_memberships",
    )

    @property
    def members(self):
        """Returns list of members (it's not a queryset)

        :return: list of Person or Organization instances
        """
        return list(self.person_members.all()) + list(
            self.organization_members.all()
        )

    person_owners = models.ManyToManyField(
        "Person",
        through="Ownership",
        through_fields=("organization", "owner_person"),
        related_name="organizations_ownerships",
    )

    organization_owners = models.ManyToManyField(
        "Organization",
        through="Ownership",
        through_fields=("organization", "owner_organization"),
        related_name="organization_ownerships",
    )

    @property
    def owners(self):
        """Returns list of owners (it's not a queryset)

        :return: list of Person or Organization instances
        """
        return list(self.person_owners.all()) + list(
            self.organization_owners.all()
        )

    url_name = "organization-detail"

    class Meta:
        verbose_name = _("Organization")
        verbose_name_plural = _("Organizations")

    try:
        # PassTrhroughManager was removed in django-model-utils 2.4,
        # see issue #22
        objects = PassThroughManager.for_queryset_class(OrganizationQuerySet)()
    except:
        objects = OrganizationQuerySet.as_manager()

    def add_member(self, member, **kwargs):
        """add a member to this organization

        :param member: a Person or an Organization
        :param kwargs: membership parameters
        :return: the added member (be it Person or Organization)
        """
        if isinstance(member, Person):
            m = member.add_membership(self, **kwargs)
        elif isinstance(member, Organization):
            m = Membership(
                organization=self, member_organization=member, **kwargs
            )
        else:
            raise Exception(_("Member must be Person or Organization"))
        m.save()
        return m

    def add_members(self, members):
        """add multiple *blank* members to this organization

        :param members: list of Person/Organization to be added as members
        :return:
        """
        for m in members:
            self.add_member(m)

    def add_membership(self, organization, **kwargs):
        """add this organization as member to the given `organization`

        :param organization: the organization this one will be a member of
        :param kwargs: membership parameters
        :return: the added Membership
        """
        m = Membership(
            organization=organization, member_organization=self, **kwargs
        )
        m.save()
        return m

    def add_owner(self, owner, **kwargs):
        """add a owner to this organization

        :param owner: a Person or an Organization
        :param kwargs: ownership parameters
        :return: the added owner (be it Person or Organization)
        """
        if isinstance(owner, Person):
            o = Ownership(organization=self, owner_person=owner, **kwargs)
        elif isinstance(owner, Organization):
            o = Ownership(organization=self, owner_organization=owner, **kwargs)
        else:
            raise Exception(_("Owner must be Person or Organization"))
        o.save()
        return o

    def add_ownership(self, organization, **kwargs):
        """add this organization as owner to the given `organization`

        :param organization: the organization this one will be a owner of
        :param kwargs: ownership parameters
        :return: the added Membership
        """
        o = Ownership(
            organization=organization, owner_organization=self, **kwargs
        )
        o.save()
        return o

    def add_post(self, **kwargs):
        """add post, specified with kwargs to this organization

        :param kwargs: Post parameters
        :return: the added Post
        """
        p = Post(organization=self, **kwargs)
        p.save()
        return p

    def add_posts(self, posts):
        for p in posts:
            self.add_post(**p)

    def merge_from(self, *args, **kwargs):
        """merge a list of organizations into this one, creating relationships
        of new/old orgs

        :param args: elements to merge into
        :param kwargs: may contain the moment key
        :return:
        """
        moment = kwargs.get(
            "moment", datetime.strftime(datetime.now(), "%Y-%m-%d")
        )

        for i in args:
            i.close(moment=moment, reason=_("Merged into other organizations"))
            i.new_orgs.add(self)
        self.start_date = moment
        self.save()

    def split_into(self, *args, **kwargs):
        """split this organization into a list of other organizations, creating
        relationships of new/old orgs

        :param args: elements to be split into
        :param kwargs: keyword args that may contain moment
        :return:
        """
        moment = kwargs.get(
            "moment", datetime.strftime(datetime.now(), "%Y-%m-%d")
        )

        for i in args:
            i.start_date = moment
            i.save()
            self.new_orgs.add(i)
        self.close(moment=moment, reason=_("Split into other organiations"))

    def add_key_event_rel(self, key_event):
        """Add key_event (rel) to the organization

        :param key_event: existing KeyEvent instance or id
        :return: the KeyEventRel instance just added
        """
        # then add the KeyEventRel to classifications
        if not isinstance(key_event, int) and not isinstance(
            key_event, KeyEvent
        ):
            raise Exception(
                "key_event needs to be an integer ID or a KeyEvent instance"
            )
        if isinstance(key_event, int):
            ke, created = self.key_events.get_or_create(key_event_id=key_event)
        else:
            ke, created = self.key_events.get_or_create(key_event=key_event)

        # and finally return the KeyEvent just added
        return ke

    def add_key_events(self, new_key_events):
        """ add multiple key_events
        :param new_key_events: KeyEvent ids to be added
        :return:
        """
        # add objects
        for new_key_event in new_key_events:
            if "key_event" in new_key_event:
                self.add_key_event_rel(**new_key_event)
            else:
                raise Exception("key_event need to be present in dict")

    def update_key_events(self, new_items):
        """update key_events,
        removing those not present in new_items
        overwriting those present and existing,
        adding those present and not existing

        :param new_items: the new list of key_events
        :return:
        """
        existing_ids = set(self.key_events.values_list("key_event", flat=True))
        new_ids = set(n.get("key_event", None) for n in new_items)

        # remove objects
        delete_ids = existing_ids - set(new_ids)
        self.key_events.filter(key_event__in=delete_ids).delete()

        # update objects
        self.add_key_events([{"key_event": ke_id} for ke_id in new_ids])

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Organization")
        verbose_name_plural = _("Organizations")
        unique_together = ("name", "identifier", "start_date")


@python_2_unicode_compatible
class RoleType(models.Model):
    """
    A role type (Sindaco, Assessore, CEO), with priority, used to
    build a sorted drop-down in interfaces.

    Each role type is related to a given organization's
    OP_FORMA_GIURIDICA classification.
    """

    label = models.CharField(
        _("label"), max_length=256, help_text=_("A label describing the post")
    )

    classification = models.ForeignKey(
        "Classification",
        related_name="role_types",
        limit_choices_to={"scheme": "FORMA_GIURIDICA_OP"},
        help_text=_(
            "The OP_FORMA_GIURIDICA classification this role type is related to"
        ),
        on_delete=models.CASCADE,
    )

    other_label = models.CharField(
        _("other label"),
        max_length=32,
        blank=True,
        null=True,
        help_text=_("An alternate label, such as an abbreviation"),
    )

    priority = models.IntegerField(
        _("priority"),
        blank=True,
        null=True,
        help_text=_(
            "The priority of this role type, within the same classification group"
        ),
    )

    def __str__(self):
        return "{0} in {1}".format(self.label, self.classification.descr)

    class Meta:
        verbose_name = _("Role type")
        verbose_name_plural = _("Role types")
        unique_together = ("classification", "label")


@python_2_unicode_compatible
class Post(
    ContactDetailsShortcutsMixin,
    LinkShortcutsMixin,
    SourceShortcutsMixin,
    Dateframeable,
    Timestampable,
    Permalinkable,
    models.Model,
):
    """
    A position that exists independent of the person holding it
    see schema at http://popoloproject.com/schemas/json#
    """

    @property
    def slug_source(self):
        return self.label

    label = models.CharField(
        _("label"),
        max_length=256,
        blank=True,
        help_text=_("A label describing the post"),
    )

    other_label = models.CharField(
        _("other label"),
        max_length=32,
        blank=True,
        null=True,
        help_text=_("An alternate label, such as an abbreviation"),
    )

    role = models.CharField(
        _("role"),
        max_length=512,
        blank=True,
        null=True,
        help_text=_("The function that the holder of the post fulfills"),
    )

    role_type = models.ForeignKey(
        "RoleType",
        related_name="posts",
        blank=True,
        null=True,
        verbose_name=_("Role type"),
        help_text=_("The structured role type for this post"),
        on_delete=models.CASCADE,
    )

    priority = models.FloatField(
        _("priority"),
        blank=True,
        null=True,
        help_text=_(
            "The absolute priority of this specific post, with respect to all others."
        ),
    )

    # reference to "http://popoloproject.com/schemas/organization.json#"
    organization = models.ForeignKey(
        "Organization",
        related_name="posts",
        blank=True,
        null=True,
        verbose_name=_("Organization"),
        help_text=_("The organization in which the post is held"),
        on_delete=models.CASCADE,
    )

    # reference to "http://popoloproject.com/schemas/area.json#"
    area = models.ForeignKey(
        "Area",
        blank=True,
        null=True,
        related_name="posts",
        verbose_name=_("Area"),
        help_text=_("The geographic area to which the post is related"),
        on_delete=models.CASCADE,
    )

    appointed_by = models.ForeignKey(
        "Post",
        blank=True,
        null=True,
        related_name="appointees",
        verbose_name=_("Appointed by"),
        help_text=_(
            "The Post that officially appoints members to this one, "
            "ex: Secr. of Defence is appointed by POTUS"
        ),
        on_delete=models.CASCADE,
    )

    holders = models.ManyToManyField(
        "Person",
        through="Membership",
        through_fields=("post", "person"),
        related_name="roles_held",
    )

    organizations = models.ManyToManyField(
        "Organization",
        through="Membership",
        through_fields=("post", "organization"),
        related_name="posts_available",
    )

    # array of items referencing
    # "http://popoloproject.com/schemas/contact_detail.json#"
    contact_details = GenericRelation(
        "ContactDetail",
        help_text=_("Means of contacting the holder of the post"),
    )

    # array of items referencing "http://popoloproject.com/schemas/link.json#"
    links = GenericRelation(
        "LinkRel", help_text=_("URLs to documents about the post")
    )

    # array of items referencing "http://popoloproject.com/schemas/source.json#"
    sources = GenericRelation(
        "SourceRel", help_text=_("URLs to source documents about the post")
    )

    url_name = "post-detail"

    class Meta:
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")

    try:
        # PassTrhroughManager was removed in django-model-utils 2.4,
        # see issue #22
        objects = PassThroughManager.for_queryset_class(PostQuerySet)()
    except:
        objects = PostQuerySet.as_manager()

    def add_person(self, person, **kwargs):
        """add given person to this post (through membership)
        A person having a post is also an explicit member
        of the organization holding the post.

        :param person: person to add
        :param kwargs: membership parameters (label, dates, ...)
        :return:
        """
        m = Membership(
            post=self, person=person, organization=self.organization, **kwargs
        )
        m.save()

    def add_person_on_behalf_of(self, person, organization, **kwargs):
        """add given `person` to this post (through a membership)
        on behalf of given `organization`

        :param person:
        :param organization: the organization on behalf the post is taken
        :param kwargs: membership parameters (label, dates, ...)
        :return:
        """
        m = Membership(
            post=self,
            person=person,
            organization=self.organization,
            on_behalf_of=organization,
            **kwargs
        )
        m.save()

    def add_appointer(self, role):
        """add role that appoints members to this one

        :param role: The apponinter
        :return: the appointee
        """
        self.appointed_by = role
        self.save()
        return self

    def __str__(self):
        return self.label


@python_2_unicode_compatible
class Membership(
    ContactDetailsShortcutsMixin,
    LinkShortcutsMixin,
    SourceShortcutsMixin,
    Dateframeable,
    Timestampable,
    Permalinkable,
    models.Model,
):
    """
    A relationship between a person and an organization
    see schema at http://popoloproject.com/schemas/membership.json#
    """

    @property
    def slug_source(self):
        return u"{0} {1}".format(
            self.member.name, self.organization.name, self.label
        )

    label = models.CharField(
        _("label"),
        max_length=512,
        blank=True,
        null=True,
        help_text=_("A label describing the membership"),
    )

    role = models.CharField(
        _("role"),
        max_length=512,
        blank=True,
        null=True,
        help_text=_("The role that the member fulfills in the organization"),
    )

    # person or organization that is a member of the organization
    member_organization = models.ForeignKey(
        "Organization",
        blank=True,
        null=True,
        related_name="memberships_as_member",
        verbose_name=_("Organization"),
        help_text=_("The organization who is a member of the organization"),
        on_delete=models.CASCADE,
    )

    # reference to "http://popoloproject.com/schemas/person.json#"
    person = models.ForeignKey(
        "Person",
        blank=True,
        null=True,
        related_name="memberships",
        verbose_name=_("Person"),
        help_text=_("The person who is a member of the organization"),
        on_delete=models.CASCADE,
    )

    @property
    def member(self):
        if self.member_organization:
            return self.member_organization
        else:
            return self.person

    # reference to "http://popoloproject.com/schemas/organization.json#"
    organization = models.ForeignKey(
        "Organization",
        blank=True,
        null=True,
        related_name="memberships",
        verbose_name=_("Organization"),
        help_text=_(
            "The organization in which the person or organization is a member"
        ),
        on_delete=models.CASCADE,
    )

    on_behalf_of = models.ForeignKey(
        "Organization",
        blank=True,
        null=True,
        related_name="memberships_on_behalf_of",
        verbose_name=_("On behalf of"),
        help_text=_(
            "The organization on whose behalf the person "
            "is a member of the organization"
        ),
        on_delete=models.CASCADE,
    )

    # reference to "http://popoloproject.com/schemas/post.json#"
    post = models.ForeignKey(
        "Post",
        blank=True,
        null=True,
        related_name="memberships",
        verbose_name=_("Post"),
        help_text=_(
            "The post held by the person in the "
            "organization through this membership"
        ),
        on_delete=models.CASCADE,
    )

    # reference to "http://popoloproject.com/schemas/area.json#"
    area = models.ForeignKey(
        "Area",
        blank=True,
        null=True,
        related_name="memberships",
        verbose_name=_("Area"),
        help_text=_("The geographic area to which the membership is related"),
        on_delete=models.CASCADE,
    )

    # these fields store information present in the Openpolitici
    # database, that will constitute part of the Election
    # info-set in the future
    # THEY ARE TO BE CONSIDERED TEMPORARY
    constituency_descr_tmp = models.CharField(
        blank=True,
        null=True,
        max_length=128,
        verbose_name=_("Constituency location description"),
    )

    electoral_list_descr_tmp = models.CharField(
        blank=True,
        null=True,
        max_length=512,
        verbose_name=_("Electoral list description"),
    )
    # END OF TEMP

    electoral_event = models.ForeignKey(
        "KeyEvent",
        blank=True,
        null=True,
        limit_choices_to={"event_type__contains": "ELE"},
        related_name="memberships_assigned",
        verbose_name=_("Electoral event"),
        help_text=_("The electoral event that assigned this membership"),
        on_delete=models.CASCADE,
    )

    # array of items referencing
    # "http://popoloproject.com/schemas/contact_detail.json#"
    contact_details = GenericRelation(
        "ContactDetail",
        help_text=_("Means of contacting the member of the organization"),
    )

    # array of items referencing "http://popoloproject.com/schemas/link.json#"
    links = GenericRelation(
        "LinkRel", help_text=_("URLs to documents about the membership")
    )

    # array of items referencing "http://popoloproject.com/schemas/source.json#"
    sources = GenericRelation(
        "SourceRel",
        help_text=_("URLs to source documents about the membership"),
    )

    url_name = "membership-detail"

    class Meta:
        verbose_name = _("Membership")
        verbose_name_plural = _("Memberships")

    try:
        # PassTrhroughManager was removed in django-model-utils 2.4,
        # see issue #22
        objects = PassThroughManager.for_queryset_class(MembershipQuerySet)()
    except:
        objects = MembershipQuerySet.as_manager()

    def __str__(self):
        if self.label:
            return "{0} -[{1}]> {2}".format(
                getattr(self.member, "name"), self.label, self.organization
            )
        else:
            return "{0} -[member of]> {1}".format(
                getattr(self.member, "name"), self.organization
            )


@python_2_unicode_compatible
class ContactDetail(
    SourceShortcutsMixin,
    Timestampable,
    Dateframeable,
    GenericRelatable,
    models.Model,
):
    """
    A means of contacting an entity
    see schema at http://popoloproject.com/schemas/contact-detail.json#
    """

    CONTACT_TYPES = Choices(
        ("ADDRESS", "address", _("Address")),
        ("EMAIL", "email", _("Email")),
        ("URL", "url", _("Url")),
        ("MAIL", "mail", _("Snail mail")),
        ("TWITTER", "twitter", _("Twitter")),
        ("FACEBOOK", "facebook", _("Facebook")),
        ("PHONE", "phone", _("Telephone")),
        ("MOBILE", "mobile", _("Mobile")),
        ("TEXT", "text", _("Text")),
        ("VOICE", "voice", _("Voice")),
        ("FAX", "fax", _("Fax")),
        ("CELL", "cell", _("Cell")),
        ("VIDEO", "video", _("Video")),
        ("INSTAGRAM", "instagram", _("Instagram")),
        ("YOUTUBE", "youtube", _("Youtube")),
        ("PAGER", "pager", _("Pager")),
        ("TEXTPHONE", "textphone", _("Textphone")),
    )

    label = models.CharField(
        _("label"),
        max_length=256,
        blank=True,
        help_text=_("A human-readable label for the contact detail"),
    )

    contact_type = models.CharField(
        _("type"),
        max_length=12,
        choices=CONTACT_TYPES,
        help_text=_("A type of medium, e.g. 'fax' or 'email'"),
    )

    value = models.CharField(
        _("value"),
        max_length=256,
        help_text=_("A value, e.g. a phone number or email address"),
    )

    note = models.CharField(
        _("note"),
        max_length=512,
        blank=True,
        null=True,
        help_text=_(
            "A note, e.g. for grouping contact details by physical location"
        ),
    )

    # array of items referencing "http://popoloproject.com/schemas/source.json#"
    sources = GenericRelation(
        "SourceRel",
        help_text=_("URLs to source documents about the contact detail"),
    )

    class Meta:
        verbose_name = _("Contact detail")
        verbose_name_plural = _("Contact details")

    try:
        # PassTrhroughManager was removed in django-model-utils 2.4,
        # see issue #22
        objects = PassThroughManager.for_queryset_class(ContactDetailQuerySet)()
    except:
        objects = ContactDetailQuerySet.as_manager()

    def __str__(self):
        return u"{0} - {1}".format(self.value, self.contact_type)


@python_2_unicode_compatible
class Area(
    SourceShortcutsMixin,
    LinkShortcutsMixin,
    IdentifierShortcutsMixin,
    OtherNamesShortcutsMixin,
    Permalinkable,
    Dateframeable,
    Timestampable,
    models.Model,
):
    """
    An Area insance is a geographic area whose geometry may change over time.

    An area may change the name, or end its status as autonomous place,
    for a variety of reasons this events are mapped through these
    fields:

    - reason_end - a brief description of the reason (merge, split, ...)
    - new_places, old_places - what comes next, or what was before,
      this is multiple to allow description of merges and splits
    - popolo.behaviours.Dateframeable's start_date and end_date fields

    From **TimeStampedModel** the class inherits **created** and
    **modified** fields, to keep track of creation and
    modification timestamps

    From **Prioritized**, it inherits the **priority** field,
    to allow custom sorting order

    """

    @property
    def slug_source(self):
        return u"{0}-{1}".format(self.istat_classification, self.identifier)

    name = models.CharField(
        _("name"),
        max_length=256,
        blank=True,
        help_text=_("The official, issued name"),
    )

    identifier = models.CharField(
        _("identifier"),
        max_length=128,
        blank=True,
        unique=True,
        help_text=_("The main issued identifier"),
    )

    classification = models.CharField(
        _("classification"),
        max_length=128,
        blank=True,
        help_text=_(
            "An area category, according to GEONames definitions: "
            "http://www.geonames.org/export/codes.html"
        ),
    )

    ISTAT_CLASSIFICATIONS = Choices(
        ("NAZ", "nazione", _("Country")),
        ("RIP", "ripartizione", _("Geographic partition")),
        ("REG", "regione", _("Region")),
        ("PROV", "provincia", _("Province")),
        ("CM", "metro", _("Metropolitan area")),
        ("COM", "comune", _("Municipality")),
    )
    istat_classification = models.CharField(
        _("ISTAT classification"),
        max_length=4,
        blank=True,
        null=True,
        choices=ISTAT_CLASSIFICATIONS,
        help_text=_(
            "An area category, according to ISTAT: "
            "Ripartizione Geografica, Regione, Provincia, "
            "Città Metropolitana, Comune"
        ),
    )

    # array of items referencing
    # "http://popoloproject.com/schemas/identifier.json#"
    identifiers = GenericRelation(
        "Identifier",
        help_text=_(
            "Other issued identifiers (zip code, other useful codes, ...)"
        ),
    )

    @property
    def other_identifiers(self):
        return self.identifiers

    # array of items referencing
    # "http://popoloproject.com/schemas/other_name.json#"
    other_names = GenericRelation(
        "OtherName", help_text=_("Alternate or former names")
    )

    # reference to "http://popoloproject.com/schemas/area.json#"
    parent = models.ForeignKey(
        "Area",
        blank=True,
        null=True,
        related_name="children",
        verbose_name=_("Main parent"),
        help_text=_(
            "The area that contains this area, "
            "as for the main administrative subdivision."
        ),
        on_delete=models.CASCADE,
    )

    is_provincial_capital = models.NullBooleanField(
        blank=True,
        null=True,
        verbose_name=_("Is provincial capital"),
        help_text=_(
            "If the city is a provincial capital."
            "Takes the Null value if not a municipality."
        ),
    )

    geometry = models.MultiPolygonField(
        _("Geometry"),
        null=True,
        blank=True,
        help_text=_("The geometry of the area"),
        geography=True,
        dim=2,
    )

    coordinates = models.PointField(
        _("Coordinates"),
        null=True,
        blank=True,
        help_text=_("The coordinates (latitude, longitude) of the area"),
    )

    @property
    def geom(self):
        return self.geometry

    @property
    def gps_lat(self):
        return self.coordinates

    @property
    def gps_lon(self):
        return self.coordinates

    # inhabitants, can be useful for some queries
    inhabitants = models.PositiveIntegerField(
        _("inhabitants"),
        null=True,
        blank=True,
        help_text=_("The total number of inhabitants"),
    )

    # array of items referencing "http://popoloproject.com/schemas/links.json#"
    links = GenericRelation(
        "LinkRel",
        blank=True,
        null=True,
        help_text=_("URLs to documents relted to the Area"),
    )

    # array of items referencing "http://popoloproject.com/schemas/source.json#"
    sources = GenericRelation(
        "SourceRel",
        blank=True,
        null=True,
        help_text=_("URLs to source documents about the Area"),
    )

    # related areas
    related_areas = models.ManyToManyField(
        "self",
        through="AreaRelationship",
        through_fields=("source_area", "dest_area"),
        help_text=_("Relationships between areas"),
        related_name="inversely_related_areas",
        symmetrical=False,
    )

    new_places = models.ManyToManyField(
        "self",
        blank=True,
        related_name="old_places",
        symmetrical=False,
        help_text=_("Link to area(s) after date_end"),
    )

    url_name = "area-detail"

    class Meta:
        verbose_name = _("Geographic Area")
        verbose_name_plural = _("Geographic Areas")

    try:
        # PassTrhroughManager was removed in django-model-utils 2.4,
        # see issue #22
        objects = PassThroughManager.for_queryset_class(AreaQuerySet)()
    except:
        objects = AreaQuerySet.as_manager()

    def add_i18n_name(self, name, language):
        """add an i18 name to the area
        if the name already exists, then it is not duplicated

        :param name: The i18n name
        :param language: a Language instance
        :return:
        """

        if not isinstance(language, Language):
            raise Exception(
                _("The language parameter needs to be a Language instance")
            )
        i18n_name, created = self.i18n_names.get_or_create(
            language=language, name=name
        )

        return i18n_name

    def merge_from(self, *areas, **kwargs):
        """merge a list of areas into this one, creating relationships
        of new/old places

        :param areas:
        :param kwargs:
        :return:
        """
        moment = kwargs.get(
            "moment", datetime.strftime(datetime.now(), "%Y-%m-%d")
        )

        for ai in areas:
            ai.close(moment=moment, reason=_("Merged into other areas"))
            ai.new_places.add(self)
        self.start_date = moment
        self.save()

    def split_into(self, *areas, **kwargs):
        """split this area into a list of other areas, creating
        relationships of new/old places

        :param areas:
        :param kwargs: keyword args that may contain moment
        :return:
        """
        moment = kwargs.get(
            "moment", datetime.strftime(datetime.now(), "%Y-%m-%d")
        )

        for ai in areas:
            ai.start_date = moment
            ai.save()
            self.new_places.add(ai)
        self.close(moment=moment, reason=_("Split into other areas"))

    def add_relationship(
        self, area, classification, start_date=None, end_date=None, **kwargs
    ):
        """add a personal relaationship to dest_area
        with parameters kwargs

        :param area: destination area
        :param classification: the classification (rel label)
        :param start_date:
        :param end_date:
        :param kwargs: other relationships parameters
        :return: a Relationship instance
        """
        relationship, created = AreaRelationship.objects.get_or_create(
            source_area=self,
            dest_area=area,
            classification=classification,
            start_date=start_date,
            end_date=end_date,
            defaults=kwargs,
        )
        return relationship, created

    def remove_relationship(
        self, area, classification, start_date, end_date, **kwargs
    ):
        """remove a relationtip to an area

        will raise an exception if no relationships or
        more than one are found

        :param area: destination area
        :param classification: the classification (rel label)
        :param start_date:
        :param end_date:
        :param kwargs: other relationships parameters
        :return:
        """
        r = AreaRelationship.objects.filter(
            source_area=self,
            dest_area=area,
            classification=classification,
            start_date=start_date,
            end_date=end_date,
            **kwargs
        )

        if r.count() > 1:
            raise Exception(_("More than one relationships found"))
        elif r.count() == 0:
            raise Exception(_("No relationships found"))
        else:
            r.delete()

    def get_relationships(self, classification):
        return self.from_relationships.filter(
            classification=classification
        ).select_related("source_area", "dest_area")

    def get_inverse_relationships(self, classification):
        return self.to_relationships.filter(
            classification=classification
        ).select_related("source_area", "dest_area")

    def get_former_parents(self, moment_date=None):
        """returns all parent relationtips valid at moment_date

        If moment_date is none, then returns all relationtips independently
        from their start and end dates

        :param moment_date: moment of validity, as YYYY-MM-DD
        :return: AreaRelationship queryset,
            with source_area and dest_area pre-selected
        """
        rels = self.get_relationships(
            AreaRelationship.CLASSIFICATION_TYPES.former_istat_parent
        ).order_by("-end_date")

        if moment_date is not None:
            rels = rels.filter(
                Q(start_date__lt=moment_date) | Q(start_date__isnull=True)
            ).filter(Q(end_date__gt=moment_date) | Q(end_date__isnull=True))

        return rels

    def get_former_children(self, moment_date=None):
        """returns all children relationtips valid at moment_date

        If moment_date is none, then returns all relationtips independently
        from their start and end dates

        :param moment_date: moment of validity, as YYYY-MM-DD
        :return: AreaRelationship queryset,
            with source_area and dest_area pre-selected
        """
        rels = self.get_inverse_relationships(
            AreaRelationship.CLASSIFICATION_TYPES.former_istat_parent
        ).order_by("-end_date")

        if moment_date is not None:
            rels = rels.filter(
                Q(start_date__lt=moment_date) | Q(start_date__isnull=True)
            ).filter(Q(end_date__gt=moment_date) | Q(end_date__isnull=True))

        return rels

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class OtherName(Dateframeable, GenericRelatable, models.Model):
    """
    An alternate or former name
    see schema at http://popoloproject.com/schemas/name-component.json#
    """

    name = models.CharField(
        _("name"), max_length=512, help_text=_("An alternate or former name")
    )

    NAME_TYPES = Choices(
        ("FOR", "former", _("Former name")),
        ("ALT", "alternate", _("Alternate name")),
        ("AKA", "aka", _("Also Known As")),
        ("NIC", "nickname", _("Nickname")),
        ("ACR", "acronym", _("Acronym")),
    )
    othername_type = models.CharField(
        _("scheme"),
        max_length=3,
        default="ALT",
        choices=NAME_TYPES,
        help_text=_(
            "Type of other name, e.g. FOR: former, ALT: alternate, ..."
        ),
    )

    note = models.CharField(
        _("note"),
        max_length=1024,
        blank=True,
        null=True,
        help_text=_("An extended note, e.g. 'Birth name used before marrige'"),
    )

    source = models.URLField(
        _("source"),
        max_length=256,
        blank=True,
        null=True,
        help_text=_("The URL of the source where this information comes from"),
    )

    class Meta:
        verbose_name = _("Other name")
        verbose_name_plural = _("Other names")

    try:
        # PassTrhroughManager was removed in django-model-utils 2.4,
        # see issue #22
        objects = PassThroughManager.for_queryset_class(OtherNameQuerySet)()
    except:
        objects = OtherNameQuerySet.as_manager()

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Identifier(Dateframeable, GenericRelatable, models.Model):
    """
    An issued identifier
    see schema at http://popoloproject.com/schemas/identifier.json#
    """

    identifier = models.CharField(
        _("identifier"),
        max_length=512,
        help_text=_("An issued identifier, e.g. a DUNS number"),
    )

    scheme = models.CharField(
        _("scheme"),
        max_length=128,
        blank=True,
        help_text=_("An identifier scheme, e.g. DUNS"),
    )

    source = models.URLField(
        _("source"),
        max_length=256,
        blank=True,
        null=True,
        help_text=_("The URL of the source where this information comes from"),
    )

    class Meta:
        verbose_name = _("Identifier")
        verbose_name_plural = _("Identifiers")
        indexes = [Index(fields=["identifier"])]

    try:
        # PassTrhroughManager was removed in django-model-utils 2.4,
        # see issue #22
        objects = PassThroughManager.for_queryset_class(IdentifierQuerySet)()
    except:
        objects = IdentifierQuerySet.as_manager()

    def __str__(self):
        return "{0}: {1}".format(self.scheme, self.identifier)


@python_2_unicode_compatible
class Classification(SourceShortcutsMixin, Dateframeable, models.Model):
    """
    A generic, hierarchical classification usable in different contexts
    """

    scheme = models.CharField(
        _("scheme"),
        max_length=128,
        blank=True,
        help_text=_("A classification scheme, e.g. ATECO, or FORMA_GIURIDICA"),
    )

    code = models.CharField(
        _("code"),
        max_length=128,
        blank=True,
        null=True,
        help_text=_("An alphanumerical code in use within the scheme"),
    )

    descr = models.CharField(
        _("description"),
        max_length=512,
        blank=True,
        null=True,
        help_text=_("The extended, textual description of the classification"),
    )

    sources = GenericRelation(
        "SourceRel",
        help_text=_("URLs to source documents about the classification"),
    )

    # reference to "http://popoloproject.com/schemas/area.json#"
    parent = models.ForeignKey(
        "Classification",
        blank=True,
        null=True,
        related_name="children",
        help_text=_("The parent classification."),
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("Classification")
        verbose_name_plural = _("Classifications")
        unique_together = ("scheme", "code", "descr")

    try:
        # PassTrhroughManager was removed in django-model-utils 2.4,
        # see issue #22
        objects = PassThroughManager.for_queryset_class(
            ClassificationQuerySet
        )()
    except:
        objects = ClassificationQuerySet.as_manager()

    def __str__(self):
        return "{0}: {1} - {2}".format(self.scheme, self.code, self.descr)


@python_2_unicode_compatible
class Link(models.Model):
    """
    A URL
    see schema at http://popoloproject.com/schemas/link.json#
    """

    url = models.URLField(_("url"), max_length=350, help_text=_("A URL"))

    note = models.CharField(
        _("note"),
        max_length=512,
        blank=True,
        help_text=_("A note, e.g. 'Wikipedia page'"),
    )

    class Meta:
        verbose_name = _("Link")
        verbose_name_plural = _("Links")

    def __str__(self):
        return self.url


@python_2_unicode_compatible
class Source(models.Model):
    """
    A URL for referring to sources of information
    see schema at http://popoloproject.com/schemas/link.json#
    """

    url = models.URLField(_("url"), max_length=350, help_text=_("A URL"))

    note = models.CharField(
        _("note"),
        max_length=512,
        blank=True,
        help_text=_("A note, e.g. 'Parliament website'"),
    )

    class Meta:
        verbose_name = _("Source")
        verbose_name_plural = _("Sources")

    def __str__(self):
        return self.url


@python_2_unicode_compatible
class Event(Timestampable, SourceShortcutsMixin, models.Model):
    """An occurrence that people may attend

    """

    name = models.CharField(
        _("name"), max_length=128, help_text=_("The event's name")
    )

    description = models.CharField(
        _("description"),
        max_length=512,
        blank=True,
        null=True,
        help_text=_("The event's description"),
    )

    # start_date and end_date are kept instead of the fields
    # provided by DateFrameable mixin,
    # starting and finishing *timestamps* for the Event are tracked
    # while fields in Dateframeable track the validity *dates* of the data
    start_date = models.CharField(
        _("start date"),
        max_length=20,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex="^[0-9]{4}("
                "(-[0-9]{2}){0,2}|(-[0-9]{2}){2}"
                "T[0-9]{2}(:[0-9]{2}){0,2}"
                "(Z|[+-][0-9]{2}(:[0-9]{2})?"
                ")"
                ")$",
                message="start date must follow the given pattern: "
                "^[0-9]{4}("
                "(-[0-9]{2}){0,2}|(-[0-9]{2}){2}"
                "T[0-9]{2}(:[0-9]{2}){0,2}"
                "(Z|[+-][0-9]{2}(:[0-9]{2})?"
                ")"
                ")$",
                code="invalid_start_date",
            )
        ],
        help_text=_("The time at which the event starts"),
    )
    end_date = models.CharField(
        _("end date"),
        max_length=20,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex="^[0-9]{4}("
                "(-[0-9]{2}){0,2}|(-[0-9]{2}){2}"
                "T[0-9]{2}(:[0-9]{2}){0,2}"
                "(Z|[+-][0-9]{2}(:[0-9]{2})?"
                ")"
                ")$",
                message="end date must follow the given pattern: "
                "^[0-9]{4}("
                "(-[0-9]{2}){0,2}|(-[0-9]{2}){2}"
                "T[0-9]{2}(:[0-9]{2}){0,2}"
                "(Z|[+-][0-9]{2}(:[0-9]{2})?"
                ")"
                ")$",
                code="invalid_end_date",
            )
        ],
        help_text=_("The time at which the event ends"),
    )

    # textual full address of the event
    location = models.CharField(
        _("location"),
        max_length=255,
        blank=True,
        null=True,
        help_text=_("The event's location"),
    )
    # reference to "http://popoloproject.com/schemas/area.json#"
    area = models.ForeignKey(
        "Area",
        blank=True,
        null=True,
        related_name="events",
        help_text=_("The Area the Event is related to"),
        on_delete=models.CASCADE,
    )

    status = models.CharField(
        _("status"),
        max_length=128,
        blank=True,
        null=True,
        help_text=_("The event's status"),
    )

    # add 'identifiers' property to get array of items referencing 'http://www.popoloproject.com/schemas/identifier.json#'
    identifiers = GenericRelation(
        "Identifier",
        blank=True,
        null=True,
        help_text=_("Issued identifiers for this event"),
    )

    classification = models.CharField(
        _("classification"),
        max_length=128,
        blank=True,
        null=True,
        help_text=_("The event's category"),
    )

    # reference to 'http://www.popoloproject.com/schemas/organization.json#'
    organization = models.ForeignKey(
        "Organization",
        blank=True,
        null=True,
        related_name="events",
        help_text=_("The organization organizing the event"),
        on_delete=models.CASCADE,
    )

    # array of items referencing 'http://www.popoloproject.com/schemas/person.json#'
    attendees = models.ManyToManyField(
        "Person",
        blank=True,
        related_name="attended_events",
        help_text=_("People attending the event"),
    )

    # reference to 'http://www.popoloproject.com/schemas/event.json#'
    parent = models.ForeignKey(
        "Event",
        blank=True,
        null=True,
        related_name="children",
        verbose_name=_("Parent"),
        help_text=_("The Event that this event is part of"),
        on_delete=models.CASCADE,
    )

    # array of items referencing
    # 'http://www.popoloproject.com/schemas/source.json#'
    sources = GenericRelation(
        "SourceRel", help_text=_("URLs to source documents about the event")
    )

    def __str__(self):
        return "{0} - {1}".format(self.name, self.start_date)

    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")
        unique_together = ("name", "start_date")
