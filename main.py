import argparse
import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Konfiguriere das Logging für die Anwendung
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BackupRotator:
    """
    Manages the backup and rotation of a single SQLite database file.

    Verwaltet die Sicherung und Rotation einer einzelnen SQLite-Datenbankdatei.
    """

    def __init__(
        self, db_path: Path, backup_dir: Path, retention_policy: Dict[str, int]
    ) -> None:
        """
        Initializes the BackupRotator with database path, backup directory, and retention policy.

        Initialisiert den BackupRotator mit dem Datenbankpfad, dem Sicherungsverzeichnis und der Aufbewahrungsrichtlinie.

        Args:
            db_path (Path): The path to the source SQLite database file.
                            Der Pfad zur Quell-SQLite-Datenbankdatei.
            backup_dir (Path): The directory where backups will be stored.
                                Das Verzeichnis, in dem Sicherungen gespeichert werden.
            retention_policy (Dict[str, int]): A dictionary defining the retention policy.
                                                Ein Wörterbuch, das die Aufbewahrungsrichtlinie definiert.
                                                Example: {'daily': 7, 'weekly': 4, 'monthly': 12}
        """
        self.db_path = db_path
        self.backup_dir = backup_dir
        self.retention_policy = retention_policy

        # Stelle sicher, dass das Sicherungsverzeichnis existiert
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Prüfe, ob die Datenbankdatei existiert
        if not self.db_path.is_file():
            logger.error(f"Die Quelldatenbank existiert nicht: {self.db_path}")
            raise FileNotFoundError(f"Source database not found: {self.db_path}")

    def _get_timestamp_str(self, dt: Optional[datetime] = None) -> str:
        """
        Generates a timestamp string for backup filenames.

        Erzeugt einen Zeitstempel-String für Sicherungsdateinamen.

        Args:
            dt (Optional[datetime]): The datetime object to use. Defaults to current UTC time.
                                     Das zu verwendende Datetime-Objekt. Standard ist die aktuelle UTC-Zeit.

        Returns:
            str: A formatted timestamp string (YYYYMMDD_HHmmss).
                 Ein formatierter Zeitstempel-String (JJJJMMTT_HHmmss).
        """
        if dt is None:
            dt = datetime.utcnow() # Verwende UTC für Konsistenz
        return dt.strftime("%Y%m%d_%H%M%S")

    def _get_backup_filename(self, dt: Optional[datetime] = None) -> Path:
        """
        Generates a full path for a new backup file.

        Erzeugt einen vollständigen Pfad für eine neue Sicherungsdatei.

        Args:
            dt (Optional[datetime]): The datetime object to use for the timestamp. Defaults to current UTC time.
                                     Das zu verwendende Datetime-Objekt für den Zeitstempel. Standard ist die aktuelle UTC-Zeit.

        Returns:
            Path: The full path for the backup file.
                  Der vollständige Pfad für die Sicherungsdatei.
        """
        db_name = self.db_path.stem # Hole den Namen der Datenbankdatei ohne Erweiterung
        timestamp = self._get_timestamp_str(dt) # Erzeuge den Zeitstempel-String
        return self.backup_dir / f"{db_name}_{timestamp}.sqlite"

    def _list_backups(self) -> List[Path]:
        """
        Lists all existing backups for the configured database, sorted by creation time.

        Listet alle vorhandenen Sicherungen für die konfigurierte Datenbank auf, sortiert nach Erstellungszeit.

        Returns:
            List[Path]: A list of paths to backup files.
                        Eine Liste von Pfaden zu Sicherungsdateien.
        """
        # Muster für Sicherungsdateien: db_name_YYYYMMDD_HHmmss.sqlite
        db_name_prefix = self.db_path.stem + "_"
        backups = [
            p for p in self.backup_dir.iterdir() 
            if p.is_file() and p.name.startswith(db_name_prefix) and p.suffix == ".sqlite"
        ]
        
        # Sortiere Sicherungen nach Datum/Uhrzeit im Dateinamen
        # Extrahiere den Zeitstempel und konvertiere ihn in ein datetime-Objekt
        def get_datetime_from_filename(path: Path) -> datetime:
            try:
                # Beispiel: 'mydatabase_20231027_103000.sqlite'
                timestamp_str = path.stem.split('_')[-2] + '_' + path.stem.split('_')[-1]
                return datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
            except (ValueError, IndexError):
                # Fallback für falsch benannte Dateien oder wenn der Zeitstempel fehlt
                logger.warning(f"Kann Zeitstempel aus Dateiname {path.name} nicht extrahieren. Verwende Änderungszeit.")
                return datetime.fromtimestamp(path.stat().st_mtime) # Fallback zur Änderungszeit

        return sorted(backups, key=get_datetime_from_filename)

    def perform_backup(self) -> Path:
        """
        Performs a backup of the SQLite database.

        Führt eine Sicherung der SQLite-Datenbank durch.

        Returns:
            Path: The path to the newly created backup file.
                  Der Pfad zur neu erstellten Sicherungsdatei.
        """
        backup_file_path = self._get_backup_filename() # Erzeuge den Pfad für die neue Sicherungsdatei
        try:
            shutil.copy2(self.db_path, backup_file_path) # Kopiere die Datenbankdatei
            logger.info(f"Datenbank erfolgreich gesichert nach: {backup_file_path}")
            return backup_file_path
        except Exception as e:
            logger.error(f"Fehler beim Sichern der Datenbank {self.db_path}: {e}")
            raise

    def perform_rotation(self) -> None:
        """
        Performs rotation of backups according to the retention policy.

        Führt die Rotation von Sicherungen gemäß der Aufbewahrungsrichtlinie durch.
        """
        logger.info("Starte Sicherungsrotation...")
        all_backups = self._list_backups() # Hole alle vorhandenen Sicherungen
        if not all_backups:
            logger.info("Keine Sicherungen zum Rotieren gefunden.")
            return

        # Umkehrung der Liste, um mit den neuesten zu beginnen
        # Dies ist wichtig, da wir von den neuesten Sicherungen zählen, die wir behalten wollen
        all_backups.reverse()

        kept_backups = set() # Set zur Speicherung der Pfade der zu behaltenden Sicherungen
        now = datetime.utcnow() # Aktuelle UTC-Zeit für Vergleiche

        # Funktion zum Extrahieren des Datetime-Objekts aus dem Dateinamen
        def get_dt_from_backup_path(backup_path: Path) -> datetime:
            timestamp_str = backup_path.stem.split('_')[-2] + '_' + backup_path.stem.split('_')[-1]
            return datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")

        # --- Tägliche Rotation ---
        if 'daily' in self.retention_policy:
            daily_to_keep = self.retention_policy['daily'] # Anzahl der täglichen Sicherungen, die behalten werden sollen
            logger.debug(f"Prüfe tägliche Rotation (behalte {daily_to_keep} Tage)...")
            kept_daily_count = 0
            last_kept_day: Optional[datetime] = None

            for backup in all_backups:
                backup_dt = get_dt_from_backup_path(backup) # Zeitstempel der Sicherung
                # Wenn dies die erste tägliche Sicherung ist ODER ein neuer Tag begonnen hat
                if last_kept_day is None or (now - backup_dt).days < daily_to_keep and backup_dt.date() != last_kept_day.date():
                    kept_backups.add(backup) # Füge die Sicherung zu den zu behaltenden hinzu
                    kept_daily_count += 1
                    last_kept_day = backup_dt
                    if kept_daily_count >= daily_to_keep: # Wenn genügend tägliche Sicherungen gefunden wurden, beende die Schleife
                        break
        
        # --- Wöchentliche Rotation ---
        if 'weekly' in self.retention_policy:
            weekly_to_keep = self.retention_policy['weekly'] # Anzahl der wöchentlichen Sicherungen, die behalten werden sollen
            logger.debug(f"Prüfe wöchentliche Rotation (behalte {weekly_to_keep} Wochen)...")
            kept_weekly_count = 0
            last_kept_week: Optional[int] = None # Speichert die Kalenderwoche des letzten behaltenen Backups

            for backup in all_backups:
                backup_dt = get_dt_from_backup_path(backup) # Zeitstempel der Sicherung
                # Nur Sicherungen außerhalb des täglichen Aufbewahrungszeitraums berücksichtigen
                if backup not in kept_backups and (now - backup_dt).days >= self.retention_policy.get('daily', 0):
                    # Ein 'Wochen'-Kriterium kann der ISO-Woche oder dem Start des Kalendermonats folgen
                    # Hier verwenden wir die ISO-Woche (Mo-So)
                    current_week = backup_dt.isocalendar()[1] # isocalendar() gibt (Jahr, Woche, Wochentag) zurück
                    current_year = backup_dt.isocalendar()[0]

                    if last_kept_week is None or (current_year, current_week) != last_kept_week:
                        kept_backups.add(backup)
                        kept_weekly_count += 1
                        last_kept_week = (current_year, current_week)
                        if kept_weekly_count >= weekly_to_keep:
                            break

        # --- Monatliche Rotation ---
        if 'monthly' in self.retention_policy:
            monthly_to_keep = self.retention_policy['monthly'] # Anzahl der monatlichen Sicherungen, die behalten werden sollen
            logger.debug(f"Prüfe monatliche Rotation (behalte {monthly_to_keep} Monate)...")
            kept_monthly_count = 0
            last_kept_month: Optional[int] = None # Speichert den Monat des letzten behaltenen Backups
            last_kept_year_month: Optional[tuple[int, int]] = None # Speichert (Jahr, Monat) des letzten behaltenen Backups

            for backup in all_backups:
                backup_dt = get_dt_from_backup_path(backup) # Zeitstempel der Sicherung
                # Nur Sicherungen außerhalb des täglichen und wöchentlichen Aufbewahrungszeitraums berücksichtigen
                if backup not in kept_backups and 
                   (now - backup_dt).days >= self.retention_policy.get('daily', 0) and 
                   (now - backup_dt).days >= self.retention_policy.get('weekly', 0) * 7:
                    
                    current_year_month = (backup_dt.year, backup_dt.month)

                    if last_kept_year_month is None or current_year_month != last_kept_year_month:
                        kept_backups.add(backup)
                        kept_monthly_count += 1
                        last_kept_year_month = current_year_month
                        if kept_monthly_count >= monthly_to_keep:
                            break

        # Lösche Sicherungen, die nicht in 'kept_backups' enthalten sind
        for backup in reversed(all_backups): # Gehe die Liste erneut durch, um zu löschen
            if backup not in kept_backups:
                try:
                    backup.unlink() # Lösche die Datei
                    logger.info(f"Alte Sicherung gelöscht: {backup}")
                except OSError as e:
                    logger.error(f"Fehler beim Löschen der Sicherung {backup}: {e}")

        logger.info("Sicherungsrotation abgeschlossen.")

def parse_retention_policy(policy_str: str) -> Dict[str, int]:
    """
    Parses a retention policy string into a dictionary.

    Analysiert einen Aufbewahrungsrichtlinien-String in ein Wörterbuch.

    Args:
        policy_str (str): A string like 'daily=7,weekly=4,monthly=12'.
                          Ein String wie 'daily=7,weekly=4,monthly=12'.

    Returns:
        Dict[str, int]: The parsed retention policy.
                        Die analysierte Aufbewahrungsrichtlinie.
    """
    policy = {}
    try:
        for item in policy_str.split(','):
            key, value = item.split('=')
            policy[key.strip()] = int(value.strip())
    except ValueError:
        raise ValueError("Ungültiges Format für die Aufbewahrungsrichtlinie. Erwartet: 'daily=N,weekly=M,monthly=P'.")
    return policy

def main() -> None:
    """
    Main function to parse arguments and run the backup rotator.

    Hauptfunktion zum Parsen von Argumenten und Ausführen des Backup-Rotators.
    """
    parser = argparse.ArgumentParser(
        description="Automatischer SQLite-Datenbank-Backup-Rotator."
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        required=True,
        help="Pfad zur SQLite-Quelldatenbankdatei."
    )
    parser.add_argument(
        "--backup-dir",
        type=Path,
        required=True,
        help="Verzeichnis, in dem Sicherungen gespeichert werden sollen."
    )
    parser.add_argument(
        "--retention-policy",
        type=str,
        default="daily=7,weekly=4,monthly=12",
        help="Aufbewahrungsrichtlinie (z.B. 'daily=7,weekly=4,monthly=12')."
    )

    args = parser.parse_args()

    try:
        retention_policy = parse_retention_policy(args.retention_policy)
        rotator = BackupRotator(args.db_path, args.backup_dir, retention_policy)
        
        logger.info(f"Starte Sicherung für {args.db_path}...")
        new_backup_path = rotator.perform_backup()
        logger.info(f"Sicherung erstellt: {new_backup_path}")
        
        logger.info("Führe Sicherungsrotation durch...")
        rotator.perform_rotation()
        logger.info("Sicherungs- und Rotationsvorgang abgeschlossen.")

    except FileNotFoundError as e:
        logger.error(f"Fehler: {e}")
        exit(1)
    except ValueError as e:
        logger.error(f"Konfigurationsfehler: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
        exit(1)

if __name__ == "__main__":
    main()
