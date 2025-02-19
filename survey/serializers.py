from django.contrib.gis.geos import GEOSGeometry
from django.core.files.storage import default_storage
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.fields import ImageField
from rest_framework_gis.fields import GeometryField

from neatplus.serializers import RichTextUploadingModelSerializer
from summary.serializers import SurveyResultSerializer, WritableSurveyResultSerializer

from .models import (
    AnswerTypeChoices,
    Option,
    Question,
    QuestionGroup,
    Survey,
    SurveyAnswer,
)


class QuestionGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionGroup
        fields = "__all__"


class QuestionSerializer(RichTextUploadingModelSerializer):
    class Meta:
        model = Question
        fields = "__all__"


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = "__all__"


class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = "__all__"


class ImageListField(serializers.ListField):
    child = serializers.ImageField()


class SurveyAnswerSerializer(serializers.ModelSerializer):
    formatted_answer = serializers.SerializerMethodField()

    answer_type_serializer_mapping = {
        AnswerTypeChoices.BOOLEAN.value: serializers.BooleanField,
        AnswerTypeChoices.DATE.value: serializers.DateField,
        AnswerTypeChoices.DESCRIPTION.value: None,
        AnswerTypeChoices.SINGLE_IMAGE.value: serializers.ImageField,
        AnswerTypeChoices.MULTIPLE_IMAGE.value: ImageListField,
        AnswerTypeChoices.LOCATION.value: GeometryField,
        AnswerTypeChoices.NUMBER.value: serializers.FloatField,
        AnswerTypeChoices.TEXT.value: serializers.CharField,
        AnswerTypeChoices.SINGLE_OPTION.value: None,
        AnswerTypeChoices.MULTIPLE_OPTION.value: None,
    }

    class Meta:
        model = SurveyAnswer
        fields = "__all__"

    def validate(self, attrs):
        data = super().validate(attrs)
        question_obj = data["question"]
        answer_type = data["answer_type"]
        options = data.get("options")
        if answer_type != question_obj.answer_type:
            raise serializers.ValidationError(
                {
                    "answer_type": _(
                        "Answer type of question and provided answer_type value doesn't match"
                    )
                }
            )
        serializer_class = self.answer_type_serializer_mapping[answer_type]
        if serializer_class is None and data.get("answer") is not None:
            raise serializers.ValidationError(
                {"answer": _("answer field cannot be present for provided answer_type")}
            )
        if answer_type in [
            AnswerTypeChoices.SINGLE_OPTION.value,
            AnswerTypeChoices.MULTIPLE_OPTION.value,
        ]:
            if options is None:
                raise serializers.ValidationError(
                    {"options": _("options should be present for provided answer_type")}
                )
            for option in options:
                if option.question != question_obj:
                    raise serializers.ValidationError(
                        {"options": _("Invalid option for question")}
                    )
            if (
                answer_type == AnswerTypeChoices.SINGLE_OPTION.value
                and len(options) != 1
            ):
                raise serializers.ValidationError(
                    {
                        "options": _(
                            "Only one option in list form is supported for question"
                        )
                    }
                )
        if serializer_class is None:
            validation_data = None
        elif serializer_class == GeometryField:
            validation_data = GEOSGeometry(data["answer"], srid=4326)
        elif serializer_class in [ImageField, ImageListField]:
            image_paths = data["answer"].split(",")
            if serializer_class == ImageField and len(image_paths) != 1:
                raise serializers.ValidationError(
                    {"answer": _("Only one image is supported for question")}
                )
            if serializer_class == ImageField:
                serializer_class_object = serializer_class()
            elif serializer_class == ImageListField:
                serializer_class_object = serializer_class.child
            errors = {}
            for i, image_path in enumerate(image_paths):
                try:
                    with default_storage.open(image_path) as file:
                        serializer_class_object.run_validation(file)
                except Exception:
                    errors[image_path] = "Invalid image file or image doesn't exists"
            if errors:
                raise serializers.ValidationError({"answer": errors})
            validation_data = None
        else:
            validation_data = data["answer"]
        if validation_data is not None:
            serializer_class().run_validation(validation_data)
        return data

    def get_formatted_answer(self, instance):
        serializer_class = self.answer_type_serializer_mapping[instance.answer_type]
        if serializer_class is None:
            representation_val = None
        elif serializer_class == GeometryField:
            representation_val = GEOSGeometry(instance.answer, srid=4326)
        elif serializer_class == ImageField:
            return self.context["request"].build_absolute_uri(
                default_storage.url(instance.answer)
            )
        elif serializer_class == ImageListField:
            image_paths = instance.answer.split(",")
            urls = []
            for image_path in image_paths:
                urls.append(
                    self.context["request"].build_absolute_uri(
                        default_storage.url(image_path)
                    )
                )
            return urls
        else:
            representation_val = instance.answer
        if representation_val is not None:
            return serializer_class().to_representation(representation_val)
        else:
            return None


class WritableSurveyAnswerSerializer(SurveyAnswerSerializer):
    class Meta:
        model = SurveyAnswer
        exclude = ("survey",)


class WritableSurveySerializer(SurveySerializer):
    answers = WritableSurveyAnswerSerializer(many=True)
    results = WritableSurveyResultSerializer(many=True)

    class Meta:
        model = Survey
        exclude = ("project", "is_shared_publicly")


class SharedSurveySerializer(SurveySerializer):
    answers = SurveyAnswerSerializer(many=True)
    results = SurveyResultSerializer(many=True)
