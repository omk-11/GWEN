import subprocess
import socket
import json
import os
import time

SOCKET_PATH = "/tmp/mpv_socket"


PLAYLISTS = {
    "you'll": "https://music.youtube.com/playlist?list=PL0LpVNOjpohP0WMQBwXQGEzPfHi2RIOUn"
}

class MusicService:
    def __init__(self):
        self.process = None

    def _is_running(self):
        return self.process is not None and os.path.exists(SOCKET_PATH)

    # 🔥 start mpv with shuffle ALWAYS ON
    def _start(self, source):
        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)

        self.process = subprocess.Popen(
            [
                "mpv",
                "--no-video",
                "--ytdl-format=bestaudio",
                "--force-window=no",
                "--shuffle=yes",  # ✅ HARD CODED SHUFFLE
                f"--input-ipc-server={SOCKET_PATH}",
                source
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True
        )

        # wait for socket
        for _ in range(20):
            if os.path.exists(SOCKET_PATH):
                return
            time.sleep(0.1)

        print("⚠️ mpv socket not ready")

    # 🔍 resolve query
    def _resolve_source(self, query):
        q = query.lower().strip()

        for name in PLAYLISTS:
            if name in q:
                return PLAYLISTS[name]

        if "youtube.com" in q or "music.youtube.com" in q:
            return q

        return f"ytdl://ytsearch1:{q}"

    # 🎧 play / queue
    def play(self, query="lofi music"):
        source = self._resolve_source(query)

        if not self._is_running():
            self._start(source)
        else:
            self._send({
                "command": ["loadfile", source, "append"]
            })

    # ▶️ override queue
    def play_now(self, query):
        source = self._resolve_source(query)
        self._send({
            "command": ["loadfile", source, "replace"]
        })

    # 🔌 IPC sender
    def _send(self, command):
        if not self._is_running():
            print("⚠️ mpv not running")
            return

        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
                client.connect(SOCKET_PATH)
                client.send((json.dumps(command) + "\n").encode())
        except Exception as e:
            print("Socket error:", e)

    # ⏸️ pause
    def pause(self):
        self._send({"command": ["set_property", "pause", True]})

    # ▶️ resume
    def resume(self):
        self._send({"command": ["set_property", "pause", False]})

    # ⏭️ next
    def skip(self):
        self._send({"command": ["playlist-next"]})

    # ⏮️ previous
    def previous(self):
        self._send({"command": ["playlist-prev"]})

    # 🧹 clear queue
    def clear(self):
        self._send({"command": ["playlist-clear"]})

    # ⏹️ stop
    def stop(self):
        if self.process:
            try:
                self.process.kill()
            except:
                pass
            self.process = None

        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)