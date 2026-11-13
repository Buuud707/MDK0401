from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

User = get_user_model()
PASSWORD = "Str0ngPass!2026"


class AuthTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user("adm", password=PASSWORD, role="admin")
        cls.operator = User.objects.create_user("op", password=PASSWORD, role="operator")

    def test_login_returns_jwt_and_token_works(self):
        resp = self.client.post("/api/auth/login/", {"username": "op", "password": PASSWORD}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("access", resp.data)
        self.assertIn("refresh", resp.data)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")
        me = self.client.get("/api/auth/me/")
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.data["username"], "op")

    def test_wrong_password(self):
        resp = self.client.post("/api/auth/login/", {"username": "op", "password": "bad"}, format="json")
        self.assertEqual(resp.status_code, 401)

    def test_refresh(self):
        login = self.client.post("/api/auth/login/", {"username": "op", "password": PASSWORD}, format="json")
        resp = self.client.post("/api/auth/refresh/", {"refresh": login.data["refresh"]}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("access", resp.data)

    def test_operator_cannot_list_users(self):
        self.client.force_authenticate(self.operator)
        self.assertEqual(self.client.get("/api/users/").status_code, 403)

    def test_admin_creates_user_password_is_hashed(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.post(
            "/api/users/",
            {"username": "new", "password": PASSWORD, "role": "operator", "full_name": "Новый"},
            format="json",
        )
        self.assertEqual(resp.status_code, 201, resp.data)
        self.assertNotIn("password", resp.data)
        user = User.objects.get(username="new")
        self.assertNotEqual(user.password, PASSWORD)
        self.assertTrue(user.check_password(PASSWORD))

    def test_api_root_is_public(self):
        self.assertEqual(self.client.get("/api/").status_code, 200)
