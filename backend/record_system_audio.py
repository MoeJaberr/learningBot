import sounddevice as sd
import numpy as np
import wave
import os
from tkinter import simpledialog, Tk

def record_system_audio(duration=300):
    # Prompt for metadata using minimal GUI
    root = Tk()
    root.withdraw()  # Hide main window
    course_code = simpledialog.askstring("Course Code", "Enter course code (e.g., COMP201)")
    week_number = simpledialog.askstring("Week Number", "Enter week number (e.g., 3)")
    weekday = simpledialog.askstring("Weekday", "Enter weekday (e.g., Monday)")
    root.destroy()

    if not all([course_code, week_number, weekday]):
        print("[!] All fields are required.")
        return

    filename = f"{course_code}_WEEK{week_number}_{weekday}.wav"
    filepath = os.path.abspath(os.path.join("output", filename))

    print(f"[*] Recording system audio to: {filepath}")
    samplerate = 44100
    duration_sec = duration  # You can change to your preferred default

    try:
        # Find WASAPI loopback input device
        wasapi_devices = [i for i, dev in enumerate(sd.query_devices()) if dev['hostapi'] == sd.default.hostapi and dev['max_input_channels'] > 0 and 'Loopback' in dev['name']]
        if not wasapi_devices:
            print("[!] No loopback-capable system audio device found.")
            return
        device = wasapi_devices[0]
        print(f"[*] Using device: {sd.query_devices(device)['name']}")

        recording = sd.rec(int(duration_sec * samplerate), samplerate=samplerate, channels=2, dtype='int16', device=device)
        sd.wait()

        os.makedirs("output", exist_ok=True)
        with wave.open(filepath, 'wb') as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(samplerate)
            wf.writeframes(recording.tobytes())

        print(f"[+] Recording saved to {filepath}")

    except Exception as e:
        print(f"[!] Recording failed: {e}")

if __name__ == "__main__":
    record_system_audio(duration=5100)  # 85 min max
