import pytest
from unittest.mock import patch, MagicMock

from checker.checks import check_app_is_alive, check_event_update_site, CONFIG

from checker.utils import CICommit




def test_event_update_site(requests_mock, monkeypatch):

    app_url = "https://example.ru"

    webhook_url = "git@github.com:example/repo.git"

    app_api = MagicMock()
    app_api.extract_deploy_ref.side_effect = ["old_ref", "new_ref"]

    monkeypatch.setitem(CONFIG, "timeout", 0.1)
    monkeypatch.setitem(CONFIG, "poll_interval", 0.1)

    requests_mock.get(app_url, [

        {"text": 'foo<meta name="deployref" content="20260120012">bar', "status_code": 200},

        {"text": 'foo<meta name="deployref" content="20260120013">bar', "status_code": 200}

    ])



    with patch('checker.checks.CICommit') as mock_commit_class:

        # The __init__ of Commit is now mocked, so it won't run the git clone.

        # We create an instance of the mock class.

        mock_commit_instance = mock_commit_class.return_value

        

        # When check_event_update_site calls commit.push(), it will be using the mock.

        assert check_event_update_site(app_api, app_url, mock_commit_instance) is True

        

        # We can also assert that the push method was called.

        mock_commit_instance.push_to_autotest_branch.assert_called_once()



def test_event_doest_not_update_site(requests_mock, monkeypatch):

    app_url = "https://example.ru"

    webhook_url = "git@github.com:example/repo.git"


    app_api = MagicMock()
    app_api.extract_deploy_ref.side_effect = ["old_ref", "old_ref"]

    monkeypatch.setitem(CONFIG, "timeout", 0.1)
    monkeypatch.setitem(CONFIG, "poll_interval", 0.1)

    requests_mock.get(app_url, [

        {"text": 'foo<meta name="deployref" content="20260120012">bar', "status_code": 200},

        {"text": 'foo<meta name="deployref" content="20260120012">var', "status_code": 200}

    ])



    with patch('checker.checks.CICommit') as mock_commit_class:

        mock_commit_instance = mock_commit_class.return_value

        assert check_event_update_site(app_api, app_url, mock_commit_instance) is False

        mock_commit_instance.push_to_autotest_branch.assert_called_once()





@pytest.mark.slow

def test_commit_push():

    # This test will attempt to push a commit to a real repository.

    # It should only be run if the environment is set up with SSH agent for GitHub.

    # The 'slow' mark indicates it's an integration test.

    ci_commit = CICommit("git@github.com:prafdin/check-assignment-tests.git", "webhooks_devops_assignment", CONFIG)

    ci_commit.push_to_autotest_branch()

    assert True is True
