# core/recorder.py

import pyaudio
import wave
import time

def record_microphone_audio(output_path, duration=5100):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("[*] Recording from microphone...")
    frames = []

    for _ in range(0, int(RATE / CHUNK * duration)):
        frames.append(stream.read(CHUNK))

    print("[*] Finished recording.")
    stream.stop_stream()
    stream.close()
    p.terminate()

    with wave.open(output_path, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))


def record_system_audio(output_path, duration=5100):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100

    p = pyaudio.PyAudio()

    loopback_index = None
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        if dev.get('name').lower().__contains__('loopback') or dev.get('hostApi') == 0:
            if dev.get('maxInputChannels') > 0 and 'output' in dev.get('name').lower():
                loopback_index = i
                break

    if loopback_index is None:
        raise RuntimeError("System audio capture not supported on this machine. Enable 'Stereo Mix' or WASAPI loopback.")

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    input_device_index=loopback_index,
                    frames_per_buffer=CHUNK)

    print("[*] Recording system audio...")
    frames = []

    for _ in range(0, int(RATE / CHUNK * duration)):
        frames.append(stream.read(CHUNK))

    print("[*] Finished recording.")
    stream.stop_stream()
    stream.close()
    p.terminate()

    with wave.open(output_path, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
