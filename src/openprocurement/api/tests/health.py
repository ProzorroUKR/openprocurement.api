from openprocurement.api.tests.base import BaseWebTest


class HealthTestBase(BaseWebTest):

    return_value = []

    def setUp(self):
        self.app.authorization = ("Basic", ("token", ""))

    def test_health_view(self):
        response = self.app.get("/health", status=200)
        self.assertEqual(response.status, "200 OK")
