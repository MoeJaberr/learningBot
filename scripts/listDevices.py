import pyaudio

audio = pyaudio.PyAudio()
for i in range(audio.get_device_count()):
    info = audio.get_device_info_by_index(i)
    if info["maxInputChannels"] > 0:
        print(f"[{i}] {info['name']} — Input Channels: {info['maxInputChannels']}")
audio.terminate()
