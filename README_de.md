# SQLite Backup Rotator

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/github/license/username/repo-name)
![CI Status](https://github.com/username/repo-name/workflows/Python%20application/badge.svg)

## 📚 Projektbeschreibung

Der `sqlite-backup-rotator` ist ein unternehmenstaugliches Open-Source-Kommandozeilen-Tool, das entwickelt wurde, um die Sicherung und Rotation lokaler SQLite-Datenbankdateien zu automatisieren. Es bietet eine robuste Lösung zur Gewährleistung der Datenintegrität und -verfügbarkeit, indem es regelmäßig Backups erstellt und deren Aufbewahrung intelligent auf der Grundlage konfigurierbarer Richtlinien verwaltet (z. B. Beibehaltung der letzten 7 täglichen, 4 wöchentlichen und 12 monatlichen Sicherungen).

Dieses Projekt zielt darauf ab, einfach, zuverlässig und leicht in verschiedene Systeme integrierbar zu sein, von kleinen persönlichen Projekten bis hin zu größeren Unternehmensanwendungen, die eine lokale Datenpersistenz mit starken Sicherungsstrategien erfordern.

## ✨ Funktionen

*   **Automatisierte Sicherungen**: Erstellen Sie einfach Sicherungen Ihrer SQLite-Datenbankdateien mit Zeitstempel.
*   **Konfigurierbare Aufbewahrungsrichtlinien**: Definieren Sie, wie viele tägliche, wöchentliche und monatliche Sicherungen aufbewahrt werden sollen.
*   **Intelligente Rotation**: Löscht automatisch alte Sicherungen, die außerhalb der angegebenen Aufbewahrungsrichtlinie liegen.
*   **Robuste Fehlerbehandlung**: Protokolliert Fehler und liefert informative Meldungen.
*   **Kommandozeilen-Interface**: Einfach über Kommandozeilenargumente zu bedienen.
*   **Pythonisch & Type-Hinted**: Entwickelt nach modernen Python-Best Practices, einschließlich OOP und Type-Hints.
*   **Zweisprachige Dokumentation**: Umfassende Dokumentation in Englisch und Deutsch verfügbar.
*   **Unit-Tests**: Hohe Testabdeckung zur Gewährleistung der Zuverlässigkeit.
*   **CI/CD-Integration**: GitHub Actions Workflow für automatisierte Tests.

## 🚀 Installation

### Voraussetzungen

*   Python 3.8 oder höher

### Schritte

1.  **Klonen Sie das Repository:**
    ```bash
    git clone https://github.com/your-username/sqlite-backup-rotator.git
    cd sqlite-backup-rotator
    ```

2.  **Erstellen und aktivieren Sie eine virtuelle Umgebung (empfohlen):**
    ```bash
    python -m venv venv
    # Unter Windows:
    # .\venv\Scripts\activate
    # Unter macOS/Linux:
    source venv/bin/activate
    ```

3.  **Installieren Sie Abhängigkeiten:**
    ```bash
    pip install -r requirements.txt
    ```

## 💡 Verwendung

Um den Sicherungs- und Rotationsprozess auszuführen, führen Sie das Skript `main.py` mit den erforderlichen Argumenten aus:

```bash
python main.py \
  --db-path /pfad/zu/ihrer/datenbank.sqlite \
  --backup-dir /pfad/zu/ihrem/sicherungsverzeichnis \
  --retention-policy "daily=7,weekly=4,monthly=12"
```

### Argumente:

*   `--db-path` (erforderlich): Der absolute Pfad zu Ihrer Quell-SQLite-Datenbankdatei.
*   `--backup-dir` (erforderlich): Der absolute Pfad zu dem Verzeichnis, in dem Sicherungen gespeichert werden sollen.
*   `--retention-policy` (optional): Ein durch Kommas getrennter String, der die Aufbewahrungsrichtlinie definiert. Standard ist `"daily=7,weekly=4,monthly=12"`.
    *   `daily=N`: Behält die letzten `N` täglichen Sicherungen.
    *   `weekly=M`: Behält die letzten `M` wöchentlichen Sicherungen.
    *   `monthly=P`: Behält die letzten `P` monatlichen Sicherungen.

    *Hinweis: Die Rotationslogik priorisiert täglich, dann wöchentlich, dann monatlich. Das bedeutet, ein Backup wird möglicherweise behalten, wenn es eines der Aufbewahrungskriterien erfüllt.*

### Beispiel:

Stellen Sie sich vor, Sie haben eine Datenbank unter `/home/user/app/data.sqlite` und möchten Sicherungen in `/home/user/backups` speichern. Sie möchten die letzten 5 täglichen Sicherungen, 2 wöchentlichen Sicherungen und 6 monatlichen Sicherungen behalten.

```bash
python main.py \
  --db-path /home/user/app/data.sqlite \
  --backup-dir /home/user/backups \
  --retention-policy "daily=5,weekly=2,monthly=6"
```

### Planung

Für automatisierte, regelmäßige Sicherungen können Sie dieses Skript mit Tools wie `cron` (Linux/macOS) oder dem Task-Scheduler (Windows) planen.

**Cron-Beispiel (täglich um 2 Uhr morgens):**

1.  Öffnen Sie Ihre Crontab zur Bearbeitung:
    ```bash
    crontab -e
    ```
2.  Fügen Sie die folgende Zeile hinzu (Pfade bei Bedarf anpassen, einschließlich des vollständigen Pfades zu Ihrem Python-Executable und Skript):
    ```cron
    0 2 * * * /usr/bin/python3 /pfad/zu/sqlite-backup-rotator/main.py --db-path /pfad/zu/ihrer/datenbank.sqlite --backup-dir /pfad/zu/ihrem/sicherungsverzeichnis --retention-policy "daily=7,weekly=4,monthly=12" >> /var/log/sqlite_backup.log 2>&1
    ```

## 🧪 Tests ausführen

Um sicherzustellen, dass alles ordnungsgemäß funktioniert, können Sie die Unit-Tests ausführen:

```bash
python -m unittest discover
```

## 🤝 Mitwirken

Wir freuen uns über Beiträge zum Projekt `sqlite-backup-rotator`! Bitte beachten Sie die Datei [CONTRIBUTING.md](CONTRIBUTING.md) für Richtlinien zum Einstieg.

## 📄 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert. Details finden Sie in der Datei [LICENSE](LICENSE).

## 📞 Kontakt

Für Fragen, Anregungen oder Probleme eröffnen Sie bitte ein Issue im GitHub-Repository.
