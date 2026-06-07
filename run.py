import threading
import time
import os
import subprocess

from text_to_audio import text_to_speech_file
from main import app  # imports your Flask app


# ── Background worker (from generate_process.py) ──────────────────────────────

def text_to_audio(folder):
    print("TTA - ", folder)
    with open(f"user_uploads/{folder}/desc.txt") as f:
        text = f.read()
    text_to_speech_file(text, folder)

def create_reel(folder):
    command = (
        f'ffmpeg -f concat -safe 0 '
        f'-i user_uploads/{folder}/input.txt '
        f'-i user_uploads/{folder}/audio.mp3 '
        f'-vf "scale=1080:1920:force_original_aspect_ratio=decrease,'
        f'pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black" '
        f'-c:v libx264 -c:a aac -shortest -r 30 -pix_fmt yuv420p '
        f'static/reels/{folder}.mp4'
    )
    subprocess.run(command, shell=True, check=True)
    print("CR - ", folder)

def run_worker():
    """Polls user_uploads/ and processes any new folders."""
    while True:
        print("Processing queue...")
        with open("done.txt", "r") as f:
            done_folders = [line.strip() for line in f.readlines()]

        for folder in os.listdir("user_uploads"):
            if folder not in done_folders:
                try:
                    text_to_audio(folder)
                    create_reel(folder)
                    with open("done.txt", "a") as f:
                        f.write(folder + "\n")
                except Exception as e:
                    print(f"Error processing {folder}: {e}")

        time.sleep(4)


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Start the background worker in a daemon thread
    worker_thread = threading.Thread(target=run_worker, daemon=True)
    worker_thread.start()
    print("Background worker started.")

    # Start the Flask server (blocking — keeps the process alive)
    app.run(debug=False, use_reloader=False)