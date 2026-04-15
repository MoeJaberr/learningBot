import os
import wave
import threading

FORMAT_INT16 = None  # resolved lazily to avoid importing pyaudio at module level
SAMPLE_RATE = 44100
CHANNELS = 1
CHUNK_SIZE = 1024
SAMPLE_WIDTH = 2  # paInt16 = 2 bytes

# Fire the on_chunk callback every N seconds of recorded audio
CHUNK_INTERVAL_SECS = 120


def record_microphone(
    duration: int = 5100,
    filename: str = "output/audio.wav",
    device_index: int | None = None,
    stop_flag: dict | None = None,
    on_chunk=None,  # callable(chunk_wav_path: str) — fired every CHUNK_INTERVAL_SECS
):
    import pyaudio

    filename = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", filename))
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    if device_index is None:
        print("[!] No device index provided.")
        return

    audio = pyaudio.PyAudio()
    global FORMAT_INT16
    FORMAT_INT16 = pyaudio.paInt16

    try:
        stream = audio.open(
            format=FORMAT_INT16,
            channels=CHANNELS,
            rate=SAMPLE_RATE,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=CHUNK_SIZE,
        )

        all_frames: list[bytes] = []
        chunk_frames: list[bytes] = []
        max_frames = int(SAMPLE_RATE / CHUNK_SIZE * duration)
        frames_per_chunk = int(SAMPLE_RATE / CHUNK_SIZE * CHUNK_INTERVAL_SECS)
        chunk_counter = 0

        print("[*] Recording started.")

        for _ in range(max_frames):
            if stop_flag and stop_flag.get("stop"):
                print("[*] Early stop signal received.")
                break
            data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
            all_frames.append(data)
            chunk_frames.append(data)

            if on_chunk and len(chunk_frames) >= frames_per_chunk:
                chunk_counter += 1
                chunk_path = os.path.abspath(f"output/chunk_{chunk_counter:03d}.wav")
                _save_wav(chunk_frames, chunk_path)
                chunk_frames = []
                threading.Thread(target=on_chunk, args=(chunk_path,), daemon=True).start()

        print("[*] Recording stopped.")
        stream.stop_stream()
        stream.close()
        audio.terminate()

        _save_wav(all_frames, filename)
        print(f"[+] Full recording saved to {filename}")

    except Exception as e:
        print(f"[!] Recording failed: {e}")
        audio.terminate()


def _save_wav(frames: list[bytes], path: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(SAMPLE_WIDTH)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(b"".join(frames))
