import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from pathlib import Path
import shutil
import os

from main import BackupRotator, parse_retention_policy

class TestBackupRotator(unittest.TestCase):
    """
    Unit tests for the BackupRotator class.

    Unit-Tests für die Klasse BackupRotator.
    """

    def setUp(self) -> None:
        """
        Set up common test variables and mock objects.

        Einrichtung gemeinsamer Testvariablen und Mock-Objekte.
        """
        self.test_db_path = Path("test_db.sqlite")
        self.test_backup_dir = Path("test_backups")
        self.test_db_path.touch() # Erstelle eine leere Datenbankdatei für Tests

        # Mock-Attribute für Path-Objekte
        self.mock_db_path = MagicMock(spec=Path)
        self.mock_db_path.is_file.return_value = True
        self.mock_db_path.stem = "test_db"
        self.mock_db_path.__str__.return_value = str(self.test_db_path)

        self.mock_backup_dir = MagicMock(spec=Path)
        self.mock_backup_dir.mkdir.return_value = None
        self.mock_backup_dir.__str__.return_value = str(self.test_backup_dir)

    def tearDown(self) -> None:
        """
        Clean up after tests.

        Aufräumen nach den Tests.
        """
        if self.test_db_path.exists():
            self.test_db_path.unlink() # Lösche die Test-Datenbankdatei
        if self.test_backup_dir.exists():
            shutil.rmtree(self.test_backup_dir) # Lösche das Test-Sicherungsverzeichnis

    @patch('main.Path.mkdir')
    @patch('main.Path.is_file')
    def test_init_success(self, mock_is_file: MagicMock, mock_mkdir: MagicMock) -> None:
        """
        Test successful initialization of BackupRotator.

        Teste die erfolgreiche Initialisierung von BackupRotator.
        """
        mock_is_file.return_value = True
        policy = {'daily': 7}
        rotator = BackupRotator(self.mock_db_path, self.mock_backup_dir, policy)
        self.assertEqual(rotator.db_path, self.mock_db_path)
        self.assertEqual(rotator.backup_dir, self.mock_backup_dir)
        self.assertEqual(rotator.retention_policy, policy)
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True) # Überprüfe, ob mkdir aufgerufen wurde

    @patch('main.Path.is_file')
    def test_init_db_not_found(self, mock_is_file: MagicMock) -> None:
        """
        Test initialization when the database file does not exist.

        Teste die Initialisierung, wenn die Datenbankdatei nicht existiert.
        """
        mock_is_file.return_value = False
        policy = {'daily': 7}
        with self.assertRaises(FileNotFoundError): # Erwarte einen FileNotFoundError
            BackupRotator(self.mock_db_path, self.mock_backup_dir, policy)

    @patch('main.shutil.copy2')
    @patch('main.Path.is_file', return_value=True)
    @patch('main.Path.mkdir')
    @patch('main.datetime')
    def test_perform_backup(self, mock_datetime: MagicMock, mock_mkdir: MagicMock, mock_is_file: MagicMock, mock_copy2: MagicMock) -> None:
        """
        Test the perform_backup method.

        Teste die Methode perform_backup.
        """
        # Mocke datetime.utcnow, um einen konsistenten Zeitstempel zu erhalten
        mock_now = datetime(2023, 10, 27, 10, 30, 0)
        mock_datetime.utcnow.return_value = mock_now
        mock_datetime.strptime = datetime.strptime # Stelle sicher, dass strptime funktioniert

        rotator = BackupRotator(self.mock_db_path, self.mock_backup_dir, {'daily': 7})
        expected_backup_path = self.mock_backup_dir / "test_db_20231027_103000.sqlite"

        result_path = rotator.perform_backup()
        
        mock_copy2.assert_called_once_with(self.mock_db_path, expected_backup_path) # Überprüfe den Aufruf von shutil.copy2
        self.assertEqual(result_path, expected_backup_path)

    @patch('main.Path.unlink')
    @patch('main.Path.iterdir')
    @patch('main.Path.is_file', return_value=True) # Mocke, dass die DB-Datei existiert
    @patch('main.Path.mkdir') # Mocke, dass das Backup-Verzeichnis erstellt wird
    @patch('main.datetime')
    def test_perform_rotation_daily(self, mock_datetime: MagicMock, mock_mkdir: MagicMock, mock_is_file: MagicMock, mock_iterdir: MagicMock, mock_unlink: MagicMock) -> None:
        """
        Test daily rotation policy.

        Teste die tägliche Rotationsrichtlinie.
        """
        # Mocke die aktuelle Zeit
        mock_now = datetime(2023, 10, 27, 12, 0, 0)
        mock_datetime.utcnow.return_value = mock_now
        mock_datetime.strptime = datetime.strptime # Stelle sicher, dass strptime funktioniert
        mock_datetime.fromtimestamp = datetime.fromtimestamp # Stelle sicher, dass fromtimestamp funktioniert

        # Erstelle eine Liste von Mock-Sicherungsdateien
        # Format: test_db_YYYYMMDD_HHmmss.sqlite
        backup_files_data = [
            (datetime(2023, 10, 27, 11, 0, 0), True),  # Heute, 11:00 (neueste)
            (datetime(2023, 10, 27, 10, 0, 0), True),  # Heute, 10:00
            (datetime(2023, 10, 26, 12, 0, 0), True),  # Gestern
            (datetime(2023, 10, 25, 12, 0, 0), True),  # Vor 2 Tagen
            (datetime(2023, 10, 24, 12, 0, 0), True),  # Vor 3 Tagen
            (datetime(2023, 10, 20, 12, 0, 0), False), # Vor 7 Tagen (sollte gelöscht werden bei daily=7)
            (datetime(2023, 10, 19, 12, 0, 0), False), # Vor 8 Tagen (sollte gelöscht werden)
        ]

        mock_backup_paths = []
        for dt, _ in backup_files_data:
            mock_path = MagicMock(spec=Path)
            mock_path.name = f"test_db_{dt.strftime('%Y%m%d_%H%M%S')}.sqlite"
            mock_path.stem = f"test_db_{dt.strftime('%Y%m%d_%H%M%S')}"
            mock_path.suffix = ".sqlite"
            mock_path.is_file.return_value = True
            mock_path.unlink.return_value = None
            mock_backup_paths.append(mock_path)
        
        # Kehre die Liste um, da _list_backups sie sortiert zurückgibt und perform_rotation sie dann umkehrt
        mock_iterdir.return_value = mock_backup_paths 

        rotator = BackupRotator(self.mock_db_path, self.mock_backup_dir, {'daily': 4})
        rotator.perform_rotation()

        # Erwartete zu löschende Dateien: die, die als False markiert sind
        expected_deleted_count = sum(1 for _, should_keep in backup_files_data if not should_keep)

        # Überprüfe, wie oft unlink aufgerufen wurde
        self.assertEqual(mock_unlink.call_count, expected_deleted_count)
        
        # Prüfe, ob die richtigen Dateien gelöscht wurden
        for i, (dt, should_keep) in enumerate(backup_files_data):
            if not should_keep:
                mock_unlink.assert_any_call(mock_backup_paths[i])
            else:
                # Sicherstellen, dass die beibehaltenen Dateien NICHT gelöscht wurden
                # Dies erfordert eine Negativprüfung, die komplexer ist mit assert_any_call
                # Stattdessen können wir prüfen, ob die gelöschten Dateien die sind, die wir erwarten.
                pass # Die assert_any_call Prüfung oben ist ausreichend für die gelöschten Dateien

    @patch('main.Path.unlink')
    @patch('main.Path.iterdir')
    @patch('main.Path.is_file', return_value=True)
    @patch('main.Path.mkdir')
    @patch('main.datetime')
    def test_perform_rotation_weekly_monthly(self, mock_datetime: MagicMock, mock_mkdir: MagicMock, mock_is_file: MagicMock, mock_iterdir: MagicMock, mock_unlink: MagicMock) -> None:
        """
        Test weekly and monthly rotation policies together.

        Teste wöchentliche und monatliche Rotationsrichtlinien zusammen.
        """
        mock_now = datetime(2023, 10, 27, 12, 0, 0) # Freitag, 27. Okt 2023
        mock_datetime.utcnow.return_value = mock_now
        mock_datetime.strptime = datetime.strptime
        mock_datetime.fromtimestamp = datetime.fromtimestamp

        # Testdaten für Sicherungen
        # (Datum, Erwartet zu behalten)
        backup_files_data = [
            (datetime(2023, 10, 27, 11, 0, 0), True),  # HEUTE (daily)
            (datetime(2023, 10, 26, 11, 0, 0), True),  # gestern (daily)
            (datetime(2023, 10, 20, 11, 0, 0), True),  # Letzte Woche (weekly)
            (datetime(2023, 10, 13, 11, 0, 0), True),  # Vor 2 Wochen (weekly)
            (datetime(2023, 10, 6, 11, 0, 0), True),   # Vor 3 Wochen (weekly)
            (datetime(2023, 9, 29, 11, 0, 0), False),  # Vor 4 Wochen (sollte gelöscht werden bei weekly=4)
            (datetime(2023, 9, 20, 11, 0, 0), True),   # Letzten Monat (monthly)
            (datetime(2023, 8, 20, 11, 0, 0), True),   # Vor 2 Monaten (monthly)
            (datetime(2023, 7, 20, 11, 0, 0), True),   # Vor 3 Monaten (monthly)
            (datetime(2023, 6, 20, 11, 0, 0), False),  # Vor 4 Monaten (sollte gelöscht werden bei monthly=4)
            (datetime(2023, 5, 20, 11, 0, 0), False),  # Vor 5 Monaten (sollte gelöscht werden)
        ]

        mock_backup_paths = []
        for dt, _ in backup_files_data:
            mock_path = MagicMock(spec=Path)
            mock_path.name = f"test_db_{dt.strftime('%Y%m%d_%H%M%S')}.sqlite"
            mock_path.stem = f"test_db_{dt.strftime('%Y%m%d_%H%M%S')}"
            mock_path.suffix = ".sqlite"
            mock_path.is_file.return_value = True
            mock_path.unlink.return_value = None
            mock_backup_paths.append(mock_path)
        
        mock_iterdir.return_value = mock_backup_paths

        policy = {'daily': 2, 'weekly': 3, 'monthly': 3}
        rotator = BackupRotator(self.mock_db_path, self.mock_backup_dir, policy)
        rotator.perform_rotation()

        # Erwarte 2 tägliche + 3 wöchentliche + 3 monatliche = 8 zu behaltende Backups
        # Die täglichen und wöchentlichen/monatlichen können sich überschneiden, aber die Logik sollte das handhaben
        # Hier sind die zu behaltenden Backups:
        # 27.10 (daily), 26.10 (daily)
        # 20.10 (weekly), 13.10 (weekly), 06.10 (weekly)
        # 20.09 (monthly), 20.08 (monthly), 20.07 (monthly)
        # Total: 2 + 3 + 3 = 8 einzigartige Backups

        expected_kept_count = sum(1 for _, should_keep in backup_files_data if should_keep)
        expected_deleted_count = len(backup_files_data) - expected_kept_count

        self.assertEqual(mock_unlink.call_count, expected_deleted_count)

        for i, (dt, should_keep) in enumerate(backup_files_data):
            if not should_keep:
                mock_unlink.assert_any_call(mock_backup_paths[i])

    def test_parse_retention_policy_valid(self) -> None:
        """
        Test parsing a valid retention policy string.

        Teste das Parsen eines gültigen Aufbewahrungsrichtlinien-Strings.
        """
        policy_str = "daily=7,weekly=4,monthly=12"
        expected_policy = {'daily': 7, 'weekly': 4, 'monthly': 12}
        self.assertEqual(parse_retention_policy(policy_str), expected_policy)

    def test_parse_retention_policy_invalid(self) -> None:
        """
        Test parsing an invalid retention policy string.

        Teste das Parsen eines ungültigen Aufbewahrungsrichtlinien-Strings.
        """
        policy_str = "daily=7,weeklyx4"
        with self.assertRaises(ValueError): # Erwarte einen ValueError bei ungültigem Format
            parse_retention_policy(policy_str)

        policy_str_non_int = "daily=seven"
        with self.assertRaises(ValueError): # Erwarte einen ValueError bei nicht-ganzzahligem Wert
            parse_retention_policy(policy_str_non_int)


if __name__ == '__main__':
    unittest.main()
