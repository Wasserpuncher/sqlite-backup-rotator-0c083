# SQLite Backup Rotator

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/github/license/Wasserpuncher/sqlite-backup-rotator-0c083)
![CI Status](https://github.com/Wasserpuncher/sqlite-backup-rotator-0c083/workflows/Python%20application/badge.svg)

## 📚 Project Description

The `sqlite-backup-rotator` is an enterprise-ready, open-source command-line tool designed to automate the backup and rotation of local SQLite database files. It provides a robust solution for ensuring data integrity and availability by regularly creating backups and intelligently managing their retention based on configurable policies (e.g., keeping the last 7 daily, 4 weekly, and 12 monthly backups).

This project aims to be simple, reliable, and easily integratable into various systems, from small personal projects to larger enterprise applications requiring local data persistence with strong backup strategies.

## ✨ Features

*   **Automated Backups**: Easily create timestamped backups of your SQLite database files.
*   **Configurable Retention Policies**: Define how many daily, weekly, and monthly backups to keep.
*   **Intelligent Rotation**: Automatically deletes old backups that fall outside the specified retention policy.
*   **Robust Error Handling**: Logs errors and provides informative messages.
*   **Command-Line Interface**: Simple to use via command-line arguments.
*   **Pythonic & Type-Hinted**: Developed with modern Python best practices, including OOP and type hints.
*   **Bilingual Documentation**: Comprehensive documentation available in both English and German.
*   **Unit Tested**: High test coverage to ensure reliability.
*   **CI/CD Integration**: GitHub Actions workflow for automated testing.

## 🚀 Installation

### Prerequisites

*   Python 3.8 or higher

### Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Wasserpuncher/sqlite-backup-rotator-0c083.git
    cd sqlite-backup-rotator
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows:
    # .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## 💡 Usage

To run the backup and rotation process, execute the `main.py` script with the required arguments:

```bash
python main.py \
  --db-path /path/to/your/database.sqlite \
  --backup-dir /path/to/your/backup/directory \
  --retention-policy "daily=7,weekly=4,monthly=12"
```

### Arguments:

*   `--config` (optional): Path to a JSON configuration file (see below). Defaults to `rotator.json` in the current directory if present.
*   `--db-path`: The path to your source SQLite database file. Required unless provided via the config file.
*   `--backup-dir`: The path to the directory where backups will be stored. Required unless provided via the config file.
*   `--retention-policy` (optional): A comma-separated string defining the retention policy. Default is `"daily=7,weekly=4,monthly=12"`.
    *   `daily=N`: Keep the last `N` daily backups.
    *   `weekly=M`: Keep the last `M` weekly backups.
    *   `monthly=P`: Keep the last `P` monthly backups.

    *Note: The rotation logic prioritizes daily, then weekly, then monthly. This means a backup might be kept if it satisfies any of the retention criteria.*

### Configuration file

Instead of passing every parameter on the command line, you can store the settings in a JSON configuration file (standard library only, no extra dependencies). By default the tool loads `rotator.json` from the current directory if it exists; use `--config` to point at a different file.

```json
{
  "db_path": "/home/user/app/data.sqlite",
  "backup_dir": "/home/user/backups",
  "retention_policy": { "daily": 7, "weekly": 4, "monthly": 12 }
}
```

Supported keys:

*   `db_path`: Path to the source SQLite database file.
*   `backup_dir`: Directory where backups are stored.
*   `retention_policy`: A JSON object with any of `daily`, `weekly`, `monthly` mapped to the number of backups to keep.

Precedence is **built-in defaults < config file < command-line arguments**, so an explicit flag always wins over the config file. Unknown keys are ignored.

```bash
# Use the default rotator.json in the current directory
python main.py

# Use an explicit config file, overriding the retention policy on the command line
python main.py --config configs/prod.json --retention-policy "daily=14,weekly=8,monthly=24"
```

### Example:

Imagine you have a database at `/home/user/app/data.sqlite` and you want to store backups in `/home/user/backups`. You want to keep the last 5 daily backups, 2 weekly backups, and 6 monthly backups.

```bash
python main.py \
  --db-path /home/user/app/data.sqlite \
  --backup-dir /home/user/backups \
  --retention-policy "daily=5,weekly=2,monthly=6"
```

### Scheduling

For automated, regular backups, you can schedule this script using tools like `cron` (Linux/macOS) or Task Scheduler (Windows).

**Cron example (daily at 2 AM):**

1.  Open your crontab for editing:
    ```bash
    crontab -e
    ```
2.  Add the following line (adjust paths as necessary, including the full path to your Python executable and script):
    ```cron
    0 2 * * * /usr/bin/python3 /path/to/sqlite-backup-rotator/main.py --db-path /path/to/your/database.sqlite --backup-dir /path/to/your/backup/directory --retention-policy "daily=7,weekly=4,monthly=12" >> /var/log/sqlite_backup.log 2>&1
    ```

## 🧪 Running Tests

To ensure everything is working correctly, you can run the unit tests:

```bash
python -m unittest discover
```

## 🤝 Contributing

We welcome contributions to the `sqlite-backup-rotator` project! Please refer to the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to get started.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 📞 Contact

For questions, suggestions, or issues, please open an issue on the GitHub repository.
