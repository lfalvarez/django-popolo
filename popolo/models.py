from autoslug import AutoSlugField
from autoslug.utils import slugify
from django.contrib.contenttypes.models import ContentType

try:
    from django.contrib.contenttypes.fields import GenericRelation, \
    GenericForeignKey
except ImportError:
    # This fallback import is the version that was deprecated in
    # Django 1.7 and is removed in 1.9:
    from django.contrib.contenttypes.generic import GenericRelation, \
    GenericForeignKey

try:
    # PassTrhroughManager was removed in django-model-utils 2.4
    # see issue #22 at https://github.com/openpolis/django-popolo/issues/22
    from model_utils.managers import PassThroughManager
except ImportError:
    pass

from django.core.validators import RegexValidator
from django.db import models
from model_utils import Choices
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import pre_save
from django.dispatch import receiver

from .behaviors.models import (
    Permalinkable, Timestampable, Dateframeable,
    GenericRelatable, get_slug_source
)
from .querysets import (
    PostQuerySet, OtherNameQuerySet, ContactDetailQuerySet,
    MembershipQuerySet, OrganizationQuerySet, PersonQuerySet
)


@python_2_unicode_compatible
class Person(Dateframeable, Timestampable, Permalinkable, models.Model):
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
        help_text=_("A person's preferred full name")
    )

    # array of items referencing
    # "http://popoloproject.com/schemas/other_name.json#"
    other_names = GenericRelation(
        'OtherName',
        help_text=_("Alternate or former names")
    )

    # array of items referencing
    # "http://popoloproject.com/schemas/identifier.json#"
    identifiers = GenericRelation(
        'Identifier',
        help_text=_("Issued identifiers")
    )

    family_name = models.CharField(
        _("family name"),
        max_length=128, blank=True, null=True,
        help_text=_("One or more family names")
    )

    given_name = models.CharField(
        _("given name"),
        max_length=128, blank=True, null=True,
        help_text=_("One or more primary given names")
    )

    additional_name = models.CharField(
        _("additional name"),
        max_length=128, blank=True, null=True,
        help_text=_("One or more secondary given names")
    )

    honorific_prefix = models.CharField(
        _("honorific prefix"),
        max_length=32, blank=True, null=True,
        help_text=_("One or more honorifics preceding a person's name")
    )

    honorific_suffix = models.CharField(
        _("honorific suffix"),
        max_length=32, blank=True, null=True,
        help_text=_("One or more honorifics following a person's name")
    )

    patronymic_name = models.CharField(
        _("patronymic name"),
        max_length=128, blank=True, null=True,
        help_text=_("One or more patronymic names")
    )

    sort_name = models.CharField(
        _("sort name"),
        max_length=128, blank=True, null=True,
        help_text=_(
            "A name to use in an lexicographically "
            "ordered list"
        )
    )

    email = models.EmailField(
        _("email"),
        blank=True, null=True,
        help_text=_("A preferred email address")
    )

    gender = models.CharField(
        _('gender'),
        max_length=32, blank=True,
        help_text=_("A gender")
    )

    birth_date = models.CharField(
        _("birth date"),
        max_length=10, blank=True, null=True,
        help_text=_("A date of birth")
    )

    death_date = models.CharField(
        _("death date"),
        max_length=10, blank=True, null=True,
        help_text=_("A date of death")
    )

    image = models.URLField(
        _("image"),
        blank=True, null=True,
        help_text=_("A URL of a head shot")
    )

    summary = models.CharField(
        _("summary"),
        max_length=1024, blank=True, null=True,
        help_text=_("A one-line account of a person's life")
    )

    biography = models.TextField(
        _("biography"),
        blank=True, null=True,
        help_text=_(
            "An extended account of a person's life"
        )
    )

    national_identity = models.CharField(
        _("national identity"),
        max_length=128, blank=True, null=True,
        help_text=_("A national identity")
    )

    # array of items referencing
    # "http://popoloproject.com/schemas/contact_detail.json#"
    contact_details = GenericRelation(
        'ContactDetail',
        help_text="Means of contacting the person"
    )

    # array of items referencing "http://popoloproject.com/schemas/link.json#"
    links = GenericRelation(
        'Link',
        help_text="URLs to documents related to the person"
    )

    # array of items referencing "http://popoloproject.com/schemas/link.json#"
    sources = GenericRelation(
        'Source',
        help_text="URLs to source documents about the person"
    )

    url_name = 'person-detail'

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
        """Add membership to Organization for member

        :param organization: Organization instance
        :param kwargs: start_date|end_date
        :return: added Membership
        """
        m = Membership(person=self, organization=organization)
        if 'start_date' in kwargs:
            m.start_date = kwargs['start_date']
        if 'end_date' in kwargs:
            m.end_date = kwargs['end_date']

        m.save()

        return m

    def add_memberships(self, organizations):
        for o in organizations:
            self.add_membership(o)

    def organizations_is_member_of(self):
        """get all organizations the person is member of

        :return: List of Organizations
        """
        return Organization.objects.filter(memberships__person=self)

    def add_role(self, post):
        """add a role (post) in an Organization

        A *role* is identified by the Membership to a given Post in an
        Organization.

        :param post: the post fullfilled
        :return: the Membership to rhe role
        """
        m = Membership(person=self, post=post, organization=post.organization)
        m.save()

        return m

    def add_role_on_behalf_of(self, post, organization):
        """add a role (post) in an Organization on behhalf of the given
        Organization

        :param post: the post fullfilled
        :param organiazione: the organization on behalf of which the Post
        is fullfilled
        :return: the Membership to rhe role
        """
        m = Membership(
            person=self,
            post=post, organization=post.organization,
            on_behalf_of=organization
        )
        m.save()

        return m

    def organizations_has_role_in(self):
        """get all organizations the person has a role in

        :return:
        """
        return Organization.objects.filter(
            posts__in=Post.objects.filter(memberships__person=self)
        )


    def add_contact_detail(self, **kwargs):
        c = ContactDetail(content_object=self, **kwargs)
        c.save()
        return c

    def add_contact_details(self, contacts):
        for c in contacts:
            self.add_contact_detail(**c)

    def add_other_name(self, **kwargs):
        n = OtherName(content_object=self, **kwargs)
        n.save()
        return n

    def add_other_names(self, names):
        for n in names:
            self.add_other_name(**n)

    def add_identifier(self, **kwargs):
        i = Identifier(content_object=self, **kwargs)
        i.save()
        return i

    def add_identifiers(self, identifiers):
        for i in identifiers:
            self.add_identifier(**i)

    def add_link(self, **kwargs):
        l = Link(content_object=self, **kwargs)
        l.save()
        return l

    def add_links(self, links):
        for l in links:
            self.add_link(**l)

    def add_source(self, **kwargs):
        s = Source(content_object=self, **kwargs)
        s.save()
        return s

    def add_sources(self, sources):
        for s in sources:
            self.add_source(**s)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Organization(Dateframeable, Timestampable, Permalinkable, models.Model):
    """
    A group with a common purpose or reason for existence that goes beyond
    the set of people belonging to it
    see schema at http://popoloproject.com/schemas/organization.json#
    """

    @property
    def slug_source(self):
        return self.name

    name = models.CharField(
        _("name"),
        max_length=128,
        help_text=_("A primary name, e.g. a legally recognized name")
    )

    # array of items referencing
    # "http://popoloproject.com/schemas/other_name.json#"
    other_names = GenericRelation(
        'OtherName',
        help_text=_("Alternate or former names")
    )

    # array of items referencing
    # "http://popoloproject.com/schemas/identifier.json#"
    identifiers = GenericRelation(
        'Identifier', help_text=_("Issued identifiers")
    )

    classification = models.CharField(
        _("classification"),
        max_length=64, blank=True, null=True,
        help_text=_("An organization category, e.g. committee")
    )

    # reference to "http://popoloproject.com/schemas/organization.json#"
    parent = models.ForeignKey(
        'Organization',
        blank=True, null=True,
        related_name='children',
        verbose_name=_("Parent"),
        help_text=_(
           "The organization that contains this "
           "organization"
        )
    )

    # reference to "http://popoloproject.com/schemas/area.json#"
    area = models.ForeignKey(
        'Area',
        blank=True, null=True,
        related_name='organizations',
        help_text=_(
            "The geographic area to which this "
            "organization is related")
        )

    abstract = models.CharField(
        _("abstract"),
        max_length=256, blank=True, null=True,
        help_text=_("A one-line description of an organization")
    )

    description = models.TextField(
        _("biography"),
        blank=True, null=True,
        help_text=_("An extended description of an organization")
    )

    founding_date = models.CharField(
        _("founding date"),
        max_length=10,
        null=True, blank=True,
        validators=[
            RegexValidator(
                regex='^[0-9]{4}(-[0-9]{2}){0,2}$',
                message='founding date must follow the given pattern: ^[0-9]{'
                '4}(-[0-9]{2}){0,2}$',
                code='invalid_founding_date'
            )
        ],
        help_text=_("A date of founding")
    )

    dissolution_date = models.CharField(
        _("dissolution date"),
        max_length=10,
        null=True, blank=True,
        validators=[
            RegexValidator(
                regex='^[0-9]{4}(-[0-9]{2}){0,2}$',
                message='dissolution date must follow the given pattern: ^['
                '0-9]{4}(-[0-9]{2}){0,2}$',
                code='invalid_dissolution_date'
            )
        ],
        help_text=_("A date of dissolution")
    )

    image = models.URLField(
        _("image"),
        max_length=255,
        blank=True, null=True,
        help_text=_(
            "A URL of an image, to identify the organization visually"
        )
    )

    # array of items referencing
    # "http://popoloproject.com/schemas/contact_detail.json#"
    contact_details = GenericRelation(
        'ContactDetail',
        help_text=_("Means of contacting the organization")

    )

    # array of items referencing "http://popoloproject.com/schemas/link.json#"
    links = GenericRelation(
        'Link',
        help_text=_("URLs to documents about the organization")
    )

    # array of items referencing "http://popoloproject.com/schemas/link.json#"
    sources = GenericRelation(
        'Source',
        help_text=_("URLs to source documents about the organization")
    )

    url_name = 'organization-detail'

    class Meta:
        verbose_name = _("Organization")
        verbose_name_plural = _("Organizations")

    try:
        # PassTrhroughManager was removed in django-model-utils 2.4,
        # see issue #22
        objects = PassThroughManager.for_queryset_class(OrganizationQuerySet)()
    except:
        objects = OrganizationQuerySet.as_manager()

    def add_member(self, member):
        """add a member to this organization

        :param member: a Person or an Organization
        :return: the added member (be it Person or Organization)
        """
        if isinstance(member, Person):
            m = Membership(organization=self, person=member)
        elif isinstance(member, Organization):
            m = Membership(organization=self, member_organization=member)
        else:
            raise Exception(_(
                "Member must be Person or Organization"
            ))
        m.save()
        return m


    def add_members(self, members):
        """add multiple members to this organization

        :param members: list of Person/Organization to be added as members
        :return:
        """
        for m in members:
            self.add_member(m)

    def add_membership(self, organization):
        """add this organization as member to the given `organization`

        :param organization: the organization this one will be a member of
        :return: the added Membership
        """
        m = Membership(organization=organization, member_organization=self)
        m.save()
        return m

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

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Post(Dateframeable, Timestampable, Permalinkable, models.Model):
    """
    A position that exists independent of the person holding it
    see schema at http://popoloproject.com/schemas/json#
    """

    @property
    def slug_source(self):
        return self.label

    label = models.CharField(
        _("label"),
        max_length=256, blank=True,
        help_text=_("A label describing the post")
    )

    other_label = models.CharField(
        _("other label"),
        max_length=32, blank=True, null=True,
        help_text=_(
            "An alternate label, such as an abbreviation"
        )
    )

    role = models.CharField(
        _("role"),
        max_length=256, blank=True, null=True,
        help_text=_(
            "The function that the holder of the post fulfills"
        )
    )

    # reference to "http://popoloproject.com/schemas/organization.json#"
    organization = models.ForeignKey(
        'Organization',
        related_name='posts',
        verbose_name=_("Organization"),
        help_text=_("The organization in which the post is held")
    )

    # reference to "http://popoloproject.com/schemas/area.json#"
    area = models.ForeignKey(
        'Area',
        blank=True, null=True,
        related_name='posts',
        verbose_name=_("Area"),
        help_text=_("The geographic area to which the post is related")
    )

    # array of items referencing
    # "http://popoloproject.com/schemas/contact_detail.json#"
    contact_details = GenericRelation(
        'ContactDetail',
        help_text=_("Means of contacting the holder of the post")
    )

    # array of items referencing "http://popoloproject.com/schemas/link.json#"
    links = GenericRelation(
        'Link',
        help_text=_("URLs to documents about the post")
    )

    # array of items referencing "http://popoloproject.com/schemas/link.json#"
    sources = GenericRelation(
        'Source',
        help_text=_("URLs to source documents about the post")
    )

    url_name = 'post-detail'

    class Meta:
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")

    try:
        # PassTrhroughManager was removed in django-model-utils 2.4,
        # see issue #22
        objects = PassThroughManager.for_queryset_class(PostQuerySet)()
    except:
        objects = PostQuerySet.as_manager()

    def add_person(self, person):
        """add given person to this post (through membership)
        A person having a post is also an explicit member
        of the organization holding the post.

        :param person:
        :return:
        """
        m = Membership(
            post=self, person=person, organization=self.organization
        )
        m.save()

    def add_person_on_behalf_of(self, person, organization):
        """add given `person` to this post (through a membership)
        on behalf of given `organization`

        :param person:
        :param organization: the organization on behalf the post is taken
        :return:
        """
        m = Membership(
            post=self,
            person=person, organization=self.organization,
            on_behalf_of=organization
        )
        m.save()

    def __str__(self):
        return self.label


@python_2_unicode_compatible
class Membership(Dateframeable, Timestampable, Permalinkable, models.Model):
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
        max_length=256, blank=True, null=True,
        help_text=_("A label describing the membership")
    )

    role = models.CharField(
        _("role"),
        max_length=256, blank=True, null=True,
        help_text=_("The role that the member fulfills in the organization")
    )

    # person or organization that is a member of the organization
    member_organization = models.ForeignKey(
        'Organization',
        blank=True, null=True,
        related_name='memberships_as_member',
        verbose_name=_("Person"),
        help_text=_("The person who is a member of the organization")
    )

    # reference to "http://popoloproject.com/schemas/person.json#"
    person = models.ForeignKey(
        'Person',
        blank=True, null=True,
        related_name='memberships',
        verbose_name=_("Person"),
        help_text=_("The person who is a member of the organization")
    )

    @property
    def member(self):
        if self.member_organization:
            return self.member_organization
        else:
            return self.person

    # reference to "http://popoloproject.com/schemas/organization.json#"
    organization = models.ForeignKey(
        'Organization',
        blank=True, null=True,
        related_name='memberships',
        verbose_name=_("Organization"),
        help_text=_(
             "The organization in which the person or organization is a member"
         )
     )

    on_behalf_of = models.ForeignKey(
        'Organization',
        blank=True, null=True,
        related_name='memberships_on_behalf_of',
        verbose_name=_("On behalf of"),
        help_text=_(
            "The organization on whose behalf the person "
            "is a member of the organization"
        )
    )

    # reference to "http://popoloproject.com/schemas/post.json#"
    post = models.ForeignKey(
        'Post',
        blank=True, null=True,
        related_name='memberships',
        verbose_name=_("Post"),
        help_text=_(
            "The post held by the person in the "
            "organization through this membership"
        )
    )

    # reference to "http://popoloproject.com/schemas/area.json#"
    area = models.ForeignKey(
        'Area',
        blank=True, null=True,
        related_name='memberships',
        verbose_name=_("Area"),
        help_text=_("The geographic area to which the post is related")
    )

    # array of items referencing
    # "http://popoloproject.com/schemas/contact_detail.json#"
    contact_details = GenericRelation(
        'ContactDetail',
        help_text=_("Means of contacting the member of the organization")
    )

    # array of items referencing "http://popoloproject.com/schemas/link.json#"
    links = GenericRelation(
        'Link',
        help_text=_("URLs to documents about the membership")
    )

    # array of items referencing "http://popoloproject.com/schemas/link.json#"
    sources = GenericRelation(
        'Source',
        help_text=_("URLs to source documents about the membership")
    )

    url_name = 'membership-detail'

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
                getattr(self.member, 'name'),
                self.label,
                self.organization
            )
        else:
            return "{0} -[member of]> {1}".format(
                getattr(self.member, 'name'),
                self.organization
            )


@python_2_unicode_compatible
class ContactDetail(Timestampable, Dateframeable, GenericRelatable,
                    models.Model):
    """
    A means of contacting an entity
    see schema at http://popoloproject.com/schemas/contact-detail.json#
    """

    CONTACT_TYPES = Choices(
        ('ADDRESS', 'address', _('Address')),
        ('EMAIL', 'email', _('Email')),
        ('URL', 'url', _('Url')),
        ('MAIL', 'mail', _('Snail mail')),
        ('TWITTER', 'twitter', _('Twitter')),
        ('FACEBOOK', 'facebook', _('Facebook')),
        ('PHONE', 'phone', _('Telephone')),
        ('MOBILE', 'mobile', _('Mobile')),
        ('TEXT', 'text', _('Text')),
        ('VOICE', 'voice', _('Voice')),
        ('FAX', 'fax', _('Fax')),
        ('CELL', 'cell', _('Cell')),
        ('VIDEO', 'video', _('Video')),
        ('PAGER', 'pager', _('Pager')),
        ('TEXTPHONE', 'textphone', _('Textphone')),
    )

    label = models.CharField(
        _("label"),
        max_length=256, blank=True,
        help_text=_("A human-readable label for the contact detail")
    )

    contact_type = models.CharField(
        _("type"),
        max_length=12,
        choices=CONTACT_TYPES,
        help_text=_("A type of medium, e.g. 'fax' or 'email'")
    )

    value = models.CharField(
        _("value"),
        max_length=256,
        help_text=_("A value, e.g. a phone number or email address")
    )

    note = models.CharField(
        _("note"),
        max_length=512, blank=True,
        help_text=_(
            "A note, e.g. for grouping contact details by physical location"
        )
    )

    # array of items referencing "http://popoloproject.com/schemas/link.json#"
    sources = GenericRelation(
        'Source',
        help_text=_("URLs to source documents about the contact detail")
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
class OtherName(Dateframeable, GenericRelatable, models.Model):
    """
    An alternate or former name
    see schema at http://popoloproject.com/schemas/name-component.json#
    """
    name = models.CharField(
        _("name"),
        max_length=512,
        help_text=_("An alternate or former name")
    )

    note = models.CharField(
        _("note"),
        max_length=1024, blank=True, null=True,
        help_text=_("A note, e.g. 'Birth name'")
    )

    source = models.URLField(
        _("source"),
        max_length=256, blank=True, null=True,
        help_text=_("The URL of the source where this information comes from")
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
        help_text=_("An issued identifier, e.g. a DUNS number")
    )

    scheme = models.CharField(
        _("scheme"),
        max_length=128, blank=True,
        help_text=_("An identifier scheme, e.g. DUNS")
    )

    source = models.URLField(
        _("source"),
        max_length=256, blank=True, null=True,
        help_text=_("The URL of the source where this information comes from")
    )

    class Meta:
        verbose_name = _("Identifier")
        verbose_name_plural = _("Identifiers")

    def __str__(self):
        return "{0}: {1}".format(self.scheme, self.identifier)


@python_2_unicode_compatible
class Link(GenericRelatable, models.Model):
    """
    A URL
    see schema at http://popoloproject.com/schemas/link.json#
    """
    url = models.URLField(
        _("url"),
        max_length=350,
        help_text=_("A URL")
    )

    note = models.CharField(
        _("note"),
        max_length=512, blank=True,
        help_text=_("A note, e.g. 'Wikipedia page'")
    )

    class Meta:
        verbose_name = _("Link")
        verbose_name_plural = _("Links")

    def __str__(self):
        return self.url


@python_2_unicode_compatible
class Source(GenericRelatable, models.Model):
    """
    A URL for referring to sources of information
    see schema at http://popoloproject.com/schemas/link.json#
    """
    url = models.URLField(
        _("url"),
        max_length=350,
        help_text=_("A URL")
    )

    note = models.CharField(
        _("note"),
        max_length=512, blank=True,
        help_text=_("A note, e.g. 'Parliament website'")
    )

    class Meta:
        verbose_name = _("Source")
        verbose_name_plural = _("Sources")

    def __str__(self):
        return self.url


@python_2_unicode_compatible
class Language(models.Model):
    """
    Maps languages, with names and 2-char iso 639-1 codes.
    Taken from http://dbpedia.org, using a sparql query
    """
    dbpedia_resource = models.CharField(
        _("dbpedia resource"),
        max_length=255,
        help_text=_("DbPedia URI of the resource"),
        unique=True
    )
    iso639_1_code = models.CharField(
        _("iso639_1 code"),
        max_length=2,
        help_text=_("ISO 639_1 code, ex: en, it, de, fr, es, ..."),
    )
    name = models.CharField(
        _("name"),
        max_length=128,
        help_text=_("English name of the language")
    )

    class Meta:
        verbose_name = _("Language")
        verbose_name_plural = _("Languages")

    def __str__(self):
        return u"{0} ({1})".format(self.name, self.iso639_1_code)


@python_2_unicode_compatible
class Area(Permalinkable, GenericRelatable,
    Dateframeable, Timestampable, models.Model):
    """
    An area is a geographic area whose geometry may change over time.
    see schema at http://popoloproject.com/schemas/area.json#
    """
    @property
    def slug_source(self):
        return u"{0} {1} {2}".format(
            self.name, self.classification, self.identifier
        )

    name = models.CharField(
        _("name"),
        max_length=256, blank=True,
        help_text=_("A primary name")
    )

    identifier = models.CharField(
        _("identifier"),
        max_length=128, blank=True,
        help_text=_("An issued identifier")
    )

    classification = models.CharField(
        _("classification"),
        max_length=128, blank=True,
        help_text=_("An area category, e.g. city")
    )

    # array of items referencing
    # "http://popoloproject.com/schemas/identifier.json#"
    other_identifiers = GenericRelation(
        'Identifier',
        blank=True, null=True,
        help_text=_(
            "Other issued identifiers (zip code, other useful codes, ...)"
        )
    )

    # reference to "http://popoloproject.com/schemas/area.json#"
    parent = models.ForeignKey(
        'Area',
        blank=True, null=True,
        related_name='children',
        verbose_name=_('Parent'),
        help_text=_("The area that contains this area")
    )

    # geom property, as text (GeoJson, KML, GML)
    geom = models.TextField(
        _("geom"),
        null=True, blank=True,
        help_text=_("A geometry")
    )

    # inhabitants, can be useful for some queries
    inhabitants = models.IntegerField(
        _("inhabitants"),
        null=True, blank=True,
        help_text=_("The total number of inhabitants")
    )

    # array of items referencing "http://popoloproject.com/schemas/link.json#"
    sources = GenericRelation(
        'Source',
        blank=True, null=True,
        help_text=_("URLs to source documents about the contact detail")
    )

    class Meta:
        verbose_name = _("Geographic Area")
        verbose_name_plural = _("Geographic Areas")

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class AreaI18Name(models.Model):
    """
    Internationalized name for an Area.
    Contains references to language and area.
    """
    area = models.ForeignKey(
        'Area',
        related_name='i18n_names'
    )

    language = models.ForeignKey(
        'Language',
        verbose_name=_('Language')
    )

    name = models.CharField(
        _("name"),
        max_length=255
    )


    def __str__(self):
        return "{0} - {1}".format(self.language, self.name)

    class Meta:
        verbose_name = _('I18N Name')
        verbose_name_plural = _('I18N Names')
        unique_together = ('area', 'language', 'name')


@python_2_unicode_compatible
class Event(Timestampable, models.Model):
    """An occurrence that people may attend

    """

    name = models.CharField(
        _("name"),
        max_length=128,
        help_text=_("The event's name")
    )

    description = models.CharField(
        _("description"),
        max_length=512, blank=True, null=True,
        help_text=_("The event's description")
    )

    # start_date and end_date are kept instead of the fields
    # provided by DateFrameable mixin,
    # starting and finishing *timestamps* for the Event are tracked
    # wjile fields in Dateframeable track the validity *dates* of the data
    start_date = models.CharField(
        _("start date"),
        max_length=20, blank=True, null=True,
        validators=[
            RegexValidator(
                regex='^[0-9]{4}('
                    '(-[0-9]{2}){0,2}|(-[0-9]{2}){2}'
                        'T[0-9]{2}(:[0-9]{2}){0,2}'
                        '(Z|[+-][0-9]{2}(:[0-9]{2})?'
                    ')'
                ')$',
                message='start date must follow the given pattern: '
                    '^[0-9]{4}('
                        '(-[0-9]{2}){0,2}|(-[0-9]{2}){2}'
                        'T[0-9]{2}(:[0-9]{2}){0,2}'
                        '(Z|[+-][0-9]{2}(:[0-9]{2})?'
                    ')'
                ')$',
                code='invalid_start_date'
            )
        ],
        help_text=_("The time at which the event starts")
    )
    end_date = models.CharField(
        _("end date"),
        max_length=20, blank=True, null=True,
        validators=[
            RegexValidator(
                regex='^[0-9]{4}('
                    '(-[0-9]{2}){0,2}|(-[0-9]{2}){2}'
                        'T[0-9]{2}(:[0-9]{2}){0,2}'
                        '(Z|[+-][0-9]{2}(:[0-9]{2})?'
                    ')'
                ')$',
                message='end date must follow the given pattern: '
                    '^[0-9]{4}('
                        '(-[0-9]{2}){0,2}|(-[0-9]{2}){2}'
                        'T[0-9]{2}(:[0-9]{2}){0,2}'
                        '(Z|[+-][0-9]{2}(:[0-9]{2})?'
                    ')'
                ')$',
                code='invalid_end_date'
            )
        ],
        help_text=_("The time at which the event ends")
    )

    # textual full address of the event
    location = models.CharField(
        _("location"),
        max_length=255, blank=True, null=True,
        help_text=_("The event's location")
    )
    # reference to "http://popoloproject.com/schemas/area.json#"
    area = models.ForeignKey(
        'Area',
        blank=True, null=True,
        related_name='events',
        help_text=_("The Area the Event is related to")
    )

    status = models.CharField(
        _("status"),
        max_length=128, blank=True, null=True,
        help_text=_("The event's status")
    )

    # add 'identifiers' property to get array of items referencing 'http://www.popoloproject.com/schemas/identifier.json#'
    identifiers = GenericRelation(
        'Identifier',
        blank=True, null=True,
        help_text=_("Issued identifiers for this event")
    )

    classification = models.CharField(
        _("classification"),
        max_length=128, blank=True, null=True,
        help_text=_("The event's category")
    )

    # reference to 'http://www.popoloproject.com/schemas/organization.json#'
    organization = models.ForeignKey(
        'Organization',
        blank=True, null=True,
        related_name='events',
        help_text=_("The organization organizing the event")
    )

    # array of items referencing 'http://www.popoloproject.com/schemas/person.json#'
    attendees = models.ManyToManyField(
        'Person',
        blank=True,
        related_name='attended_events',
        help_text=_("People attending the event")
    )

    # reference to 'http://www.popoloproject.com/schemas/event.json#'
    parent = models.ForeignKey(
        'Event',
        blank=True, null=True,
        related_name='children',
        verbose_name=_('Parent'),
        help_text=_("The Event that this event is part of")
    )

    # array of items referencing 'http://www.popoloproject.com/schemas/link.json#'
    sources = GenericRelation(
        'Source',
        help_text=_("URLs to source documents about the organization")
    )

    def __str__(self):
        return "{0} - {1}".format(self.name, self.start_date)

    class Meta:
        verbose_name = _('Event')
        verbose_name_plural = _('Events')
        unique_together = ('name', 'start_date', 'name')


#
# signals
#

# copy founding and dissolution dates into start and end dates,
# so that Organization can extend the abstract Dateframeable behavior
# (it's way easier than dynamic field names)
@receiver(pre_save, sender=Organization)
def copy_organization_date_fields(sender, **kwargs):
    obj = kwargs['instance']

    if obj.founding_date:
        obj.start_date = obj.founding_date
    if obj.dissolution_date:
        obj.end_date = obj.dissolution_date


# copy birth and death dates into start and end dates,
# so that Person can extend the abstract Dateframeable behavior
# (it's way easier than dynamic field names)
@receiver(pre_save, sender=Person)
def copy_person_date_fields(sender, **kwargs):
    obj = kwargs['instance']

    if obj.birth_date:
        obj.start_date = obj.birth_date
    if obj.death_date:
        obj.end_date = obj.death_date


# all Dateframeable instances need to have dates properly sorted
@receiver(pre_save)
def verify_start_end_dates_order(sender, **kwargs):
    if not issubclass(sender, Dateframeable):
        return
    obj = kwargs['instance']
    if obj.start_date and obj.end_date and obj.start_date > obj.end_date:
        raise Exception(_(
            "Initial date must precede end date"
        ))


# all instances are validated before being saved
@receiver(pre_save, sender=Person)
@receiver(pre_save, sender=Organization)
@receiver(pre_save, sender=Post)
def validate_date_fields(sender, **kwargs):
    obj = kwargs['instance']
    obj.full_clean()


