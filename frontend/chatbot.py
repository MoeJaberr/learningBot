import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import openai
from PIL import Image
import pytesseract
import fitz  # PyMuPDF
from core.obsidian import generate_obsidian_notes

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise EnvironmentError("OPENAI_API_KEY not found in environment.")

client = openai.OpenAI(api_key=OPENAI_API_KEY)
chat_history = []

def extract_text_from_file(filepath):
    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".txt":
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    elif ext == ".pdf":
        text = ""
        with fitz.open(filepath) as doc:
            for page in doc:
                text += page.get_text()
        return text

    elif ext in [".png", ".jpg", ".jpeg"]:
        return pytesseract.image_to_string(Image.open(filepath))

    else:
        messagebox.showerror("Unsupported File", f"Unsupported file type: {ext}")
        return ""

def load_study_materials():
    file_paths = filedialog.askopenfilenames(
        title="Select Study Materials",
        filetypes=[
            ("Supported files", "*.txt *.pdf *.png *.jpg *.jpeg"),
            ("Text files", "*.txt"),
            ("PDF files", "*.pdf"),
            ("Images", "*.png *.jpg *.jpeg")
        ],
        initialdir="output"
    )

    if not file_paths:
        return None

    full_text = ""
    for path in file_paths:
        full_text += extract_text_from_file(path) + "\n\n"

    return full_text

def ask_chatgpt(study_material, user_input):
    global chat_history

    if not chat_history:
        system_msg = {
            "role": "system",
            "content": (
                "You are a Socratic tutor helping a university student understand study material. "
                "Ask one guiding question at a time. Adapt based on the student's responses. "
                "Gently correct misunderstandings. Use the provided content as context."
            )
        }
        material_msg = {
            "role": "user",
            "content": f"Here is the study material:\n{study_material[:4000]}"
        }
        chat_history.extend([system_msg, material_msg])

    chat_history.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="gpt-4",
        messages=chat_history
    )
    reply = response.choices[0].message.content
    chat_history.append({"role": "assistant", "content": reply})
    return reply

def export_notes():
    global chat_history
    full_convo = "\n".join(f"{msg['role'].capitalize()}: {msg['content']}" for msg in chat_history if msg["role"] != "system")
    note = generate_obsidian_notes(full_convo, client)

    if not note:
        messagebox.showerror("Error", "Failed to generate Obsidian note.")
        return

    os.makedirs("obsidian_notes", exist_ok=True)
    filename = os.path.join("obsidian_notes", "socratic_notes.md")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(note)

    messagebox.showinfo("Success", f"Note saved to: {filename}")

def launch_chatbot():
    study_material = load_study_materials()
    if not study_material:
        messagebox.showerror("Error", "No valid study material selected.")
        return

    def on_send():
        user_input = user_entry.get()
        user_entry.delete(0, tk.END)
        chat_area.insert(tk.END, f"You: {user_input}\n", "user")

        if user_input.lower().strip() == "i have no more questions":
            export_notes()
            root.destroy()
            return

        reply = ask_chatgpt(study_material, user_input)
        chat_area.insert(tk.END, f"Tutor: {reply}\n\n", "assistant")
        chat_area.see(tk.END)

    root = tk.Toplevel()
    root.title("Socratic Tutor Chatbot")
    root.geometry("700x550")

    chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD)
    chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    chat_area.tag_config("user", foreground="blue")
    chat_area.tag_config("assistant", foreground="green")

    user_entry = tk.Entry(root, width=80)
    user_entry.pack(side=tk.LEFT, padx=10, pady=10)
    user_entry.focus()

    send_button = tk.Button(root, text="Send", command=on_send)
    send_button.pack(side=tk.RIGHT, padx=10, pady=10)

    root.mainloop()
