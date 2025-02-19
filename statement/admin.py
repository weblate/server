from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from modeltranslation.admin import TranslationAdmin
from ordered_model.admin import OrderedModelAdmin

from neatplus.admin import UserStampedModelAdmin

from .models import (
    Mitigation,
    Opportunity,
    OptionMitigation,
    OptionOpportunity,
    OptionStatement,
    QuestionStatement,
    Statement,
    StatementTag,
    StatementTagGroup,
    StatementTopic,
)


@admin.register(StatementTopic)
class StatementTopicAdmin(UserStampedModelAdmin, TranslationAdmin, OrderedModelAdmin):
    list_display = ("title", "context", "move_up_down_links")
    search_fields = ("title",)
    autocomplete_fields = ("context",)

    class Meta:
        verbose_name = _("statement topic")
        verbose_plural_name = _("statement topics")


@admin.register(StatementTagGroup)
class StatementTagGroupAdmin(
    UserStampedModelAdmin, TranslationAdmin, OrderedModelAdmin
):
    list_display = ("title", "move_up_down_links")
    search_fields = ("title",)

    class Meta:
        verbose_name = _("statement tag group")
        verbose_plural_name = _("statement tag groups")


@admin.register(StatementTag)
class StatementTagAdmin(UserStampedModelAdmin, TranslationAdmin, OrderedModelAdmin):
    list_display = ("title", "group", "move_up_down_links")
    search_fields = ("title",)
    autocomplete_fields = ("group",)

    class Meta:
        verbose_name = _("statement tag")
        verbose_plural_name = _("statement tags")


@admin.register(Statement)
class StatementAdmin(
    UserStampedModelAdmin,
    TranslationAdmin,
    OrderedModelAdmin,
):
    list_display = (
        "code",
        "topic",
        "title",
        "move_up_down_links",
    )
    search_fields = (
        "code",
        "title",
    )
    autocomplete_fields = ("topic", "tags")

    class Meta:
        verbose_name = _("statement")
        verbose_plural_name = _("statements")


@admin.register(Mitigation)
class MitigationAdmin(
    UserStampedModelAdmin,
    TranslationAdmin,
    OrderedModelAdmin,
):
    list_display = (
        "code",
        "statement",
        "title",
        "move_up_down_links",
    )
    search_fields = (
        "code",
        "title",
    )
    autocomplete_fields = ("statement",)

    class Meta:
        verbose_name = _("mitigation")
        verbose_plural_name = _("mitigations")


@admin.register(Opportunity)
class OpportunityAdmin(
    UserStampedModelAdmin,
    TranslationAdmin,
    OrderedModelAdmin,
):
    list_display = (
        "code",
        "statement",
        "title",
        "move_up_down_links",
    )
    search_fields = (
        "code",
        "title",
    )
    autocomplete_fields = ("statement",)

    class Meta:
        verbose_name = _("opportunity")
        verbose_plural_name = _("opportunities")


@admin.register(QuestionStatement)
class QuestionStatementAdmin(
    UserStampedModelAdmin,
    OrderedModelAdmin,
):
    list_display = ("question", "statement", "weightage", "move_up_down_links")
    autocomplete_fields = ("question", "statement")

    class Meta:
        verbose_name = _("question statement")
        verbose_plural_name = _("question statements")


@admin.register(OptionStatement)
class OptionStatementAdmin(
    UserStampedModelAdmin,
    OrderedModelAdmin,
):
    list_display = ("option", "statement", "weightage", "move_up_down_links")
    autocomplete_fields = ("option", "statement")

    class Meta:
        verbose_name = _("option statement")
        verbose_plural_name = _("option statements")


@admin.register(OptionMitigation)
class OptionMitigationAdmin(
    UserStampedModelAdmin,
    OrderedModelAdmin,
):
    list_display = ("option", "mitigation", "move_up_down_links")
    autocomplete_fields = ("option", "mitigation")

    class Meta:
        verbose_name = _("option mitigation")
        verbose_plural_name = _("option mitigations")


@admin.register(OptionOpportunity)
class OptionOpportunityAdmin(
    UserStampedModelAdmin,
    OrderedModelAdmin,
):
    list_display = ("option", "opportunity", "move_up_down_links")
    autocomplete_fields = ("option", "opportunity")

    class Meta:
        verbose_name = _("option opportunity")
        verbose_plural_name = _("option opportunites")
