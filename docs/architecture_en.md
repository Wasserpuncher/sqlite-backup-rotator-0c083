# Architecture Overview: SQLite Backup Rotator

## 1. Introduction

The `sqlite-backup-rotator` is a Python-based command-line tool designed for the automated backup and intelligent rotation of local SQLite database files. Its primary goal is to provide a reliable, easy-to-use, and configurable solution for maintaining database integrity through systematic backups, while preventing excessive disk space usage by applying a flexible retention policy.

## 2. Core Components

The architecture is straightforward, focusing on clarity, modularity, and maintainability. It consists of the following main components:

### 2.1. `main.py`

This is the entry point of the application. It handles command-line argument parsing and orchestrates the backup and rotation process.

*   **`argparse`**: Used to define and parse command-line arguments such as `db-path`, `backup-dir`, and `retention-policy`.
*   **`BackupRotator` Class**: The central class encapsulating the core logic for backup and rotation.
*   **`parse_retention_policy` Function**: A utility function to convert the string-based retention policy from the command line into a structured dictionary for the `BackupRotator`.
*   **Logging**: Utilizes Python's standard `logging` module for clear feedback on operations and error reporting.

### 2.2. `BackupRotator` Class (within `main.py`)

This class is the heart of the application, responsible for executing the backup and rotation logic.

*   **`__init__(self, db_path: Path, backup_dir: Path, retention_policy: Dict[str, int])`**:
    *   Initializes the rotator with the source database path, the destination backup directory, and a dictionary representing the retention policy (e.g., `{'daily': 7, 'weekly': 4, 'monthly': 12}`).
    *   Ensures the backup directory exists and the source database file is accessible.
    *   Uses `pathlib.Path` objects for robust and OS-agnostic file path handling.

*   **`_get_timestamp_str(self, dt: Optional[datetime] = None) -> str`**:
    *   A private helper method to generate a consistent timestamp string (YYYYMMDD_HHmmss) for backup filenames, using UTC for consistency.

*   **`_get_backup_filename(self, dt: Optional[datetime] = None) -> Path`**:
    *   A private helper method to construct the full path for a new backup file based on the database name and a timestamp.

*   **`_list_backups(self) -> List[Path]`**:
    *   Identifies and lists all existing backup files for the specific database within the `backup_dir`.
    *   Parses the timestamp from filenames to sort them chronologically, ensuring correct rotation logic.

*   **`perform_backup(self) -> Path`**:
    *   Executes the actual file copy operation using `shutil.copy2` to preserve metadata.
    *   Generates a unique timestamped filename for the new backup.
    *   Logs the success or failure of the backup operation.

*   **`perform_rotation(self) -> None`**:
    *   This is the core logic for managing old backups.
    *   It retrieves all existing backups and iterates through them in reverse chronological order (newest first).
    *   It applies the retention policy (`daily`, `weekly`, `monthly`) to determine which backups should be kept.
    *   **Daily Retention**: Keeps the specified number of the most recent daily backups (one per day).
    *   **Weekly Retention**: From backups *not* already kept by the daily policy, it keeps the specified number of weekly backups (one per week).
    *   **Monthly Retention**: From backups *not* already kept by daily or weekly policies, it keeps the specified number of monthly backups (one per month).
    *   Backups that do not meet any retention criteria are deleted using `pathlib.Path.unlink()`.
    *   Robust logging is used to track which backups are kept and which are deleted.

## 3. Data Flow

1.  **Initialization**: `main.py` receives `db_path`, `backup_dir`, and `retention_policy_str` from command-line arguments.
2.  **Policy Parsing**: `parse_retention_policy` converts `retention_policy_str` into a dictionary.
3.  **Rotator Instantiation**: An instance of `BackupRotator` is created with the parsed arguments.
4.  **Backup Execution**: `rotator.perform_backup()` is called.
    *   It generates a new backup filename with a timestamp.
    *   It copies the `db_path` file to the new backup location in `backup_dir`.
5.  **Rotation Execution**: `rotator.perform_rotation()` is called.
    *   It calls `_list_backups()` to get all existing backups, sorted chronologically.
    *   It iterates through the sorted backups, identifying those to keep based on the `retention_policy`.
    *   For any backup not marked for retention, it calls `backup.unlink()` to delete the file.

## 4. Error Handling and Logging

*   The application uses Python's standard `logging` module to provide clear output. Info messages report successful operations, and error messages highlight issues (e.g., database not found, permission errors during file deletion).
*   `FileNotFoundError` is raised early if the source database doesn't exist.
*   General `Exception` handling is in place in `main()` to catch unexpected issues during the process, ensuring a graceful exit with an error message.

## 5. Future Enhancements

*   **Configuration File Support**: Implement a `config.json` or `config.ini` to store database paths, backup directories, and retention policies, removing the need for long command-line arguments.
*   **Multiple Database Support**: Extend the tool to manage backups for multiple SQLite databases with individual policies.
*   **Compression**: Add an option to compress backup files (e.g., `.zip`, `.gz`) to save disk space.
*   **Integrity Checks**: Implement optional SQLite `PRAGMA integrity_check` on backups to ensure their validity.
*   **Cloud Storage Integration**: Allow uploading backups to cloud storage services (e.g., S3, Google Drive, Dropbox).
*   **Notification System**: Add hooks for sending notifications (email, Slack, etc.) on success or failure.
*   **Detailed Reporting**: Generate more detailed reports on backups created, deleted, and kept.
*   **Locking Mechanism**: Implement a file-based or process-based lock to prevent multiple instances from running concurrently on the same database.
