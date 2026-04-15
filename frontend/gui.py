import os
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog

from backend.deviceUtils import list_input_devices
from backend.recordMic import record_microphone
from backend.transcribe_api import transcribe_audio

# ── App state ─────────────────────────────────────────────────────────────────
_transcript: str = ""       # Full accumulated transcript
_rolling_summary: str = ""  # Latest rolling summary text
_tutor_fn = None            # Callable returned by create_tutor_session
_window: tk.Tk | None = None
_summary_widget: scrolledtext.ScrolledText | None = None
status_var: tk.StringVar | None = None

_recording_thread: threading.Thread | None = None
_stop_flag: dict = {"stop": False}


# ── Thread-safe GUI helpers ───────────────────────────────────────────────────
def _ui(fn):
    """Schedule fn() on the Tk main thread."""
    if _window:
        _window.after(0, fn)


def _set_status(msg: str):
    _ui(lambda: status_var.set(msg) if status_var else None)


def _set_summary_text(text: str):
    global _rolling_summary
    _rolling_summary = text

    def update():
        if _summary_widget:
            _summary_widget.config(state=tk.NORMAL)
            _summary_widget.delete("1.0", tk.END)
            _summary_widget.insert(tk.END, text)
            _summary_widget.config(state=tk.DISABLED)

    _ui(update)


# ── Chunk callback (background thread, triggered during recording) ─────────────
def _make_chunk_callback():
    api_key = os.getenv("OPENAI_API_KEY", "")
    chunk_index = [0]

    def on_chunk(chunk_wav_path: str):
        global _transcript
        chunk_index[0] += 1
        _set_status(f"Transcribing chunk {chunk_index[0]}...")

        chunk_txt_path = chunk_wav_path.replace(".wav", ".txt")
        try:
            transcribe_audio(api_key, chunk_wav_path, chunk_txt_path)
            with open(chunk_txt_path, "r", encoding="utf-8") as f:
                chunk_text = f.read().strip()
            if chunk_text:
                _transcript += ("\n" if _transcript else "") + chunk_text
                from core.rolling_summary import update_rolling_summary
                updated = update_rolling_summary(chunk_text, _rolling_summary)
                _set_summary_text(updated)
                _set_status("Recording... (summary updated)")
        except Exception as e:
            print(f"[!] Chunk processing error: {e}")
            _set_status("Recording...")

    return on_chunk


# ── Recording ─────────────────────────────────────────────────────────────────
def _stop_recording():
    _stop_flag["stop"] = True


def _record_in_person(parent_window):
    global _recording_thread, _transcript, _rolling_summary

    devices = list_input_devices()
    if not devices:
        messagebox.showerror("Error", "No microphones found.")
        return

    mic_win = tk.Toplevel(parent_window)
    mic_win.title("Select Microphone")
    tk.Label(mic_win, text="Choose input device:").pack(pady=5)

    mic_options = [f"[{idx}] {name}" for idx, name in devices]
    mic_var = tk.StringVar(value=mic_options[0])
    tk.OptionMenu(mic_win, mic_var, *mic_options).pack(pady=5)

    def start():
        global _recording_thread
        try:
            device_idx = int(mic_var.get().split("]")[0][1:])
        except Exception:
            messagebox.showerror("Error", "Invalid mic selection.")
            mic_win.destroy()
            return

        _transcript = ""
        _rolling_summary = ""
        _stop_flag["stop"] = False
        _set_summary_text("Recording in progress...\nSummary will appear after first 2 minutes.")
        _set_status("Recording (in-person mic)...")
        mic_win.destroy()

        on_chunk = _make_chunk_callback()

        def run():
            record_microphone(
                duration=5100,
                device_index=device_idx,
                stop_flag=_stop_flag,
                on_chunk=on_chunk,
            )
            _set_status("Recording complete. Ready to transcribe or generate notes.")

        _recording_thread = threading.Thread(target=run, daemon=True)
        _recording_thread.start()
        tk.Button(parent_window, text="Stop Recording", fg="red", command=_stop_recording).pack(pady=5)

    tk.Button(mic_win, text="Start Recording", command=start).pack(pady=10)


def _record_online(parent_window):
    global _transcript, _rolling_summary
    _transcript = ""
    _rolling_summary = ""
    _set_summary_text("Recording in progress...\nSummary will appear after first 2 minutes.")

    course_code = simpledialog.askstring("Course Code", "Enter course code (e.g., COMP201)")
    week_number = simpledialog.askstring("Week Number", "Enter week number (e.g., 3)")
    weekday = simpledialog.askstring("Weekday", "Enter weekday (e.g., Monday)")

    if not all([course_code, week_number, weekday]):
        messagebox.showerror("Error", "All fields are required.")
        return

    import subprocess

    def run():
        subprocess.run(["python", "scripts/record_system_audio.py"])
        _set_status("System audio recording complete.")

    threading.Thread(target=run, daemon=True).start()
    _set_status("Recording system audio...")
    tk.Button(parent_window, text="Stop Recording", fg="red",
              command=lambda: messagebox.showinfo("Stopped", "Recording stopped.")).pack()


def _launch_recording_window():
    mode_win = tk.Toplevel(_window)
    mode_win.title("Select Lecture Mode")
    tk.Label(mode_win, text="Select Lecture Mode:").pack(pady=10)
    tk.Button(mode_win, text="In-Person (Mic)", width=25,
              command=lambda: _record_in_person(mode_win)).pack(pady=5)
    tk.Button(mode_win, text="Online (System Audio)", width=25,
              command=lambda: _record_online(mode_win)).pack(pady=5)


# ── Post-recording actions ────────────────────────────────────────────────────
def _transcribe_gui():
    global _transcript
    _set_status("Transcribing...")
    api_key = os.getenv("OPENAI_API_KEY", "")
    audio_path = os.path.abspath("output/audio.wav")
    transcript_path = os.path.abspath("output/transcript.txt")

    def run():
        global _transcript
        try:
            transcribe_audio(api_key, audio_path, transcript_path)
            with open(transcript_path, "r", encoding="utf-8") as f:
                _transcript = f.read()
            _set_status("Transcription complete.")
            _ui(lambda: messagebox.showinfo("Done", f"Transcript saved to:\n{transcript_path}"))
        except Exception as e:
            _ui(lambda: messagebox.showerror("Error", str(e)))
            _set_status("Transcription error.")

    threading.Thread(target=run, daemon=True).start()


def _generate_notes_gui():
    if not _transcript:
        messagebox.showwarning("No Transcript", "Transcribe audio first (or recording must have produced chunks).")
        return
    _set_status("Generating Obsidian notes...")

    course_code = simpledialog.askstring("Course Code", "Course code for the note filename (e.g., COMP3520)") or "lecture"

    def run():
        from core.obsidian import generate_obsidian_notes, save_obsidian_note
        notes = generate_obsidian_notes(_transcript)
        if notes:
            path = save_obsidian_note(
                notes,
                filename_prefix=course_code,
                tags=[course_code.lower().replace(" ", "-")],
            )
            _set_status("Notes saved to Obsidian vault.")
            _ui(lambda: messagebox.showinfo("Done", f"Note saved to vault:\n{path}"))
        else:
            _set_status("Note generation failed.")

    threading.Thread(target=run, daemon=True).start()


def _generate_flashcards_gui():
    if not _transcript:
        messagebox.showwarning("No Transcript", "Transcribe audio first.")
        return
    _set_status("Generating flashcards...")

    def run():
        from core.anki import generate_flashcards, save_anki_csv
        cards = generate_flashcards(_transcript)
        if cards:
            path = save_anki_csv(cards)
            _set_status(f"Generated {len(cards)} flashcards.")
            _ui(lambda: messagebox.showinfo(
                "Done",
                f"Anki CSV saved to:\n{path}\n\nImport in Anki: File → Import"
            ))
        else:
            _set_status("Flashcard generation failed.")

    threading.Thread(target=run, daemon=True).start()


def _launch_tutor_gui():
    global _tutor_fn
    if not _transcript:
        messagebox.showwarning("No Transcript", "Transcribe audio first.")
        return
    _set_status("Loading tutor session...")

    def start_session():
        global _tutor_fn
        from core.tutor import create_tutor_session
        try:
            _tutor_fn = create_tutor_session(_transcript)
            _ui(_open_chat_window)
            _set_status("Tutor session active.")
        except Exception as e:
            _ui(lambda: messagebox.showerror("Error", f"Failed to start tutor: {e}"))
            _set_status("Tutor session failed.")

    threading.Thread(target=start_session, daemon=True).start()


def _open_chat_window():
    global _tutor_fn
    if not _tutor_fn:
        return

    chat_win = tk.Toplevel(_window)
    chat_win.title("Socratic Tutor")
    chat_win.geometry("620x520")
    chat_win.resizable(True, True)

    history_text = scrolledtext.ScrolledText(
        chat_win, state=tk.DISABLED, wrap=tk.WORD, font=("Arial", 10)
    )
    history_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))
    history_text.tag_config("you", foreground="#1a6fb5", font=("Arial", 10, "bold"))
    history_text.tag_config("tutor", foreground="#2e7d32")

    def append(speaker: str, msg: str, tag: str):
        history_text.config(state=tk.NORMAL)
        history_text.insert(tk.END, f"{speaker}:\n{msg}\n\n", tag)
        history_text.see(tk.END)
        history_text.config(state=tk.DISABLED)

    append("Tutor", "Ready to help! What didn't click in today's lecture?", "tutor")

    input_frame = tk.Frame(chat_win)
    input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

    msg_var = tk.StringVar()
    msg_entry = tk.Entry(input_frame, textvariable=msg_var, font=("Arial", 11))
    msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    msg_entry.focus()

    def send():
        msg = msg_var.get().strip()
        if not msg:
            return
        msg_var.set("")
        append("You", msg, "you")

        def get_reply():
            reply = _tutor_fn(msg)
            chat_win.after(0, lambda: append("Tutor", reply, "tutor"))

        threading.Thread(target=get_reply, daemon=True).start()

    msg_entry.bind("<Return>", lambda _: send())
    tk.Button(input_frame, text="Send", width=8, command=send).pack(side=tk.RIGHT, padx=(5, 0))


# ── Main window ───────────────────────────────────────────────────────────────
def launch_ui():
    global _window, _summary_widget, status_var
    from dotenv import load_dotenv
    load_dotenv()

    _window = tk.Tk()
    _window.title("Learning Bot")
    _window.geometry("540x660")
    _window.resizable(True, True)

    status_var = tk.StringVar(value="Idle.")

    # ── Session controls ──
    ctrl = tk.LabelFrame(_window, text="Session", padx=10, pady=8)
    ctrl.pack(fill=tk.X, padx=12, pady=(10, 4))

    tk.Button(ctrl, text="Record Lecture", width=22,
              command=_launch_recording_window).grid(row=0, column=0, padx=6, pady=4)
    tk.Button(ctrl, text="Transcribe Audio", width=22,
              command=_transcribe_gui).grid(row=0, column=1, padx=6, pady=4)

    # ── Rolling summary ──
    summary_frame = tk.LabelFrame(_window, text="Rolling Summary  (live during recording)", padx=6, pady=6)
    summary_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=4)

    _summary_widget = scrolledtext.ScrolledText(
        summary_frame, state=tk.DISABLED, wrap=tk.WORD, font=("Arial", 10), height=14
    )
    _summary_widget.pack(fill=tk.BOTH, expand=True)

    # ── Post-session actions ──
    actions = tk.LabelFrame(_window, text="Post-Session", padx=10, pady=8)
    actions.pack(fill=tk.X, padx=12, pady=4)

    tk.Button(actions, text="Generate Notes → Obsidian", width=26,
              command=_generate_notes_gui).grid(row=0, column=0, padx=6, pady=4)
    tk.Button(actions, text="Generate Flashcards (Anki)", width=26,
              command=_generate_flashcards_gui).grid(row=0, column=1, padx=6, pady=4)
    tk.Button(actions, text="Start Socratic Tutor", width=56,
              command=_launch_tutor_gui).grid(row=1, column=0, columnspan=2, padx=6, pady=4)

    # ── Status bar ──
    tk.Label(_window, textvariable=status_var, relief=tk.SUNKEN, anchor=tk.W,
             font=("Arial", 9)).pack(fill=tk.X, padx=12, pady=(4, 10))

    _window.mainloop()
