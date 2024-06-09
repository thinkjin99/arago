import pytest
from django.conf import settings
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def django_db_setup():
    settings.DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        "ATOMIC_REQUESTS": True,
    }
