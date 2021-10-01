from rest_framework import serializers

from neatplus.serializers import UserModelSerializer

from .models import Organization, OrganizationMemberRequest


class OrganizationSerializer(UserModelSerializer):
    class Meta:
        model = Organization
        exclude = (
            "admins",
            "members",
        )


class OrganizationMemberRequestSerializer(UserModelSerializer):
    is_organization_admin = serializers.SerializerMethodField()

    class Meta:
        model = OrganizationMemberRequest
        fields = "__all__"

    def get_is_organization_admin(self, obj):
        return self.context["request"].user in obj.organization.admins.all()


class OrganizationUserSerializer(serializers.Serializer):
    user = serializers.CharField()
    role = serializers.ChoiceField(choices=["admin", "member"])
