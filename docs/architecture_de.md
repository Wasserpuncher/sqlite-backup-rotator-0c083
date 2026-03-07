# Architekturübersicht: SQLite Backup Rotator

## 1. Einführung

Der `sqlite-backup-rotator` ist ein Python-basiertes Kommandozeilen-Tool, das für die automatisierte Sicherung und intelligente Rotation lokaler SQLite-Datenbankdateien entwickelt wurde. Sein primäres Ziel ist es, eine zuverlässige, benutzerfreundliche und konfigurierbare Lösung zur Aufrechterhaltung der Datenbankintegrität durch systematische Sicherungen bereitzustellen und gleichzeitig eine übermäßige Nutzung des Speicherplatzes durch die Anwendung einer flexiblen Aufbewahrungsrichtlinie zu verhindern.

## 2. Kernkomponenten

Die Architektur ist geradlinig und konzentriert sich auf Klarheit, Modularität und Wartbarkeit. Sie besteht aus den folgenden Hauptkomponenten:

### 2.1. `main.py`

Dies ist der Einstiegspunkt der Anwendung. Es verarbeitet die Kommandozeilenargumente und orchestriert den Sicherungs- und Rotationsprozess.

*   **`argparse`**: Wird verwendet, um Kommandozeilenargumente wie `db-path`, `backup-dir` und `retention-policy` zu definieren und zu parsen.
*   **`BackupRotator` Klasse**: Die zentrale Klasse, die die Kernlogik für Sicherung und Rotation kapselt.
*   **`parse_retention_policy` Funktion**: Eine Dienstfunktion zur Umwandlung der String-basierten Aufbewahrungsrichtlinie von der Kommandozeile in ein strukturiertes Wörterbuch für den `BackupRotator`.
*   **Logging**: Verwendet das Standard-`logging`-Modul von Python für klares Feedback zu Operationen und zur Fehlerberichterstattung.

### 2.2. `BackupRotator` Klasse (innerhalb von `main.py`)

Diese Klasse ist das Herzstück der Anwendung und verantwortlich für die Ausführung der Sicherungs- und Rotationslogik.

*   **`__init__(self, db_path: Path, backup_dir: Path, retention_policy: Dict[str, int])`**:
    *   Initialisiert den Rotator mit dem Pfad zur Quelldatenbank, dem Ziel-Sicherungsverzeichnis und einem Wörterbuch, das die Aufbewahrungsrichtlinie darstellt (z. B. `{'daily': 7, 'weekly': 4, 'monthly': 12}`).
    *   Stellt sicher, dass das Sicherungsverzeichnis existiert und die Quelldatenbankdatei zugänglich ist.
    *   Verwendet `pathlib.Path`-Objekte für eine robuste und OS-unabhängige Handhabung von Dateipfaden.

*   **`_get_timestamp_str(self, dt: Optional[datetime] = None) -> str`**:
    *   Eine private Hilfsmethode zur Generierung eines konsistenten Zeitstempel-Strings (JJJJMMTT_HHmmss) für Sicherungsdateinamen, wobei UTC für Konsistenz verwendet wird.

*   **`_get_backup_filename(self, dt: Optional[datetime] = None) -> Path`**:
    *   Eine private Hilfsmethode zur Konstruktion des vollständigen Pfades für eine neue Sicherungsdatei basierend auf dem Datenbanknamen und einem Zeitstempel.

*   **`_list_backups(self) -> List[Path]`**:
    *   Identifiziert und listet alle vorhandenen Sicherungsdateien für die spezifische Datenbank innerhalb des `backup_dir` auf.
    *   Analysiert den Zeitstempel aus Dateinamen, um sie chronologisch zu sortieren und so eine korrekte Rotationslogik zu gewährleisten.

*   **`perform_backup(self) -> Path`**:
    *   Führt den eigentlichen Dateikopiervorgang mit `shutil.copy2` aus, um Metadaten zu erhalten.
    *   Generiert einen eindeutigen Dateinamen mit Zeitstempel für die neue Sicherung.
    *   Protokolliert den Erfolg oder Misserfolg des Sicherungsvorgangs.

*   **`perform_rotation(self) -> None`**:
    *   Dies ist die Kernlogik für die Verwaltung alter Sicherungen.
    *   Es ruft alle vorhandenen Sicherungen ab und iteriert sie in umgekehrter chronologischer Reihenfolge (neueste zuerst).
    *   Es wendet die Aufbewahrungsrichtlinie (`daily`, `weekly`, `monthly`) an, um zu bestimmen, welche Sicherungen behalten werden sollen.
    *   **Tägliche Aufbewahrung**: Behält die angegebene Anzahl der neuesten täglichen Sicherungen (eine pro Tag).
    *   **Wöchentliche Aufbewahrung**: Von Sicherungen, die *nicht* bereits durch die tägliche Richtlinie behalten wurden, werden die angegebene Anzahl wöchentlicher Sicherungen behalten (eine pro Woche).
    *   **Monatliche Aufbewahrung**: Von Sicherungen, die *nicht* bereits durch tägliche oder wöchentliche Richtlinien behalten wurden, werden die angegebene Anzahl monatlicher Sicherungen behalten (eine pro Monat).
    *   Sicherungen, die keine Aufbewahrungskriterien erfüllen, werden mit `pathlib.Path.unlink()` gelöscht.
    *   Eine robuste Protokollierung wird verwendet, um zu verfolgen, welche Sicherungen behalten und welche gelöscht werden.

## 3. Datenfluss

1.  **Initialisierung**: `main.py` empfängt `db_path`, `backup_dir` und `retention_policy_str` von Kommandozeilenargumenten.
2.  **Richtlinien-Parsing**: `parse_retention_policy` konvertiert `retention_policy_str` in ein Wörterbuch.
3.  **Rotator-Instanziierung**: Eine Instanz von `BackupRotator` wird mit den geparsten Argumenten erstellt.
4.  **Sicherungsausführung**: `rotator.perform_backup()` wird aufgerufen.
    *   Es wird ein neuer Sicherungsdateiname mit Zeitstempel generiert.
    *   Die Datei `db_path` wird an den neuen Sicherungsort in `backup_dir` kopiert.
5.  **Rotationsausführung**: `rotator.perform_rotation()` wird aufgerufen.
    *   Es ruft `_list_backups()` auf, um alle vorhandenen Sicherungen chronologisch sortiert zu erhalten.
    *   Es iteriert durch die sortierten Sicherungen und identifiziert diejenigen, die gemäß der `retention_policy` behalten werden sollen.
    *   Für jede Sicherung, die nicht zur Aufbewahrung markiert ist, wird `backup.unlink()` aufgerufen, um die Datei zu löschen.

## 4. Fehlerbehandlung und Protokollierung

*   Die Anwendung verwendet das Standard-`logging`-Modul von Python, um eine klare Ausgabe zu liefern. Informationsmeldungen berichten über erfolgreiche Operationen, und Fehlermeldungen heben Probleme hervor (z. B. Datenbank nicht gefunden, Berechtigungsfehler beim Löschen von Dateien).
*   `FileNotFoundError` wird frühzeitig ausgelöst, wenn die Quelldatenbank nicht existiert.
*   Eine allgemeine `Exception`-Behandlung ist in `main()` vorhanden, um unerwartete Probleme während des Prozesses abzufangen und einen ordnungsgemäßen Exit mit einer Fehlermeldung zu gewährleisten.

## 5. Zukünftige Erweiterungen

*   **Unterstützung für Konfigurationsdateien**: Implementierung einer `config.json` oder `config.ini`, um Datenbankpfade, Sicherungsverzeichnisse und Aufbewahrungsrichtlinien zu speichern und so die Notwendigkeit langer Kommandozeilenargumente zu eliminieren.
*   **Unterstützung für mehrere Datenbanken**: Erweiterung des Tools zur Verwaltung von Sicherungen für mehrere SQLite-Datenbanken mit individuellen Richtlinien.
*   **Komprimierung**: Hinzufügen einer Option zur Komprimierung von Sicherungsdateien (z. B. `.zip`, `.gz`), um Speicherplatz zu sparen.
*   **Integritätsprüfungen**: Implementierung optionaler SQLite `PRAGMA integrity_check` für Sicherungen, um deren Gültigkeit sicherzustellen.
*   **Cloud-Speicher-Integration**: Ermöglichen des Hochladens von Sicherungen in Cloud-Speicherdienste (z. B. S3, Google Drive, Dropbox).
*   **Benachrichtigungssystem**: Hinzufügen von Hooks zum Senden von Benachrichtigungen (E-Mail, Slack usw.) bei Erfolg oder Misserfolg.
*   **Detaillierte Berichterstattung**: Erstellung detaillierterer Berichte über erstellte, gelöschte und beibehaltene Sicherungen.
*   **Sperrmechanismus**: Implementierung einer dateibasierten oder prozessbasierten Sperre, um zu verhindern, dass mehrere Instanzen gleichzeitig auf derselben Datenbank ausgeführt werden.
