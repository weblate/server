from django.conf import settings

from neatplus.tests import APIFullTestCase


class TestAPI(APIFullTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.baker.make(
            settings.AUTH_USER_MODEL, is_superuser=True, is_active=True
        )
        cls.organization = cls.baker.make(
            "organization.Organization", members=[cls.user]
        )
        project = cls.baker.make("organization.Project", users=[cls.user])
        cls.organization_list_url = cls.reverse(
            "organization-list", kwargs={"version": "v1"}
        )
        cls.organization_detail_url = cls.reverse(
            "organization-detail", kwargs={"version": "v1", "pk": cls.organization.pk}
        )
        cls.project_list_url = cls.reverse("project-list", kwargs={"version": "v1"})
        cls.project_detail_url = cls.reverse(
            "project-detail", kwargs={"version": "v1", "pk": project.pk}
        )

    def test_organization_list(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.organization_list_url)
        self.assertEqual(response.status_code, self.status_code.HTTP_200_OK)

    def test_organization_detail(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.organization_detail_url)
        self.assertEqual(response.status_code, self.status_code.HTTP_200_OK)

    def test_non_authenticated_project_access(self):
        response = self.client.get(self.project_list_url)
        self.assertEqual(response.status_code, self.status_code.HTTP_403_FORBIDDEN)

    def test_project_list(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.project_list_url)
        self.assertEqual(response.status_code, self.status_code.HTTP_200_OK)

    def test_project_detail(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.project_detail_url)
        self.assertEqual(response.status_code, self.status_code.HTTP_200_OK)

    def test_project_creation(self):
        self.client.force_authenticate(self.user)
        another_user_pk = self.baker.make(settings.AUTH_USER_MODEL, is_active=True).pk
        data = {
            "title": "sample_project",
            "description": "Description goes here",
            "visibility": "private",
            "users": [another_user_pk],
        }
        url = self.reverse(
            "organization-create-project",
            kwargs={"version": "v1", "pk": self.organization.pk},
        )
        post_response = self.client.post(url, data=data)
        self.assertEqual(post_response.status_code, self.status_code.HTTP_201_CREATED)
        created_project_detail_url = self.reverse(
            "project-detail", kwargs={"version": "v1", "pk": post_response.json()["id"]}
        )
        get_response = self.client.get(created_project_detail_url)
        self.assertEqual(get_response.status_code, self.status_code.HTTP_200_OK)
