from rest_framework import serializers

from neatplus.serializers import UserModelSerializer

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


class StatementTopicSerializer(UserModelSerializer):
    class Meta:
        model = StatementTopic
        fields = "__all__"


class StatementTagGroupSerializer(UserModelSerializer):
    class Meta:
        model = StatementTagGroup
        fields = "__all__"


class StatementTagSerializer(UserModelSerializer):
    class Meta:
        model = StatementTag
        fields = "__all__"


class StatementSerializer(UserModelSerializer):
    class Meta:
        model = Statement
        fields = "__all__"


class MitigationSerializer(UserModelSerializer):
    class Meta:
        model = Mitigation
        fields = "__all__"


class OpportunitySerializer(UserModelSerializer):
    class Meta:
        model = Opportunity
        fields = "__all__"


class QuestionStatementSerializer(UserModelSerializer):
    class Meta:
        model = QuestionStatement
        fields = "__all__"


class OptionStatementSerializer(UserModelSerializer):
    class Meta:
        model = OptionStatement
        fields = "__all__"


class OptionMitigationSerializer(UserModelSerializer):
    class Meta:
        model = OptionMitigation
        fields = "__all__"


class OptionOpportunitySerializer(UserModelSerializer):
    class Meta:
        model = OptionOpportunity
        fields = "__all__"
