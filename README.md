# Check Assignment

This project provides a GitHub Action and associated Python scripts for automatically checking assignments.

## Installation

To set up the project locally for development and testing, follow these steps:

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/prafdin/check-assignment.git
    cd check-assignment
    ```

2.  **Install in editable mode**:
    This will install the project as a package in your Python environment, making the `checker` modules and scripts available. This mode is ideal for local development, as changes to the source code are immediately reflected without needing to reinstall.
    ```bash
    pip install -e .
    ```
    For production environments or CI/CD pipelines where the code is not actively being developed, a normal installation (`pip install .`) is typically preferred. This performs a standard installation, copying the project files into your Python environment's `site-packages` directory.

## Usage

Once the project is installed in editable mode, you should run the scripts as Python modules. This is the recommended way to ensure that imports within the project work correctly.

### Running a check script

You can run a script using the `python -m` flag, followed by the script's module path.

**General format**:
```bash
python -m scripts.<script_name> [arguments]
```

#### `check_webhooks_devops_assignment`

This script runs checks specifically for the webhooks DevOps assignment.

**Arguments**:
*   `--repo_url`: URL of the student's repository.
*   `--id`: The ID for the URL.
*   `--proxy`: The PROXY for the URL.
*   `--sa_login`: GitHub service account login.
*   `--sa_mail`: GitHub service account mail.

**Example**:
```bash
python -m scripts.check_webhooks_devops_assignment --repo_url "https://github.com/student/repo.git" --id "student_id" --proxy "example.com" --sa_login "github_user" --sa_mail "user@example.com"
```

**Example**:
```bash
python -m scripts.new_assignment_check --repo_url "https://github.com/student/new-repo.git" --id "new_id" --proxy "new-example.com" --sa_login "github_user" --sa_mail "user@example.com"
```

### Running Tests

You can run the project's tests using `pytest`:

```bash
pytest
```
To run tests excluding those marked as 'slow':
```bash
pytest -m "not slow"
```
