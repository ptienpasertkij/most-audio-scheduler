import vlc

def play_audio(file):
    player = vlc.MediaPlayer(file)
    player.play()
    time.sleep(5)  # Wait for the player to start
    while player.is_playing():
        time.sleep(1)
    player.stop()

if __name__ == "__main__":
    play_audio("/home/autoannc/Music/5mintest.wav")
