import subprocess
import signal
import sys

# Global variable to hold the process reference
cvlc_process = None

def play_audio(file_path):
    global cvlc_process
    # Start cvlc as a subprocess
    cvlc_process = subprocess.Popen(["cvlc", "--repeat", file_path])

def signal_handler(sig, frame):
    global cvlc_process
    if cvlc_process:
        # Terminate the cvlc process gracefully
        cvlc_process.terminate()
        cvlc_process.wait()  # Wait for the process to finish cleanly
        print("cvlc process terminated gracefully.")
    sys.exit(0)

def main():
    # Set up signal handling for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)  # Handle Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Handle kill command

    file_path = "/home/autoannc/most-audio-scheduler/recordings/500close.wav"
    play_audio(file_path)

    # Keep the script running to listen for signals
    signal.pause()

if __name__ == "__main__":
    main()
