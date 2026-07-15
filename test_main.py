import unittest
import json
import os
import shutil
import tempfile
from unittest.mock import patch
from datetime import datetime
from pathlib import Path

from main import (
    BackupRotator,
    parse_retention_policy,
    load_config,
    resolve_settings,
    DEFAULT_RETENTION_POLICY,
)


class TestBackupRotator(unittest.TestCase):
    """
    Unit tests for the BackupRotator class, using real temporary files.

    Unit-Tests für die Klasse BackupRotator mit echten temporären Dateien.
    """

    def setUp(self) -> None:
        """Erstellt ein echtes temporäres Verzeichnis mit einer DB-Datei."""
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp_dir, ignore_errors=True)
        self.db_path = self.tmp_dir / "test_db.sqlite"
        self.db_path.write_bytes(b"SQLite format 3\x00")  # Minimaler DB-Inhalt.
        self.backup_dir = self.tmp_dir / "backups"

    def _make_backup_files(self, datetimes):
        """Erstellt echte Sicherungsdateien mit den Zeitstempeln aus datetimes."""
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        for dt in datetimes:
            name = f"test_db_{dt.strftime('%Y%m%d_%H%M%S')}.sqlite"
            (self.backup_dir / name).write_bytes(b"backup")

    def _remaining(self):
        """Namen der noch vorhandenen Sicherungsdateien."""
        return sorted(p.name for p in self.backup_dir.iterdir())

    def test_init_success(self) -> None:
        """Erfolgreiche Initialisierung erstellt das Sicherungsverzeichnis."""
        policy = {'daily': 7}
        rotator = BackupRotator(self.db_path, self.backup_dir, policy)
        self.assertEqual(rotator.db_path, self.db_path)
        self.assertEqual(rotator.backup_dir, self.backup_dir)
        self.assertEqual(rotator.retention_policy, policy)
        self.assertTrue(self.backup_dir.is_dir())  # mkdir wurde ausgeführt.

    def test_init_db_not_found(self) -> None:
        """Ein fehlender Datenbankpfad löst FileNotFoundError aus."""
        missing = self.tmp_dir / "does_not_exist.sqlite"
        with self.assertRaises(FileNotFoundError):
            BackupRotator(missing, self.backup_dir, {'daily': 7})

    def test_perform_backup(self) -> None:
        """perform_backup kopiert die DB in eine korrekt benannte Sicherungsdatei."""
        with patch('main.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2023, 10, 27, 10, 30, 0)
            mock_datetime.strptime = datetime.strptime
            rotator = BackupRotator(self.db_path, self.backup_dir, {'daily': 7})
            result_path = rotator.perform_backup()

        expected = self.backup_dir / "test_db_20231027_103000.sqlite"
        self.assertEqual(result_path, expected)
        self.assertTrue(expected.is_file())  # Datei wurde real erzeugt.
        self.assertEqual(expected.read_bytes(), self.db_path.read_bytes())  # Inhalt kopiert.

    def test_perform_rotation_daily(self) -> None:
        """
        Tägliche Rotation behält eine Sicherung pro Kalendertag (daily=4) und löscht
        ältere sowie zusätzliche Sicherungen desselben Tages.
        """
        datetimes = [
            datetime(2023, 10, 27, 11, 0, 0),  # heute, 11:00 (behalten)
            datetime(2023, 10, 27, 10, 0, 0),  # heute, 10:00 (gelöscht: nur eine pro Tag)
            datetime(2023, 10, 26, 12, 0, 0),  # behalten
            datetime(2023, 10, 25, 12, 0, 0),  # behalten
            datetime(2023, 10, 24, 12, 0, 0),  # behalten (4. Tag)
            datetime(2023, 10, 20, 12, 0, 0),  # gelöscht
            datetime(2023, 10, 19, 12, 0, 0),  # gelöscht
        ]
        self._make_backup_files(datetimes)

        with patch('main.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2023, 10, 27, 12, 0, 0)
            mock_datetime.strptime = datetime.strptime
            mock_datetime.fromtimestamp = datetime.fromtimestamp
            BackupRotator(self.db_path, self.backup_dir, {'daily': 4}).perform_rotation()

        expected_remaining = sorted([
            "test_db_20231027_110000.sqlite",
            "test_db_20231026_120000.sqlite",
            "test_db_20231025_120000.sqlite",
            "test_db_20231024_120000.sqlite",
        ])
        self.assertEqual(self._remaining(), expected_remaining)

    def test_perform_rotation_weekly_monthly(self) -> None:
        """
        Kombinierte Rotation behält je Zeitraum die neueste Sicherung:
        daily=2, weekly=3 (je ISO-Woche), monthly=3 (je Kalendermonat).
        """
        datetimes = [
            datetime(2023, 10, 27, 11, 0, 0),  # daily
            datetime(2023, 10, 26, 11, 0, 0),  # daily
            datetime(2023, 10, 20, 11, 0, 0),  # weekly
            datetime(2023, 10, 13, 11, 0, 0),  # weekly
            datetime(2023, 10, 6, 11, 0, 0),   # weekly
            datetime(2023, 9, 29, 11, 0, 0),   # monthly (neueste im September)
            datetime(2023, 9, 20, 11, 0, 0),   # gelöscht (September bereits abgedeckt)
            datetime(2023, 8, 20, 11, 0, 0),   # monthly
            datetime(2023, 7, 20, 11, 0, 0),   # monthly
            datetime(2023, 6, 20, 11, 0, 0),   # gelöscht
            datetime(2023, 5, 20, 11, 0, 0),   # gelöscht
        ]
        self._make_backup_files(datetimes)

        with patch('main.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2023, 10, 27, 12, 0, 0)
            mock_datetime.strptime = datetime.strptime
            mock_datetime.fromtimestamp = datetime.fromtimestamp
            policy = {'daily': 2, 'weekly': 3, 'monthly': 3}
            BackupRotator(self.db_path, self.backup_dir, policy).perform_rotation()

        expected_remaining = sorted([
            "test_db_20231027_110000.sqlite",
            "test_db_20231026_110000.sqlite",
            "test_db_20231020_110000.sqlite",
            "test_db_20231013_110000.sqlite",
            "test_db_20231006_110000.sqlite",
            "test_db_20230929_110000.sqlite",
            "test_db_20230820_110000.sqlite",
            "test_db_20230720_110000.sqlite",
        ])
        self.assertEqual(self._remaining(), expected_remaining)

    def test_parse_retention_policy_valid(self) -> None:
        """Ein gültiger Richtlinien-String wird korrekt geparst."""
        self.assertEqual(
            parse_retention_policy("daily=7,weekly=4,monthly=12"),
            {'daily': 7, 'weekly': 4, 'monthly': 12},
        )

    def test_parse_retention_policy_invalid(self) -> None:
        """Ungültige Richtlinien-Strings lösen ValueError aus."""
        with self.assertRaises(ValueError):
            parse_retention_policy("daily=7,weeklyx4")
        with self.assertRaises(ValueError):
            parse_retention_policy("daily=seven")


class TestConfigFile(unittest.TestCase):
    """
    Test cases for loading and applying the JSON configuration file.

    Testfälle für das Laden und Anwenden der JSON-Konfigurationsdatei.
    """

    def _write_config(self, data):
        """Schreibt data als JSON in eine temporäre Datei und gibt den Pfad zurück."""
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f)
        self.addCleanup(lambda: Path(path).unlink(missing_ok=True))
        return path

    def test_load_config_reads_known_keys(self) -> None:
        """load_config liest bekannte Schlüssel und verwirft unbekannte."""
        path = self._write_config({
            "db_path": "/data/app.sqlite",
            "backup_dir": "/data/backups",
            "retention_policy": {"daily": 5, "weekly": 2},
            "unknown": "dropped",
        })
        config = load_config(path)
        self.assertEqual(config["db_path"], "/data/app.sqlite")
        self.assertEqual(config["backup_dir"], "/data/backups")
        self.assertEqual(config["retention_policy"], {"daily": 5, "weekly": 2})
        self.assertNotIn("unknown", config)

    def test_load_config_rejects_non_object(self) -> None:
        """load_config lehnt JSON ab, das kein Objekt ist."""
        path = self._write_config([1, 2, 3])
        with self.assertRaises(ValueError):
            load_config(path)

    def test_load_config_rejects_bad_retention(self) -> None:
        """load_config lehnt ein retention_policy ab, das kein Objekt ist."""
        path = self._write_config({"retention_policy": "daily=7"})
        with self.assertRaises(ValueError):
            load_config(path)

    def test_load_config_missing_file(self) -> None:
        """load_config wirft FileNotFoundError bei fehlender Datei."""
        with self.assertRaises(FileNotFoundError):
            load_config("/nonexistent/rotator.json")

    def test_resolve_settings_defaults(self) -> None:
        """Ohne Config und CLI gilt die Standard-Aufbewahrungsrichtlinie."""
        settings = resolve_settings({}, {})
        self.assertIsNone(settings["db_path"])
        self.assertIsNone(settings["backup_dir"])
        self.assertEqual(settings["retention_policy"], DEFAULT_RETENTION_POLICY)

    def test_resolve_settings_precedence(self) -> None:
        """CLI überschreibt Config, Config überschreibt Defaults; None wird ignoriert."""
        config = {
            "db_path": "/cfg/app.sqlite",
            "backup_dir": "/cfg/backups",
            "retention_policy": {"daily": 3},
        }
        cli = {"db_path": "/cli/app.sqlite", "backup_dir": None, "retention_policy": None}
        settings = resolve_settings(cli, config)
        self.assertEqual(settings["db_path"], "/cli/app.sqlite")   # CLI gewinnt
        self.assertEqual(settings["backup_dir"], "/cfg/backups")   # Config (CLI war None)
        self.assertEqual(settings["retention_policy"], {"daily": 3})  # Config

    def test_config_applied_to_rotator(self) -> None:
        """Ein aus Config-Werten gebauter Rotator übernimmt die Aufbewahrungsrichtlinie."""
        tmp_dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp_dir, ignore_errors=True)
        db_path = tmp_dir / "app.sqlite"
        db_path.write_bytes(b"SQLite format 3\x00")
        backup_dir = tmp_dir / "backups"

        config = load_config(self._write_config({
            "db_path": str(db_path),
            "backup_dir": str(backup_dir),
            "retention_policy": {"daily": 9, "weekly": 1},
        }))
        settings = resolve_settings({}, config)
        rotator = BackupRotator(
            Path(settings["db_path"]),
            Path(settings["backup_dir"]),
            settings["retention_policy"],
        )
        self.assertEqual(rotator.retention_policy, {"daily": 9, "weekly": 1})
        self.assertTrue(backup_dir.is_dir())


if __name__ == '__main__':
    unittest.main()
