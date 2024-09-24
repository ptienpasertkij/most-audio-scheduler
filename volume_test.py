import os

def play_audio(file_path):
    os.system(f"cvlc --repeat {file_path}")


def main():
    file_path = "/home/autoannc/most-audio-scheduler/recordings/500close.wav"
    play_audio(file_path)


if __name__ == "__main__":
    main()
