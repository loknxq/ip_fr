"""Изолированная тестовая БД Django для pytest, без pytest-django."""

import os

import django
import pytest
from django.test.utils import (
    setup_databases,
    setup_test_environment,
    teardown_databases,
    teardown_test_environment,
)


def pytest_configure():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vinyl_project.settings")
    django.setup()


@pytest.fixture(scope="session", autouse=True)
def django_test_database():
    """Миграции применяются к тестовой БД, рабочие данные не меняются."""
    setup_test_environment()
    old_config = setup_databases(verbosity=0, interactive=False)
    try:
        yield
    finally:
        teardown_databases(old_config, verbosity=0)
        teardown_test_environment()
