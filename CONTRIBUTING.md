# Contributing to SQLite Backup Rotator

We welcome contributions to the `sqlite-backup-rotator` project! Whether it's bug reports, feature requests, documentation improvements, or code contributions, your help is valuable.

Please take a moment to review this document to make the contribution process as smooth as possible.

## How to Contribute

### 1. Reporting Bugs

If you find a bug, please open an issue on the [GitHub Issues page](https://github.com/your-username/sqlite-backup-rotator/issues).

When reporting a bug, please include:

*   A clear and concise description of the bug.
*   Steps to reproduce the behavior.
*   Expected behavior.
*   Actual behavior.
*   Any relevant error messages or logs.
*   Your operating system and Python version.

### 2. Suggesting Enhancements

We're always looking for ways to improve the project. If you have an idea for a new feature or an enhancement to an existing one, please open an issue on the [GitHub Issues page](https://github.com/your-username/sqlite-backup-rotator/issues).

When suggesting an enhancement, please include:

*   A clear and concise description of the proposed feature/enhancement.
*   Why you think it would be valuable to the project.
*   Any potential use cases or examples.

### 3. Code Contributions

We appreciate code contributions! To contribute code, please follow these steps:

1.  **Fork the repository:** Click the "Fork" button at the top right of the [repository page](https://github.com/your-username/sqlite-backup-rotator).

2.  **Clone your forked repository:**
    ```bash
    git clone https://github.com/your-username/sqlite-backup-rotator.git
    cd sqlite-backup-rotator
    ```

3.  **Create a new branch:** Choose a descriptive name for your branch (e.g., `feature/add-config-file`, `bugfix/rotation-logic`).
    ```bash
    git checkout -b feature/your-feature-name
    ```

4.  **Set up your development environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: .\venv\Scripts\activate
    pip install -r requirements.txt
    # Install development dependencies
    pip install pytest flake8
    ```

5.  **Make your changes:**
    *   Ensure your code adheres to the existing style (e.g., use `flake8` to check).
    *   Add type hints where appropriate.
    *   Write clear docstrings for new functions/methods and classes (in English).
    *   Add inline comments in *German* for complex logic to aid understanding, especially for beginners.
    *   Write unit tests for new features or bug fixes. Ensure existing tests still pass.

6.  **Run tests and linting:**
    ```bash
    flake8 .
    python -m unittest discover
    ```
    Ensure all tests pass and there are no linting errors.

7.  **Commit your changes:** Write clear and concise commit messages.
    ```bash
    git add .
    git commit -m "feat: Add configuration file support"
    ```

8.  **Push your branch to your forked repository:**
    ```bash
    git push origin feature/your-feature-name
    ```

9.  **Open a Pull Request (PR):**
    *   Go to the original `sqlite-backup-rotator` repository on GitHub.
    *   You should see a prompt to create a new pull request from your recently pushed branch.
    *   Provide a clear title and description for your PR, explaining the changes you've made and why they are necessary.
    *   Reference any related issues (e.g., `Fixes #123`, `Closes #456`).

### 4. Documentation Improvements

Good documentation is crucial. If you find typos, unclear explanations, or areas that could be better documented, please submit a pull request with your changes. Remember to update both English (`.md`) and German (`_de.md`) documentation files where applicable.

## Code of Conduct

We expect all contributors to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md) (if applicable).

Thank you for contributing to the SQLite Backup Rotator project!
