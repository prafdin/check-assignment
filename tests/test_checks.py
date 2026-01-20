import pytest
from unittest.mock import patch, MagicMock
from checker.checks import check_workflow_run_success, CONFIG


def test_check_workflow_run_success_success():
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

def test_check_workflow_run_success_failure():
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
        monkeypatch.setitem(CONFIG, "workflow_poll_interval", 0.1)

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

        monkeypatch.setitem(CONFIG, "workflow_poll_interval", 0.1)
        monkeypatch.setitem(CONFIG, "workflow_timeout", 0.5)
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
