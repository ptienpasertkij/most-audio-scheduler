import csv
import os
import time
import logging
from datetime import datetime, timedelta
import schedule
from tabulate import tabulate
import threading

# Constants for file paths
RECORDING_DIRECTORY_PATH = "/home/autoannc/most-audio-scheduler/recordings"
SCHEDULE_FILE_PATH = "/home/autoannc/most-audio-scheduler/test_schedule.csv"
# RECORDING_DIRECTORY_PATH = "D:/Github Repos/most-audio-scheduler/recordings"
# SCHEDULE_FILE_PATH = "D:/Github Repos/most-audio-scheduler/test_schedule.csv"

# Setting up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger()


# Class to represent an announcement event
class Announcement:
    def __init__(
        self, event_name, event_time, annc_time, days_to_play, annc_file_name, file_path
    ):
        self.event_name = event_name
        self.event_time = event_time
        self.annc_time = annc_time
        self.days_to_play = days_to_play.split(",")
        self.annc_file_name = annc_file_name
        self.file_path = file_path

    def __repr__(self):
        return f"Announcement(event_name={self.event_name}, annc_time={self.annc_time}, annc_file_name={self.annc_file_name})"


def print_schedule_table(schedule_data):
    table = []
    for event in schedule_data:
        table.append(
            [
                event.event_name,
                event.event_time if event.event_time else "N/A",
                event.annc_time,
                ", ".join(event.days_to_play),
                event.file_path,
            ]
        )

    headers = [
        "Event Name",
        "Event Time",
        "Announcement Time",
        "Days to Play",
        "File Path",
    ]
    print("\nSchedule Loaded:\n")
    print(tabulate(table, headers, tablefmt="pretty"))


def load_schedule(file_path):
    """Load the playback schedule from a CSV file, validate files, and sort by announcement time."""
    logger.info(f"Loading schedule from {file_path}...")
    schedule_data = []
    try:
        with open(file_path, mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                full_file_path = os.path.join(
                    RECORDING_DIRECTORY_PATH, row["ANNC FILE NAME"]
                )
                event = Announcement(
                    event_name=row["EVENT NAME"],
                    event_time=row["EVENT TIME"].strip() if row["EVENT TIME"] else None,
                    annc_time=row["ANNC TIME"],
                    days_to_play=row["DAYS TO PLAY"],
                    annc_file_name=row["ANNC FILE NAME"],
                    file_path=full_file_path,
                )
                # Check if the corresponding file exists
                if os.path.isfile(full_file_path):
                    if event.event_time:
                        logger.info(
                            f"File found: {event.file_path} for {event.event_time} {event.event_name}"
                        )
                    else:
                        logger.info(
                            f"File found: {event.file_path} for {event.event_name}"
                        )
                    schedule_data.append(event)
                else:
                    logger.warning(f"File not found: {event.file_path}")
                    user_input = (
                        input("File not found. Press 'Y' to continue or 'N' to exit: ")
                        .strip()
                        .upper()
                    )
                    if user_input == "N":
                        logger.info("Exiting program as requested by the user.")
                        exit(0)
                    elif user_input == "Y":
                        logger.info("Continuing with the remaining schedule.")
                    else:
                        logger.info(
                            "Invalid input. Continuing with the remaining schedule."
                        )

        # Sort the schedule by announcement time
        schedule_data.sort(key=lambda x: x.annc_time)
        logger.info("Schedule loaded and sorted successfully.")
        print_schedule_table(schedule_data)  # Print the schedule table
    except Exception as e:
        logger.error(f"Failed to load schedule: {e}")

    return schedule_data


def play_announcement(file_name):
    """Play the announcement recording using VLC."""
    logger.info(f"Playing announcement: {file_name}")
    try:
        os.system(f"cvlc --play-and-exit {file_name}")
    except Exception as e:
        logger.error(f"Failed to play announcement: {e}")
    logger.info(f"Finished playing: {file_name}")


def schedule_announcements(schedule_data):
    """Schedule announcements based on the provided schedule data."""
    day_mapping = {
        "mon": "monday",
        "tue": "tuesday",
        "wed": "wednesday",
        "thu": "thursday",
        "fri": "friday",
        "sat": "saturday",
        "sun": "sunday",
        "everyday": "everyday",
    }
    for event in schedule_data:
        for day in event.days_to_play:
            mapped_day = day_mapping.get(day.strip().lower(), "")
            if mapped_day:
                # schedule.every().day.at(event.annc_time).do(play_announcement, event.file_path).tag(day)
                # logger.info(f"Scheduled announcement for {event.event_name} on {day} at {event.annc_time}")
                if mapped_day == "everyday":
                    schedule.every().day.at(event.annc_time).do(
                        play_announcement, event.file_path
                    )
                    logger.info(
                        f"Scheduled announcement for {event.event_name} on {mapped_day} at {event.annc_time}"
                    )
                else:
                    getattr(schedule.every(), mapped_day).at(event.annc_time).do(
                        play_announcement, event.file_path
                    )
                    logger.info(
                        f"Scheduled announcement for {event.event_name} on {mapped_day} at {event.annc_time}"
                    )
            else:
                logger.warning(f"Invalid day provided for {event.event_name}: {day}")


def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)


def main():
    # Load and validate the schedule
    schedule_data = load_schedule(SCHEDULE_FILE_PATH)

    # # Schedule the announcements
    schedule_announcements(schedule_data)

    # Start the scheduler in a separate thread to keep the main thread free
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.start()


if __name__ == "__main__":
    main()
