from apps.tickets.tests import BaseAPITest


class ReportTests(BaseAPITest):
    def test_kpi_requires_auth(self):
        self.assertEqual(self.client.get("/api/reports/kpi/").status_code, 401)

    def test_kpi_updates_after_resolution(self):
        t1 = self.make_ticket(title="A")
        t2 = self.make_ticket(title="B")
        self.make_ticket(title="C")
        for t in (t1, t2):
            t.assign(self.operator, by=self.operator)
        t1.change_status("resolved", self.operator)

        self.client.force_authenticate(self.manager)
        data = self.client.get("/api/reports/kpi/").data
        self.assertEqual(data["total"], 3)
        self.assertEqual(data["resolved"], 1)
        self.assertEqual(data["open"], 2)
        self.assertEqual(data["by_status"]["new"], 1)
        self.assertEqual(data["by_status"]["in_progress"], 1)
        self.assertEqual(data["by_status"]["resolved"], 1)
        self.assertEqual(data["sla_compliance_percent"], 100.0)
        self.assertEqual(data["by_category"][0]["count"], 3)

    def test_kpi_empty(self):
        self.client.force_authenticate(self.manager)
        data = self.client.get("/api/reports/kpi/").data
        self.assertEqual(data["total"], 0)
        self.assertIsNone(data["avg_resolution_hours"])

    def test_csv_export(self):
        self.make_ticket()
        self.client.force_authenticate(self.manager)
        resp = self.client.get("/api/reports/export/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("text/csv", resp["Content-Type"])
        self.assertIn("REQ-", resp.content.decode("utf-8-sig"))
