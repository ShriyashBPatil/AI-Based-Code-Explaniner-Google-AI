import google.generativeai as genai
import tkinter as tk
from tkinter import scrolledtext, filedialog
import time
from docx import Document 
import threading  

def configure_genai(api_key):
    genai.configure(api_key=api_key)
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )
    return model


api_key = "YOUR API KEY HERE"
model = configure_genai(api_key)

def send_message(message): 
    chat_session = model.start_chat(
        history=[]
    )
    response = chat_session.send_message(message)
    return response.text

def type_text(widget, text):
    widget.config(state=tk.NORMAL)
    for char in text:
        if text.startswith("**"):
            widget.insert(tk.END, char, "bold")
        else:
            widget.insert(tk.END, char)
        widget.update()
        widget.see(tk.END) 
        time.sleep(0.01)  
    widget.insert(tk.END, "\n")
    widget.config(state=tk.DISABLED)

def on_send():
    def send_message_thread():
        user_message = user_input.get()
        chat_history.config(state=tk.NORMAL)
        chat_history.insert(tk.END, "You: ", "bold")
        chat_history.insert(tk.END, user_message + "\n")
        chat_history.config(state=tk.DISABLED)
        user_input.delete(0, tk.END)
        
        bot_response = send_message(user_message)
        chat_history.config(state=tk.NORMAL)
        chat_history.insert(tk.END, "Bot: ", "bold")
        chat_history.config(state=tk.DISABLED)
        type_text(chat_history, bot_response)
        
        current_input.config(state=tk.NORMAL)
        current_input.insert(tk.END, "You: ", "bold")
        current_input.insert(tk.END, user_message + "\n")
        current_input.insert(tk.END, "Bot: ", "bold")
        current_input.insert(tk.END, bot_response + "\n")
        current_input.config(state=tk.DISABLED)
    
    threading.Thread(target=send_message_thread).start()

def export_to_docx(content):
    doc = Document()
    doc.add_heading('Code Explanation', 0)
    doc.add_paragraph(content)
    file_path = filedialog.asksaveasfilename(defaultextension=".docx", filetypes=[("Word Documents", "*.docx")])
    if file_path:
        doc.save(file_path)

def open_file():
    def open_file_thread():
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, 'r') as file:
                file_content = file.read()
                code_display.config(state=tk.NORMAL)
                code_display.delete(1.0, tk.END)
                code_display.insert(tk.END, file_content)
                code_display.config(state=tk.DISABLED)
                
                explanation_request = f"Explain this code in detail:\n{file_content}"
                bot_response = send_message(explanation_request)
           
                chat_history.config(state=tk.NORMAL)
                chat_history.insert(tk.END, "Code:\n", "bold")
                chat_history.insert(tk.END, file_content + "\n\n")
                chat_history.insert(tk.END, "Bot: ", "bold")
                chat_history.config(state=tk.DISABLED)
                type_text(chat_history, bot_response)
              
                global last_explanation
                last_explanation = bot_response

            update_line_numbers()
    
    threading.Thread(target=open_file_thread).start()

def update_line_numbers(event=None):
    code_content = code_display.get("1.0", "end-1c")
    lines = code_content.split('\n')
    line_numbers = "\n".join(str(i + 1) for i in range(len(lines)))
    line_numbers_display.config(state=tk.NORMAL)
    line_numbers_display.delete("1.0", tk.END)
    line_numbers_display.insert("1.0", line_numbers)
    line_numbers_display.config(state=tk.DISABLED)

def on_scroll(event):
    code_display.yview_scroll(int(-1*(event.delta/120)), "units")
    line_numbers_display.yview_scroll(int(-1*(event.delta/120)), "units")

root = tk.Tk()
root.title("Code Explainer")
root.geometry("800x600")
root.configure(bg="#f0f0f0")

title_label = tk.Label(root, text="Code Explainer", font=("Helvetica", 16, "bold"), bg="#f0f0f0")
title_label.pack(pady=10)

description_label = tk.Label(root, text="Here you can get your code explanation", font=("Helvetica", 12), bg="#f0f0f0")
description_label.pack(pady=5)

main_frame = tk.Frame(root, bg="#f0f0f0")
main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

chat_frame = tk.Frame(main_frame, bg="#f0f0f0")
chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

input_frame = tk.Frame(main_frame, bg="#f0f0f0")
input_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

chat_history_label = tk.Label(chat_frame, text="Current Input", font=("Helvetica", 12, "bold"), bg="#f0f0f0")
chat_history_label.pack(pady=5)
chat_history = scrolledtext.ScrolledText(chat_frame, state='disabled', wrap=tk.WORD, bg="#ffffff", fg="#000000", font=("Helvetica", 10))
chat_history.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
chat_history.tag_configure("bold", font=("Helvetica", 10, "bold"))

current_input_label = tk.Label(chat_frame, text="Chat History", font=("Helvetica", 12, "bold"), bg="#f0f0f0")
current_input_label.pack(pady=5)
current_input = tk.Text(chat_frame, state='disabled', height=10, wrap=tk.WORD, bg="#ffffff", fg="#000000", font=("Helvetica", 10))
current_input.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
current_input.tag_configure("bold", font=("Helvetica", 10, "bold"))

code_display_label = tk.Label(input_frame, text="Code Display", font=("Helvetica", 12, "bold"), bg="#f0f0f0")
code_display_label.pack(pady=5)

code_frame = tk.Frame(input_frame)
code_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

line_numbers_display = tk.Text(code_frame, width=4, state='disabled', wrap=tk.NONE, bg="#f0f0f0", fg="#000000", font=("Helvetica", 10))
line_numbers_display.pack(side=tk.LEFT, fill=tk.Y)

code_display = scrolledtext.ScrolledText(code_frame, state='disabled', wrap=tk.WORD, width=50, bg="#ffffff", fg="#000000", font=("Helvetica", 10))
code_display.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

code_display.bind("<KeyRelease>", update_line_numbers)
code_display.bind("<MouseWheel>", on_scroll)
line_numbers_display.bind("<MouseWheel>", on_scroll)

user_input_label = tk.Label(input_frame, text="Your Input", font=("Helvetica", 12, "bold"), bg="#f0f0f0")
user_input_label.pack(pady=5)
user_input = tk.Entry(input_frame, width=50, bg="#ffffff", fg="#000000", font=("Helvetica", 10))
user_input.pack(padx=10, pady=10, fill=tk.X, expand=True)

send_button = tk.Button(input_frame, text="Send", command=on_send, bg="#4CAF50", fg="#ffffff", font=("Helvetica", 10, "bold"))
send_button.pack(padx=10, pady=10)

file_button = tk.Button(input_frame, text="Upload File", command=open_file, bg="#2196F3", fg="#ffffff", font=("Helvetica", 10, "bold"))
file_button.pack(padx=10, pady=10)

export_button = tk.Button(input_frame, text="Export Explanation", command=lambda: export_to_docx(last_explanation), bg="#FF9800", fg="#ffffff", font=("Helvetica", 10, "bold"))
export_button.pack(padx=10, pady=10)

root.mainloop()