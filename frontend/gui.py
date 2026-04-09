import tkinter as tk
from tkinter import messagebox, simpledialog
from backend.deviceUtils import list_input_devices
from backend.recordMic import record_microphone
from backend.transcribe_api import transcribe_audio
import subprocess
import threading
import os

recording_thread = None
stop_flag = {"stop": False}
selected_idx = None

def stop_early():
    stop_flag["stop"] = True
    print("[*] Stop flag set — recording will stop shortly.")



def record_in_person(parent_window, status_var):
    global recording_thread, stop_flag, selected_idx

    devices = list_input_devices()
    if not devices:
        messagebox.showerror("Error", "No microphones found.")
        return

    # Create a pop-up window for mic selection
    mic_win = tk.Toplevel(parent_window)
    mic_win.title("Select Microphone")

    tk.Label(mic_win, text="Choose input device:").pack(pady=5)

    mic_options = [f"[{idx}] {name}" for idx, name in devices]
    mic_var = tk.StringVar(value=mic_options[0])
    dropdown = tk.OptionMenu(mic_win, mic_var, *mic_options)
    dropdown.pack(pady=5)

    def start_recording():
        nonlocal mic_win
        global stop_flag, selected_idx, recording_thread

        try:
            selected_idx = int(mic_var.get().split("]")[0][1:])
        except Exception:
            messagebox.showerror("Error", "Invalid mic selection.")
            mic_win.destroy()
            return

        stop_flag["stop"] = False
        status_var.set("Recording mic (in-person)...")
        mic_win.destroy()

        def record():
            record_microphone(duration=5100, device_index=selected_idx, stop_flag=stop_flag)
            status_var.set("Recording complete.")

        recording_thread = threading.Thread(target=record)
        recording_thread.start()

        # Attach Stop button to parent window
        tk.Button(parent_window, text="Stop Recording", command=stop_early).pack(pady=5)

    tk.Button(mic_win, text="Start Recording", command=start_recording).pack(pady=10)




def record_online(window, status_var):
    status_var.set("Recording system audio...")
    course_code = simpledialog.askstring("Course Code", "Enter course code (e.g., COMP201)")
    week_number = simpledialog.askstring("Week Number", "Enter week number (e.g., 3)")
    weekday = simpledialog.askstring("Weekday", "Enter weekday (e.g., Monday)")

    if not all([course_code, week_number, weekday]):
        messagebox.showerror("Error", "All fields are required.")
        return

    def record():
        subprocess.run(["python", "scripts/record_system_audio.py"])
        status_var.set("System audio recording complete.")

    threading.Thread(target=record).start()

    def stop():
        messagebox.showinfo("Stopped", "Recording manually stopped (simulated).")

    tk.Button(window, text="Stop Recording", command=stop).pack()

def launch_recording_window(status_var):
    mode_win = tk.Toplevel()
    mode_win.title("Lecture Mode")

    tk.Label(mode_win, text="Select Lecture Mode:").pack(pady=5)

    tk.Button(mode_win, text="In-Person (Mic)", command=lambda: record_in_person(mode_win, status_var)).pack(pady=5)
    tk.Button(mode_win, text="Online (System Audio)", command=lambda: record_online(mode_win, status_var)).pack(pady=5)

def transcribe_audio_gui(status_var):
    status_var.set("Transcribing...")
    try:
        path = transcribe_audio()
        if path:
            messagebox.showinfo("Transcription Complete", f"Saved to:\n{path}")
            status_var.set("Done.")
        else:
            status_var.set("Transcription failed.")
    except Exception as e:
        messagebox.showerror("Error", str(e))
        status_var.set("Transcription error.")

def launch_tutoring_gui():
    messagebox.showinfo("Tutoring", "Tutoring feature is still under development.")
    # Future: Load transcript and launch AI-guided Socratic questioning

def launch_ui():
    window = tk.Tk()
    window.title("Learning Bot")

    # Main control buttons
    tk.Button(window, text="🎙️ Record Lecture", width=30, command=lambda: launch_recording_window(status_var)).pack(pady=10)
    tk.Button(window, text="📝 Transcribe Audio", width=30, command=lambda: transcribe_audio_gui(status_var)).pack(pady=10)
    tk.Button(window, text="🧠 Start Tutoring", width=30, command=launch_tutoring_gui).pack(pady=10)

    # Status label
    global status_var
    status_var = tk.StringVar(value="Idle.")
    tk.Label(window, textvariable=status_var).pack(pady=10)

    window.mainloop()
