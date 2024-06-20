# Vorlesungsassistent

Der Vorlesungsassistent ist eine KI-basierte Anwendung zur Aufbereitung von Vorlesungsvideos. Das Projekt nutzt moderne KI-Technologien, um Vorlesungen zu transkribieren und ermöglicht es Nutzern, mit einem Chatbot zu interagieren, um Fragen zu den Vorlesungsinhalten zu stellen. Die Anwendung ist in Python programmiert und verwendet ein Model-View-Controller (MVC) Designmuster.

## Voraussetzungen

- Windows 10 oder höher
- Python 3.8 oder höher
- [ffmpeg](https://ffmpeg.org/)

## Setup

Folgen Sie diesen Schritten, um das Projekt auf Ihrem lokalen Rechner einzurichten:

__1. Klonen und öffnen Sie das Repository:__

```bash
git clone https://github.com/JonasBrue/media-ai.git
cd media-ai
```

__2. Erstellen Sie die virtuelle Umgebung:__

```bash
python -m venv media-ai-venv
```

__3. Aktivieren Sie die virtuelle Umgebung:__

```bash
.\media-ai-venv\Scripts\activate
```

__4. Überprüfen Sie die Aktivierung der virtuellen Umgebung:__

Führen Sie den folgenden Befehl aus, um zu überprüfen, ob Sie sich in der virtuellen Umgebung befinden:
```bash
python -c "import sys; print(sys.prefix)"
```
Die Ausgabe sollte am Ende "media-ai-venv" enthalten. Ist dies nicht der Fall, lesen Sie den Abschnitt Fehlerbehebung 1.

__4. Installieren Sie die Abhängigkeiten:__

```bash
pip install -r requirements.txt
```

__5. Setzen Sie die Umgebungsvariablen:__

Bearbeiten Sie die .env-Datei und fügen Sie Ihren API-Schlüssel ein.
OPENAI_API_KEY=openai_api_schlüssel_hier

__6. Ausführen der Anwendung:__

```bash
python main.py
```

## Fehlerbehebung

__1. Aktivierung der virtuellen Umgebung fehlgeschlagen:__

Für PowerShell müssen Sie möglicherweise die Ausführungsrichtlinie anpassen:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Aktivieren Sie dann mit dem Befehl in Schritt 3. oder mit diesem Befehl:
```powershell
.\media-ai-venv\Scripts\Activate.ps1
```
Wenn Sie weiterhin Probleme haben, versuchen Sie, die Eingabeaufforderung (cmd.exe) anstelle von PowerShell zu verwenden.