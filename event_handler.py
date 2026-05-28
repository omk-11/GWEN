from tools.music.music_service import MusicService

music = MusicService()

def handle_event(user_input):
    text = user_input.lower().strip()

    # 🧠 remove wake word safely
    if text.startswith("cap"):
        text = text.replace("cap", "", 1).strip()

    # 🎧 PLAY
    if text.startswith("play"):
        query = text.replace("play", "", 1).strip()
        music.play(query if query else "lofi music")

    # ⏸️ PAUSE
    elif "pause" in text or "wait" in text:
        music.pause()

    # ▶️ RESUME
    elif "resume" in text:
        music.resume()

    # ⏹️ STOP
    elif "stop" in text:
        music.stop()

    # ⏭️ SKIP
    elif "skip" in text or "next" in text:
        music.skip()

    # ⏮️ PREVIOUS (bonus)
    elif "previous" in text or "back" in text:
        music.previous()

    else:
        print("⚠️ Unknown command:", text)