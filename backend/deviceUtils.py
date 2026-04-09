# backend/deviceUtils.py
import pyaudio

def list_input_devices():
    audio = pyaudio.PyAudio()
    devices = []
    for i in range(audio.get_device_count()):
        info = audio.get_device_info_by_index(i)
        if info["maxInputChannels"] > 0:
            devices.append((i, info["name"]))
    audio.terminate()
    return devices
