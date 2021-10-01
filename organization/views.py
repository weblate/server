from collections import OrderedDict

from django.db.models import Q
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import mixins, permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from neatplus.views import UserStampedModelViewSetMixin
from project.models import Project
from project.serializers import CreateProjectSerializer
from user.models import User

from .filters import OrganizationFilter, OrganizationMemberRequestFilter
from .models import Organization, OrganizationMemberRequest
from .permissions import (
    IsMemberRequestOrganizationAdmin,
    IsOrganizationAdmin,
    IsOrganizationAdminOrReadOnly,
)
from .serializers import (
    OrganizationMemberRequestSerializer,
    OrganizationSerializer,
    OrganizationUserSerializer,
)


class OrganizationViewSet(UserStampedModelViewSetMixin, viewsets.ModelViewSet):
    filterset_class = OrganizationFilter
    permission_classes = [IsOrganizationAdminOrReadOnly]
    serializer_class = OrganizationSerializer

    def get_queryset(self):
        authenticated_user = self.request.user
        if authenticated_user.is_authenticated:
            filter_statement = Q(status="accepted") | Q(created_by=self.request.user)
        else:
            filter_statement = Q(status="accepted")
        return Organization.objects.filter(filter_statement)

    @extend_schema(
        responses=inline_serializer(
            name="OrganizationProjectCreateResponseSerializer",
            fields={
                "detail": serializers.CharField(default="Successfully created project")
            },
        )
    )
    @action(
        methods=["post"],
        detail=True,
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=CreateProjectSerializer,
    )
    def create_project(self, request, *args, **kwargs):
        organization = self.get_object()
        data = request.data
        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        validated_data = serializer.validated_data
        Project.objects.create(
            **validated_data, organization=organization, created_by=self.request.user
        )
        return Response(
            {"detail": "Successfully created project"}, status=status.HTTP_201_CREATED
        )

    @extend_schema(
        responses=inline_serializer(
            name="OrganizationMemberRequestResponseSerializer",
            fields={
                "detail": serializers.CharField(
                    default="Successfully requested member access"
                )
            },
        )
    )
    @action(
        methods=["post"],
        detail=True,
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=serializers.Serializer,
    )
    def member_request(self, request, *args, **kwargs):
        organization = self.get_object()
        user = self.request.user
        OrganizationMemberRequest.objects.create(
            user=user, organization=organization, created_by=user
        )
        return Response(
            {"detail": "Successfully requested member access"},
            status=status.HTTP_200_OK,
        )

    @action(
        methods=["get"],
        detail=True,
        permission_classes=[IsOrganizationAdmin],
        serializer_class=OrganizationUserSerializer,
    )
    def users(self, request, *args, **kwargs):
        organization = self.get_object()
        users = []
        admins = organization.admins.values_list("username", flat=True)
        for admin in admins:
            users.append({"user": admin, "role": "admin"})
        members = organization.members.values_list("username", flat=True)
        for member in members:
            users.append({"user": member, "role": "member"})
        serializer = self.get_serializer(data=users, many=True)
        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return Response(serializer.data)

    @extend_schema(
        responses=inline_serializer(
            name="OrganizationAddUserSerializer",
            fields={
                "detail": serializers.CharField(
                    default="Successfully added all valid users"
                )
            },
        )
    )
    @action(
        methods=["post"],
        detail=True,
        permission_classes=[IsOrganizationAdmin],
        serializer_class=OrganizationUserSerializer,
    )
    def add_users(self, request, *args, **kwargs):
        organization = self.get_object()
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
            user = User.objects.filter(username=validated_datum["user"]).first()
            if user:
                if validated_datum["role"] == "admin":
                    organization.admins.add(user)
                elif validated_datum["role"] == "member":
                    organization.members.add(user)
        return Response({"detail": "Successfully added all valid users"})

    @extend_schema(
        responses=inline_serializer(
            name="OrganizationAddUserSerializer",
            fields={
                "detail": serializers.CharField(
                    default="Successfully removed all valid users"
                )
            },
        )
    )
    @action(
        methods=["post"],
        detail=True,
        permission_classes=[IsOrganizationAdmin],
        serializer_class=OrganizationUserSerializer,
    )
    def remove_users(self, request, *args, **kwargs):
        organization = self.get_object()
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
            user = User.objects.filter(username=validated_datum["user"]).first()
            if user:
                if validated_datum["role"] == "admin":
                    organization.admins.remove(user)
                elif validated_datum["role"] == "member":
                    organization.members.remove(user)
        return Response({"detail": "Successfully removed all valid users"})


class OrganizationMemberRequestViewSet(
    mixins.DestroyModelMixin, viewsets.ReadOnlyModelViewSet
):
    serializer_class = OrganizationMemberRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = OrganizationMemberRequestFilter

    def get_queryset(self):
        user = self.request.user
        return (
            OrganizationMemberRequest.objects.filter(
                Q(organization__admins=user) | Q(user=user)
            )
            .prefetch_related("organization__admins")
            .distinct()
        )

    @extend_schema(
        responses=inline_serializer(
            name="OrganizationMemeberRequestAcceptResponseSerializer",
            fields={
                "detail": serializers.CharField(
                    default="Member request successfully accepted"
                )
            },
        )
    )
    @action(
        methods=["post"],
        detail=True,
        serializer_class=serializers.Serializer,
        permission_classes=[IsMemberRequestOrganizationAdmin],
    )
    def accept(self, request, *args, **kwargs):
        member_request = self.get_object()
        if member_request.status != "accepted":
            member_request.updated_by = request.user
            member_request.status = "accepted"
            member_request.save()
        return Response({"detail": "Member request successfully accepted"})

    @extend_schema(
        responses=inline_serializer(
            name="OrganizationMemeberRequestRejectResponseSerializer",
            fields={
                "detail": serializers.CharField(
                    default="Member request successfully rejected"
                )
            },
        )
    )
    @action(
        methods=["post"],
        detail=True,
        serializer_class=serializers.Serializer,
        permission_classes=[IsMemberRequestOrganizationAdmin],
    )
    def reject(self, request, *args, **kwargs):
        member_request = self.get_object()
        if member_request.status != "rejected":
            member_request.updated_by = request.user
            member_request.status = "rejected"
            member_request.save()
        return Response({"detail": "Member request successfully rejected"})
