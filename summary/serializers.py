from rest_framework import serializers

from neatplus.serializers import UserModelSerializer

from .models import SurveyResult


class SurveyResultSerializer(UserModelSerializer):
    class Meta:
        model = SurveyResult
        fields = "__all__"


class WritableSurveyResultSerializer(SurveyResultSerializer):
    class Meta:
        model = SurveyResult
        exclude = ("survey",)
