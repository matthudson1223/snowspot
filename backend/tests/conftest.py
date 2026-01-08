"""Pytest configuration and fixtures."""

import pytest
from datetime import datetime, timezone, timedelta


@pytest.fixture
def current_time():
    """Provide a fixed current time for deterministic tests."""
    return datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def one_hour_ago(current_time):
    """Timestamp one hour before current time."""
    return current_time - timedelta(hours=1)


@pytest.fixture
def two_hours_ago(current_time):
    """Timestamp two hours before current time."""
    return current_time - timedelta(hours=2)


@pytest.fixture
def one_day_ago(current_time):
    """Timestamp one day before current time."""
    return current_time - timedelta(days=1)
