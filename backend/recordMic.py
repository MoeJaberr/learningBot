stop_flag = {"stop": False}


def record_microphone(duration=5100, filename="output/audio.wav", device_index=None, stop_flag=None):
    import pyaudio
    import wave
    import time
    import os

    filename = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', filename))
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024

    if device_index is None:
        print("[!] No device index provided.")
        return

    audio = pyaudio.PyAudio()

    try:
        stream = audio.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            input_device_index=device_index,
                            frames_per_buffer=CHUNK)

        frames = []
        max_frames = int(RATE / CHUNK * duration)
        print("[*] Recording started. Press Stop to end early.")

        for i in range(max_frames):
            if stop_flag and stop_flag.get("stop"):
                print("[*] Early stop signal received.")
                break
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)

        print("[*] Recording stopped.")

        stream.stop_stream()
        stream.close()
        audio.terminate()

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))

        print(f"[+] Saved to {filename}")

    except Exception as e:
        print(f"[!] Recording failed: {e}")
        audio.terminate()
