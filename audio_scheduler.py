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
    played_times = set()
    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        current_day = now.strftime("%a")
        print(f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}, Current day: {current_day}")
        for entry in schedule:
            scheduled_time = entry['time']
            if current_time == scheduled_time and current_day in entry['days']:
                # Check if this time has been played to avoid multiple plays in the same minute
                if (current_day, scheduled_time) not in played_times:
                    print(f"Scheduled time: {entry['time']}, Day: {current_day}")
                    play_audio(entry['file'])
                    played_times.add((current_day, scheduled_time))
        # Clear played_times at the end of the minute to reset for the next minute
        if now.second == 59:
            played_times.clear()
        time.sleep(30)  # Check the time every 30 seconds

if __name__ == "__main__":
    main("/home/autoannc/most-audio-scheduler/config.json")
