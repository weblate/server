from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey

from neatplus.models import TimeStampedModel, UserStampedModel


class Organization(MPTTModel, TimeStampedModel, UserStampedModel):
    class StatusChoice(models.TextChoices):
        PENDING = "pending"
        ACCEPTED = "accepted"
        REJECTED = "rejected"

    title = models.CharField(_("title"), max_length=255, unique=True)
    acronym = models.CharField(
        _("acronym"), max_length=50, null=True, blank=True, default=None
    )
    description = models.TextField(
        _("description"), null=True, blank=True, default=None
    )
    logo = models.ImageField(
        _("logo"),
        upload_to="organization/organization/logos",
        null=True,
        blank=True,
        default=None,
    )
    admins = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="admin_organizations",
        verbose_name=_("admins"),
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="member_organizations",
        blank=True,
        verbose_name=_("members"),
    )
    status = models.CharField(
        _("status"),
        max_length=8,
        choices=StatusChoice.choices,
        default=StatusChoice.PENDING,
        editable=False,
    )
    point_of_contact = models.TextField(
        _("point of contact"), null=True, blank=True, default=None
    )
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
        related_name="childerns",
        verbose_name=_("organization parent"),
    )

    class MPTTMeta:
        order_insertion_by = ["title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.pk:
            cls = self.__class__
            old = cls.objects.get(pk=self.pk)
            changed_fields = []
            for field in cls._meta.get_fields():
                field_name = field.name
                try:
                    old_val = getattr(old, field_name)
                    new_val = getattr(self, field_name)
                    if hasattr(field, "is_custom_lower_field"):
                        if field.is_custom_lower_field():
                            new_val = new_val.lower()
                    if old_val != new_val:
                        changed_fields.append(field_name)
                except Exception:
                    pass
            kwargs["update_fields"] = changed_fields
        super().save(*args, **kwargs)


class OrganizationMemberRequest(UserStampedModel, TimeStampedModel):
    class StatusChoice(models.TextChoices):
        PENDING = "pending"
        ACCEPTED = "accepted"
        REJECTED = "rejected"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="member_requests",
        verbose_name=_("user"),
    )
    organization = models.ForeignKey(
        "Organization",
        on_delete=models.CASCADE,
        related_name="member_requests",
        verbose_name=_("organization"),
    )
    status = models.CharField(
        _("status"),
        max_length=8,
        choices=StatusChoice.choices,
        default=StatusChoice.PENDING,
        editable=False,
    )

    def save(self, *args, **kwargs):
        if self.pk:
            cls = self.__class__
            old = cls.objects.get(pk=self.pk)
            changed_fields = []
            for field in cls._meta.get_fields():
                field_name = field.name
                try:
                    old_val = getattr(old, field_name)
                    new_val = getattr(self, field_name)
                    if hasattr(field, "is_custom_lower_field"):
                        if field.is_custom_lower_field():
                            new_val = new_val.lower()
                    if old_val != new_val:
                        changed_fields.append(field_name)
                except Exception:
                    pass
            kwargs["update_fields"] = changed_fields
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.user) + "-" + str(self.organization)
