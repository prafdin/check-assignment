import pytest
from checker.checks import check_required_workflow_files

@pytest.mark.slow
def test_check_required_workflow_files_integration():
    """
    This is an integration test that checks for the existence of workflow files in a real public repository.
    It is marked as 'slow' and should be run as part of the integration test suite.
    """
    repo_url = "https://github.com/prafdin/check-assignment-tests.git"
    branch_name = "main"

    # Test for an existing file
    existing_files = ["README.md"]
    assert check_required_workflow_files(repo_url, branch_name, existing_files) is True

    # Test for a non-existent file
    non_existent_files = ["non-existent-file.txt"]
    assert check_required_workflow_files(repo_url, branch_name, non_existent_files) is False

    # Test for a mix of existing and non-existent files
    mixed_files = ["README.md", "non-existent-file.txt"]
    assert check_required_workflow_files(repo_url, branch_name, mixed_files) is False
