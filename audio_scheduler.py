import json
import time
from datetime import datetime
import vlc


def load_schedule(config_file):
    with open(config_file) as f:
        return json.load(f)["schedule"]


def play_audio(file):
    player = vlc.MediaPlayer(file)
    player.play()
    time.sleep(5)  # Wait for the player to start
    while player.is_playing():
        time.sleep(1)
    player.stop()


def main(config_file):
    schedule = load_schedule(config_file)
    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        print(f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        # current_day = now.strftime("%a")
        for entry in schedule:
            if current_time == entry["time"]:
                print(f"Scheduled time: {entry['time']}")
                play_audio(entry["file"])
                time.sleep(
                    60
                )  # Wait a minute before checking the schedule again to avoid multiple plays
        time.sleep(30)  # Check the time every 30 seconds

if __name__ == "__main__":
    main("/home/autoannc/most-audio-scheduler/config.json")
