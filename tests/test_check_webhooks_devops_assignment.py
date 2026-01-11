import pygit2

from scripts.check_webhooks_devops_assignment import check_app_is_alive, check_event_update_site, CONFIG, \
    check_no_automatic_site_update, push_ci_commit

import pytest
from unittest.mock import patch

@pytest.mark.parametrize("status_code", [200, 201, 202])
def test_app_is_alive(requests_mock, status_code):
    url = "https://example.ru"
    requests_mock.get(url, status_code=status_code)
    assert check_app_is_alive(url) is True

@pytest.mark.parametrize("status_code", [100, 300, 400, 500])
def test_app_is_dead(requests_mock, status_code):
    url = "https://example.ru"
    requests_mock.get(url, status_code=status_code)
    assert check_app_is_alive(url) is False

def test_event_update_site(requests_mock, monkeypatch):
    app_url = "https://example.ru"
    webhook_url = "https://example.com"

    monkeypatch.setitem(CONFIG, "check_event_timeout", 0.1)
    requests_mock.get(app_url, [
        {"text": 'foo<meta name="deploydate" content="20260120012">bar', "status_code": 200},
        {"text": 'foo<meta name="deploydate" content="20260120013">bar', "status_code": 200}
    ])

    with patch("scripts.check_webhooks_devops_assignment.push_ci_commit") as mock_push_ci_commit:
        mock_push_ci_commit.return_value = None
        assert check_event_update_site(app_url, webhook_url, 'master') is True

def test_event_doest_not_update_site(requests_mock, monkeypatch):
    app_url = "https://example.ru"
    webhook_url = "https://example.com"

    monkeypatch.setitem(CONFIG, "check_event_timeout", 0.1)
    requests_mock.get(app_url, [
        {"text": 'foo<meta name="deploydate" content="20260120012">bar', "status_code": 200},
        {"text": 'foo<meta name="deploydate" content="20260120012">var', "status_code": 200}
    ])

    with patch("scripts.check_webhooks_devops_assignment.push_ci_commit") as mock_push_ci_commit:
        mock_push_ci_commit.return_value = None
        assert check_event_update_site(app_url, webhook_url, 'master') is False


def test_site_not_updated_automatic(requests_mock, monkeypatch):
    app_url = "https://example.ru"

    monkeypatch.setitem(CONFIG, "wait_automatic_update", 0.1)
    requests_mock.get(app_url, [
        {"text": 'foo<meta name="deploydate" content="20260120012">bar', "status_code": 200},
        {"text": 'foo<meta name="deploydate" content="20260120012">bar', "status_code": 200}
    ])

    assert check_no_automatic_site_update(app_url) is True

@pytest.mark.slow
def test_push_ci_commit():
    push_ci_commit("git@github.com:prafdin/for-test-only.git", "main")
    assert True is True