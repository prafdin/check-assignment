import io
import zipfile

import pytest
from unittest.mock import patch, MagicMock
from checker.checks import check_workflow_run_success, CONFIG, check_tests_passed


def test_check_workflow_run_success_success(monkeypatch):
    monkeypatch.setitem(CONFIG, "timeout", 1)
    monkeypatch.setitem(CONFIG, "poll_interval", 0.1)
    with patch('checker.checks.Github') as mock_github:
        # Mock the Github API response
        mock_repo = MagicMock()
        mock_workflow_run = MagicMock()
        mock_workflow_run.status = "completed"
        mock_workflow_run.conclusion = "success"
        
        mock_runs_page = MagicMock()
        mock_runs_page.totalCount = 1
        mock_runs_page.__getitem__.return_value = mock_workflow_run
        
        mock_repo.get_workflow_runs.return_value = mock_runs_page
        mock_repo.get_workflow_run.return_value = mock_workflow_run
        
        mock_github_instance = mock_github.return_value
        mock_github_instance.get_repo.return_value = mock_repo

        # Call the function and assert the result
        assert check_workflow_run_success("owner/repo", "commit_sha", "fake_token") is True

def test_check_workflow_run_success_failure(monkeypatch):
    monkeypatch.setitem(CONFIG, "timeout", 1)
    monkeypatch.setitem(CONFIG, "poll_interval", 0.1)
    with patch('checker.checks.Github') as mock_github:
        # Mock the Github API response
        mock_repo = MagicMock()
        mock_workflow_run = MagicMock()
        mock_workflow_run.status = "completed"
        mock_workflow_run.conclusion = "failure"
        
        mock_runs_page = MagicMock()
        mock_runs_page.totalCount = 1
        mock_runs_page.__getitem__.return_value = mock_workflow_run
        
        mock_repo.get_workflow_runs.return_value = mock_runs_page
        mock_repo.get_workflow_run.return_value = mock_workflow_run
        
        mock_github_instance = mock_github.return_value
        mock_github_instance.get_repo.return_value = mock_repo

        # Call the function and assert the result
        assert check_workflow_run_success("owner/repo", "commit_sha", "fake_token") is False

def test_check_workflow_run_not_found(monkeypatch):
    with patch('checker.checks.Github') as mock_github:
        monkeypatch.setitem(CONFIG, "poll_interval", 0.1)

        # Mock the Github API response
        mock_repo = MagicMock()
        mock_runs_page = MagicMock()
        mock_runs_page.totalCount = 0
        
        mock_repo.get_workflow_runs.return_value = mock_runs_page
        
        mock_github_instance = mock_github.return_value
        mock_github_instance.get_repo.return_value = mock_repo

        # Call the function and assert the result
        assert check_workflow_run_success("owner/repo", "commit_sha", "fake_token") is False

def test_check_workflow_run_timeout(monkeypatch):
    with patch('checker.checks.Github') as mock_github:

        monkeypatch.setitem(CONFIG, "poll_interval", 0.1)
        monkeypatch.setitem(CONFIG, "timeout", 0.5)
        # Mock the Github API response
        mock_repo = MagicMock()
        mock_workflow_run = MagicMock()
        mock_workflow_run.status = "in_progress"

        mock_runs_page = MagicMock()
        mock_runs_page.totalCount = 1
        mock_runs_page.__getitem__.return_value = mock_workflow_run

        mock_repo.get_workflow_runs.return_value = mock_runs_page
        mock_repo.get_workflow_run.return_value = mock_workflow_run

        mock_github_instance = mock_github.return_value
        mock_github_instance.get_repo.return_value = mock_repo

        # Call the function and assert the result
        assert check_workflow_run_success("owner/repo", "commit_sha", "fake_token") is False

def create_zip_file(xml_content):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        zf.writestr('test_results.xml', xml_content)
    zip_buffer.seek(0)
    return zip_buffer.read()


@patch('requests.get')
def test_check_tests_passed_success(mock_requests_get, monkeypatch):
    monkeypatch.setitem(CONFIG, "timeout", 1)
    monkeypatch.setitem(CONFIG, "poll_interval", 0.1)

    xml_content = '<testsuite errors="0" failures="0" skipped="0" tests="12"></testsuite>'
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = create_zip_file(xml_content)
    mock_requests_get.return_value = mock_response

    with patch('checker.checks.Github') as mock_github:
        mock_repo = MagicMock()
        mock_workflow_run = MagicMock()
        mock_workflow_run.status = "completed"
        mock_workflow_run.conclusion = "success"

        mock_artifact = MagicMock()
        mock_artifact.name = "test_result"
        mock_artifact.archive_download_url = "http://fake-url.com"

        mock_workflow_run.get_artifacts.return_value = [mock_artifact]

        mock_runs_page = MagicMock()
        mock_runs_page.totalCount = 1
        mock_runs_page.__getitem__.return_value = mock_workflow_run

        mock_repo.get_workflow_runs.return_value = mock_runs_page
        mock_repo.get_workflow_run.return_value = mock_workflow_run

        mock_github_instance = mock_github.return_value
        mock_github_instance.get_repo.return_value = mock_repo

        assert check_tests_passed("owner/repo", "commit_sha", "fake_token") is True


@patch('requests.get')
def test_check_tests_passed_test_failures(mock_requests_get, monkeypatch):
    monkeypatch.setitem(CONFIG, "timeout", 1)
    monkeypatch.setitem(CONFIG, "poll_interval", 0.1)

    xml_content = '<testsuite errors="0" failures="1" skipped="0" tests="12"></testsuite>'
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = create_zip_file(xml_content)
    mock_requests_get.return_value = mock_response

    with patch('checker.checks.Github') as mock_github:
        mock_repo = MagicMock()
        mock_workflow_run = MagicMock()
        mock_workflow_run.status = "completed"
        mock_workflow_run.conclusion = "success"

        mock_artifact = MagicMock()
        mock_artifact.name = "test_result"
        mock_artifact.archive_download_url = "http://fake-url.com"

        mock_workflow_run.get_artifacts.return_value = [mock_artifact]

        mock_runs_page = MagicMock()
        mock_runs_page.totalCount = 1
        mock_runs_page.__getitem__.return_value = mock_workflow_run

        mock_repo.get_workflow_runs.return_value = mock_runs_page
        mock_repo.get_workflow_run.return_value = mock_workflow_run

        mock_github_instance = mock_github.return_value
        mock_github_instance.get_repo.return_value = mock_repo

        assert check_tests_passed("owner/repo", "commit_sha", "fake_token") is False


@patch('requests.get')
def test_check_tests_passed_test_errors(mock_requests_get, monkeypatch):
    monkeypatch.setitem(CONFIG, "timeout", 1)
    monkeypatch.setitem(CONFIG, "poll_interval", 0.1)

    xml_content = '<testsuite errors="1" failures="0" skipped="0" tests="12"></testsuite>'
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = create_zip_file(xml_content)
    mock_requests_get.return_value = mock_response

    with patch('checker.checks.Github') as mock_github:
        mock_repo = MagicMock()
        mock_workflow_run = MagicMock()
        mock_workflow_run.status = "completed"
        mock_workflow_run.conclusion = "success"

        mock_artifact = MagicMock()
        mock_artifact.name = "test_result"
        mock_artifact.archive_download_url = "http://fake-url.com"

        mock_workflow_run.get_artifacts.return_value = [mock_artifact]

        mock_runs_page = MagicMock()
        mock_runs_page.totalCount = 1
        mock_runs_page.__getitem__.return_value = mock_workflow_run

        mock_repo.get_workflow_runs.return_value = mock_runs_page
        mock_repo.get_workflow_run.return_value = mock_workflow_run

        mock_github_instance = mock_github.return_value
        mock_github_instance.get_repo.return_value = mock_repo

        assert check_tests_passed("owner/repo", "commit_sha", "fake_token") is False


@patch('requests.get')
def test_check_tests_passed_no_tests(mock_requests_get, monkeypatch):
    monkeypatch.setitem(CONFIG, "timeout", 1)
    monkeypatch.setitem(CONFIG, "poll_interval", 0.1)

    xml_content = '<testsuite errors="0" failures="0" skipped="0" tests="0"></testsuite>'
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = create_zip_file(xml_content)
    mock_requests_get.return_value = mock_response

    with patch('checker.checks.Github') as mock_github:
        mock_repo = MagicMock()
        mock_workflow_run = MagicMock()
        mock_workflow_run.status = "completed"
        mock_workflow_run.conclusion = "success"

        mock_artifact = MagicMock()
        mock_artifact.name = "test_result"
        mock_artifact.archive_download_url = "http://fake-url.com"

        mock_workflow_run.get_artifacts.return_value = [mock_artifact]

        mock_runs_page = MagicMock()
        mock_runs_page.totalCount = 1
        mock_runs_page.__getitem__.return_value = mock_workflow_run

        mock_repo.get_workflow_runs.return_value = mock_runs_page
        mock_repo.get_workflow_run.return_value = mock_workflow_run

        mock_github_instance = mock_github.return_value
        mock_github_instance.get_repo.return_value = mock_repo

        assert check_tests_passed("owner/repo", "commit_sha", "fake_token") is False


@patch('requests.get')
def test_check_tests_passed_invalid_xml(mock_requests_get, monkeypatch):
    monkeypatch.setitem(CONFIG, "timeout", 1)
    monkeypatch.setitem(CONFIG, "poll_interval", 0.1)

    xml_content = '<testsuite errors="0" failures="0" skipped="0" tests="12">'  # Malformed XML
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = create_zip_file(xml_content)
    mock_requests_get.return_value = mock_response

    with patch('checker.checks.Github') as mock_github:
        mock_repo = MagicMock()
        mock_workflow_run = MagicMock()
        mock_workflow_run.status = "completed"
        mock_workflow_run.conclusion = "success"

        mock_artifact = MagicMock()
        mock_artifact.name = "test_result"
        mock_artifact.archive_download_url = "http://fake-url.com"

        mock_workflow_run.get_artifacts.return_value = [mock_artifact]

        mock_runs_page = MagicMock()
        mock_runs_page.totalCount = 1
        mock_runs_page.__getitem__.return_value = mock_workflow_run

        mock_repo.get_workflow_runs.return_value = mock_runs_page
        mock_repo.get_workflow_run.return_value = mock_workflow_run

        mock_github_instance = mock_github.return_value
        mock_github_instance.get_repo.return_value = mock_repo

        assert check_tests_passed("owner/repo", "commit_sha", "fake_token") is False


def test_check_tests_passed_no_artifact(monkeypatch):
    monkeypatch.setitem(CONFIG, "timeout", 1)
    monkeypatch.setitem(CONFIG, "poll_interval", 0.1)
    with patch('checker.checks.Github') as mock_github:
        mock_repo = MagicMock()
        mock_workflow_run = MagicMock()
        mock_workflow_run.status = "completed"
        mock_workflow_run.conclusion = "success"

        mock_workflow_run.get_artifacts.return_value = []

        mock_runs_page = MagicMock()
        mock_runs_page.totalCount = 1
        mock_runs_page.__getitem__.return_value = mock_workflow_run

        mock_repo.get_workflow_runs.return_value = mock_runs_page
        mock_repo.get_workflow_run.return_value = mock_workflow_run

        mock_github_instance = mock_github.return_value
        mock_github_instance.get_repo.return_value = mock_repo

        assert check_tests_passed("owner/repo", "commit_sha", "fake_token") is False


def test_check_tests_passed_workflow_failure(monkeypatch):
    monkeypatch.setitem(CONFIG, "timeout", 1)
    monkeypatch.setitem(CONFIG, "poll_interval", 0.1)
    with patch('checker.checks.Github') as mock_github:
        mock_repo = MagicMock()
        mock_workflow_run = MagicMock()
        mock_workflow_run.status = "completed"
        mock_workflow_run.conclusion = "failure"

        mock_runs_page = MagicMock()
        mock_runs_page.totalCount = 1
        mock_runs_page.__getitem__.return_value = mock_workflow_run

        mock_repo.get_workflow_runs.return_value = mock_runs_page
        mock_repo.get_workflow_run.return_value = mock_workflow_run

        mock_github_instance = mock_github.return_value
        mock_github_instance.get_repo.return_value = mock_repo

        assert check_tests_passed("owner/repo", "commit_sha", "fake_token") is False


def test_check_tests_passed_workflow_not_found(monkeypatch):
    with patch('checker.checks.Github') as mock_github:
        monkeypatch.setitem(CONFIG, "poll_interval", 0.1)

        mock_repo = MagicMock()
        mock_runs_page = MagicMock()
        mock_runs_page.totalCount = 0

        mock_repo.get_workflow_runs.return_value = mock_runs_page

        mock_github_instance = mock_github.return_value
        mock_github_instance.get_repo.return_value = mock_repo

        assert check_tests_passed("owner/repo", "commit_sha", "fake_token") is False


def test_check_tests_passed_timeout(monkeypatch):
    with patch('checker.checks.Github') as mock_github:
        monkeypatch.setitem(CONFIG, "poll_interval", 0.1)
        monkeypatch.setitem(CONFIG, "timeout", 0.5)

        mock_repo = MagicMock()
        mock_workflow_run = MagicMock()
        mock_workflow_run.status = "in_progress"

        mock_runs_page = MagicMock()
        mock_runs_page.totalCount = 1
        mock_runs_page.__getitem__.return_value = mock_workflow_run

        mock_repo.get_workflow_runs.return_value = mock_runs_page
        mock_repo.get_workflow_run.return_value = mock_workflow_run

        mock_github_instance = mock_github.return_value
        mock_github_instance.get_repo.return_value = mock_repo

        assert check_tests_passed("owner/repo", "commit_sha", "fake_token") is False
