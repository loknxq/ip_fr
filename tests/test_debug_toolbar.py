"""Панель SQL работает локально и не вмешивается в обычные проверки."""

import re

from django.conf import settings
from django.contrib.staticfiles import finders
from django.test import TestCase, override_settings

from collections_app.models import Collection
from records.models import Record


@override_settings(
    DEBUG=True,
    INSTALLED_APPS=[*settings.INSTALLED_APPS, "debug_toolbar"],
    MIDDLEWARE=[
        "debug_toolbar.middleware.DebugToolbarMiddleware",
        *settings.MIDDLEWARE,
    ],
    ROOT_URLCONF="tests.toolbar_urls",
    INTERNAL_IPS=["127.0.0.1", "::1"],
    DEBUG_TOOLBAR_CONFIG={
        "IS_RUNNING_TESTS": False,
        "RENDER_PANELS": False,
        "SHOW_COLLAPSED": True,
    },
)
class DebugToolbarTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        record = Record.objects.create(
            title="Abbey Road", artist="The Beatles", year=1969,
        )
        collection = Collection.objects.create(name="Классика рока")
        collection.records.add(record)

    def test_local_page_has_sql_panel_with_join_and_projected_fields(self):
        response = self.client.get(
            "/collections/statistics/", REMOTE_ADDR="127.0.0.1",
        )
        self.assertContains(response, "SQLPanel")
        html = response.content.decode()
        request_id = re.search(r'data-request-id="([^"]+)"', html).group(1)
        panel_url = re.search(
            r'data-render-panel-url="([^"]+)"', html,
        ).group(1)
        panel = self.client.get(
            panel_url, {"request_id": request_id, "panel_id": "SQLPanel"},
            REMOTE_ADDR="127.0.0.1",
        )
        self.assertEqual(panel.status_code, 200)
        self.assertIn("INNER JOIN", panel.json()["content"])
        self.assertIn("record_title", panel.json()["content"])
        self.assertIn("collection_name", panel.json()["content"])
        self.assertIsNotNone(finders.find("debug_toolbar/js/toolbar.js"))

    def test_nonlocal_request_does_not_receive_toolbar(self):
        response = self.client.get(
            "/collections/statistics/", REMOTE_ADDR="203.0.113.20",
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "SQLPanel")

    @override_settings(DEBUG=False)
    def test_debug_false_does_not_receive_toolbar(self):
        response = self.client.get(
            "/collections/statistics/", REMOTE_ADDR="127.0.0.1",
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "SQLPanel")
