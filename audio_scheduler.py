import csv
from datetime import datetime, timedelta
import time
import vlc
import logging

# Configuration
ROOT_DIRECTORY_PATH = "/home/autoannc/most-audio-scheduler/recordings"
CSV_FILE_PATH = "/home/autoannc/most-audio-scheduler/annoucement_schedule.csv"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_schedule(csv_file):
    schedule = []
    try:
        with open(csv_file, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row['DAYS TO PLAY'] = row['DAYS TO PLAY'].split(', ')
                row['ANNC FILE NAME'] = f"{ROOT_DIRECTORY_PATH}/{row['ANNC FILE NAME']}"
                schedule.append(row)
    except Exception as e:
        logging.error(f"Failed to load CSV configuration: {e}")
    return schedule

def play_audio(file):
    try:
        player = vlc.MediaPlayer(file)
        player.play()
        time.sleep(5)  # Allow the player to start
        while player.is_playing():
            time.sleep(1)
        player.stop()
    except Exception as e:
        logging.error(f"Failed to play audio file {file}: {e}")

def next_play_time(schedule):
    """Calculate the next time a file should be played to optimize sleep duration."""
    now = datetime.now()
    times = []
    for entry in schedule:
        for day in entry['DAYS TO PLAY']:
            play_time = datetime.strptime(f"{now.strftime('%Y-%m-%d')} {entry['ANNC TIME']}", '%Y-%m-%d %I:%M%p')
            if play_time < now:  # If today's time is past, schedule for next week
                play_time += timedelta(days=7)
            times.append(play_time)
    return min(times) if times else now + timedelta(days=1)

def main(csv_file):
    schedule = load_schedule(csv_file)
    played_times = set()
    while True:
        now = datetime.now()
        next_play = next_play_time(schedule)
        sleep_time = (next_play - now).total_seconds() - 1
        if sleep_time > 0:
            time.sleep(sleep_time)

        current_time = now.strftime("%I:%M%p")
        current_day = now.strftime("%a")
        logging.info(f"Checking schedule at {now}")
        for entry in schedule:
            scheduled_time = entry['ANNC TIME']
            if current_time == scheduled_time and current_day in entry['DAYS TO PLAY']:
                if (current_day, scheduled_time) not in played_times:
                    logging.info(f"Event: {entry['EVENT NAME']}, Announcement Time: {entry['ANNC TIME']}, File: {entry['ANNC FILE NAME']}")
                    play_audio(entry['ANNC FILE NAME'])
                    played_times.add((current_day, scheduled_time))
                else:
                    logging.info(f"Audio already played today at {scheduled_time}.")

        # Reset played times if no upcoming plays are scheduled soon
        if now.hour == 23 and now.minute == 59:
            played_times.clear()

if __name__ == "__main__":
    main(CSV_FILE_PATH)
