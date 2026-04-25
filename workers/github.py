import json
import urllib.request
from PySide6.QtCore import QThread, Signal

class GitHubUpdateWorker(QThread):
    update_available = Signal(str, str, str)

    def run(self):
        try:
            url = "https://api.github.com/repos/mattjoykaraoke/ChromaLyric/releases/latest"
            req = urllib.request.Request(url, headers={"User-Agent": "ChromaLyric-App"})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                latest_version = data.get("tag_name", "")
                release_notes = data.get("body", "")
                html_url = data.get("html_url", "")
                self.update_available.emit(latest_version, release_notes, html_url)
        except Exception:
            pass
