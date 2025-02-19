from collections import OrderedDict

from django.db import transaction
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from neatplus.views import UserStampedModelViewSetMixin
from summary.models import SurveyResult
from survey.models import Survey, SurveyAnswer
from survey.serializers import WritableSurveySerializer

from .filters import ProjectFilter
from .models import ProjectUser
from .permissions import (
    CanAcceptRejectProject,
    CanCreateSurveyForProject,
    CanEditProject,
    CanEditProjectOrReadOnly,
)
from .serializers import (
    AccessLevelResponseSerializer,
    CreateProjectSerializer,
    ProjectSerializer,
    ProjectUserSerializer,
    RemoveProjectUserSerializer,
    UpsertProjectUserSerializer,
)
from .utils import read_allowed_project_for_user


class ProjectViewSet(UserStampedModelViewSetMixin, viewsets.ModelViewSet):
    permission_classes = [CanEditProjectOrReadOnly]
    filterset_class = ProjectFilter

    def get_queryset(self):
        current_user = self.request.user
        return (
            read_allowed_project_for_user(current_user)
            .select_related("created_by")
            .prefetch_related("organization__admins")
        )

    def get_serializer_class(self):
        if self.name and self.serializer_class:
            return self.serializer_class
        if self.action == "create":
            return CreateProjectSerializer
        return ProjectSerializer

    @action(
        methods=["get"],
        detail=True,
        permission_classes=[CanEditProject],
        serializer_class=ProjectUserSerializer,
    )
    def users(self, request, *args, **kwargs):
        project = self.get_object()
        users = project.users.all()
        project_user = ProjectUser.objects.filter(project=project, user__in=users)
        serializer = self.get_serializer(project_user, many=True)
        return Response(serializer.data)

    @extend_schema(
        responses=inline_serializer(
            name="ProjectAcceptResponseSerializer",
            fields={
                "detail": serializers.CharField(
                    default=_("Project successfully accepted")
                )
            },
        )
    )
    @action(
        methods=["post"],
        detail=True,
        permission_classes=[CanAcceptRejectProject],
        serializer_class=serializers.Serializer,
    )
    def accept(self, request, *args, **kwargs):
        project = self.get_object()
        if project.status != "accepted":
            project.updated_by = request.user
            project.status = "accepted"
            project.save()
        return Response({"detail": _("Project successfully accepted")})

    @extend_schema(
        responses=inline_serializer(
            name="ProjectRejectResponseSerializer",
            fields={
                "detail": serializers.CharField(
                    default=_("Project successfully rejected")
                )
            },
        )
    )
    @action(
        methods=["post"],
        detail=True,
        permission_classes=[CanAcceptRejectProject],
        serializer_class=serializers.Serializer,
    )
    def reject(self, request, *args, **kwargs):
        project = self.get_object()
        if project.status != "rejected":
            project.updated_by = request.user
            project.status = "rejected"
            project.save()
        return Response({"detail": _("Project successfully rejected")})

    @extend_schema(
        responses=inline_serializer(
            name="ProjectUpsertResponseSerializer",
            fields={
                "detail": serializers.CharField(
                    default=_("Successfully modified users list for project")
                )
            },
        )
    )
    @action(
        methods=["post"],
        detail=True,
        permission_classes=[CanEditProject],
        serializer_class=UpsertProjectUserSerializer,
    )
    def update_or_add_users(self, request, *args, **kwargs):
        project = self.get_object()
        data = request.data

        if isinstance(data, dict):
            serializer = self.get_serializer(data=data)
        else:
            serializer = self.get_serializer(data=data, many=True)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        if isinstance(validated_data, OrderedDict):
            validated_data = [validated_data]

        for validated_datum in validated_data:
            user = validated_datum.pop("user")
            try:
                project_user = ProjectUser.objects.get(project=project, user=user)
                validated_datum["updated_by"] = request.user
                for key, value in validated_datum.items():
                    setattr(project_user, key, value)
                project_user.save()
            except ProjectUser.DoesNotExist:
                validated_datum["created_by"] = request.user
                project_user = ProjectUser.objects.create(
                    project=project, user=user, **validated_datum
                )
        return Response({"detail": _("Successfully modified users list for project")})

    @extend_schema(
        responses=inline_serializer(
            name="ProjectRemoveUserResponseSerializer",
            fields={
                "detail": serializers.CharField(
                    default=_("Successfully removed users from project")
                )
            },
        )
    )
    @action(
        methods=["post"],
        detail=True,
        permission_classes=[CanEditProject],
        serializer_class=RemoveProjectUserSerializer,
    )
    def remove_users(self, request, *args, **kwargs):
        project = self.get_object()
        data = request.data

        if isinstance(data, dict):
            serializer = self.get_serializer(data=data)
        else:
            serializer = self.get_serializer(data=data, many=True)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        if isinstance(validated_data, OrderedDict):
            validated_data = [validated_data]

        for validated_datum in validated_data:
            user_obj = validated_datum.pop("user")
            project.users.remove(user_obj)
        return Response({"detail": _("Successfully removed users from project")})

    @action(
        methods=["get"],
        detail=True,
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=AccessLevelResponseSerializer,
    )
    def access_level(self, request, *args, **kwargs):
        project = self.get_object()
        user = self.request.user
        if project.organization and user in project.organization.admins.all():
            access_level = "organization_admin"
        elif user == project.created_by:
            access_level = "owner"
        elif user in project.users.all():
            permission = ProjectUser.objects.get(user=user, project=project).permission
            if permission == "write":
                access_level = "write"
            else:
                access_level = "read_only"
        else:
            access_level = "visibility"
        data = {"access_level": access_level}
        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return Response(serializer.data)

    @extend_schema(
        responses=inline_serializer(
            name="ProjectSurveySubmitResponseSerializer",
            fields={
                "detail": serializers.CharField(
                    default=_("Successfully submitted survey")
                )
            },
        )
    )
    @action(
        methods=["post"],
        detail=True,
        permission_classes=[CanCreateSurveyForProject],
        serializer_class=WritableSurveySerializer,
    )
    def create_survey(self, request, *args, **kwargs):
        project = self.get_object()
        data = request.data
        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        validated_data = serializer.validated_data
        answers = validated_data.pop("answers", [])
        results = validated_data.pop("results", [])
        try:
            with transaction.atomic():
                survey = Survey.objects.create(
                    **validated_data, created_by=request.user, project=project
                )
                for answer in answers:
                    options = answer.pop("options", None)
                    survey_answer = SurveyAnswer.objects.create(
                        **answer, created_by=request.user, survey=survey
                    )
                    if options:
                        survey_answer.options.add(*options)
                for result in results:
                    SurveyResult.objects.create(
                        **result, created_by=request.user, survey=survey
                    )
        except Exception:
            return Response(
                {
                    "error": _(
                        "Failed to create survey or survey answer due to invalid data"
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"detail": _("Successfully submitted survey")},
            status=status.HTTP_201_CREATED,
        )
