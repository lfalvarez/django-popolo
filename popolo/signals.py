# -*- coding: utf-8 -*-
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from popolo.behaviors.models import Dateframeable
from popolo.models import (
    Organization,
    Person,
    Membership,
    Ownership,
    Post,
    ElectoralResult,
    Area,
    OriginalEducationLevel,
    KeyEvent,
)


# copy founding and dissolution dates into start and end dates,
# so that Organization can extend the abstract Dateframeable behavior
# (it's way easier than dynamic field names)
@receiver(pre_save, sender=Organization)
def copy_organization_date_fields(sender, **kwargs):
    obj = kwargs["instance"]

    if obj.founding_date:
        obj.start_date = obj.founding_date
    if obj.dissolution_date:
        obj.end_date = obj.dissolution_date


# copy birth and death dates into start and end dates,
# so that Person can extend the abstract Dateframeable behavior
# (it's way easier than dynamic field names)
@receiver(pre_save, sender=Person)
def copy_person_date_fields(sender, **kwargs):
    obj = kwargs["instance"]

    if obj.birth_date:
        obj.start_date = obj.birth_date
    if obj.death_date:
        obj.end_date = obj.death_date


# all Dateframeable instances need to have dates properly sorted
@receiver(pre_save)
def verify_start_end_dates_order(sender, **kwargs):
    if not issubclass(sender, Dateframeable):
        return
    obj = kwargs["instance"]
    if obj.start_date and obj.end_date and obj.start_date > obj.end_date:
        raise Exception(_("Initial date must precede end date"))


@receiver(pre_save, sender=Membership)
def verify_membership_has_org_and_member(sender, **kwargs):
    obj = kwargs["instance"]
    if obj.person is None and obj.member_organization is None:
        raise Exception(
            _(
                "A member, either a Person or an Organization, must be specified."
            )
        )
    if obj.organization is None:
        raise Exception(_("An Organization, must be specified."))


@receiver(pre_save, sender=Ownership)
def verify_ownership_has_org_and_owner(sender, **kwargs):
    obj = kwargs["instance"]
    if obj.owner_person is None and obj.owner_organization is None:
        raise Exception(
            _(
                "An owner, either a Person or an Organization, must be specified."
            )
        )


@receiver(post_save, sender=OriginalEducationLevel)
def update_education_levels(sender, **kwargs):
    """Updates persons education_level when the mapping between
    the original education_level and the normalized one is touched
    :param sender:
    :param kwargs:
    :return:
    """
    obj = kwargs["instance"]
    if obj.normalized_education_level:
        obj.persons_with_this_original_education_level.exclude(
            education_level=obj.normalized_education_level
        ).update(education_level=obj.normalized_education_level)


# all main instances are validated before being saved
@receiver(pre_save, sender=Person)
@receiver(pre_save, sender=Organization)
@receiver(pre_save, sender=Post)
@receiver(pre_save, sender=Membership)
@receiver(pre_save, sender=Ownership)
@receiver(pre_save, sender=KeyEvent)
@receiver(pre_save, sender=ElectoralResult)
@receiver(pre_save, sender=Area)
def validate_fields(sender, **kwargs):
    obj = kwargs["instance"]
    obj.full_clean()
