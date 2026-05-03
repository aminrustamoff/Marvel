import tkinter as tk
from tkinter import scrolledtext, messagebox
import subprocess
import threading
import socket
import webbrowser
import os
import signal
import ctypes


# =========================
# CONFIGURATION
# =========================

# Automatically gets current folder
DJANGO_PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

# Change this if needed
DJANGO_PORT = 8000

# =========================
# COLORS
# =========================

MAIN_BG = "#272B35"
SECOND_BG = "#31353E"
BUTTON_BG = "#393F4C"

TEXT_COLOR = "#9C9FA6"
TERMINAL_TEXT = "#50703f"

# =========================
# GLOBALS
# =========================

django_process = None


# =========================
# GET LOCAL IP ADDRESS
# =========================
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))

        ip = s.getsockname()[0]
        s.close()

        return ip

    except Exception:
        return "127.0.0.1"


# =========================
# START DJANGO SERVER
# =========================
def start_server():
    global django_process

    if django_process is not None:
        messagebox.showinfo("Server Running", "Django server is already running.")
        return

    ip = get_local_ip()

    try:
        command = [
            "python",
            "manage.py",
            "runserver",
            f"0.0.0.0:{DJANGO_PORT}"
        ]

        django_process = subprocess.Popen(
            command,
            cwd=DJANGO_PROJECT_PATH,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            shell=True
        )

        log_terminal.insert(tk.END, f"Starting Django server at {ip}:{DJANGO_PORT}\n\n")
        log_terminal.see(tk.END)

        threading.Thread(target=read_logs, daemon=True).start()

    except Exception as e:
        messagebox.showerror("Error", str(e))


# =========================
# STOP DJANGO SERVER
# =========================
def stop_server():
    global django_process

    if django_process is None:
        messagebox.showinfo("Server Stopped", "No running Django server.")
        return

    try:
        if os.name == "nt":
            django_process.send_signal(signal.CTRL_BREAK_EVENT)
        else:
            django_process.terminate()

        django_process.kill()
        django_process = None

        log_terminal.insert(tk.END, "\nDjango server stopped.\n")
        log_terminal.see(tk.END)

    except Exception as e:
        messagebox.showerror("Error", str(e))


# =========================
# READ TERMINAL LOGS
# =========================
def read_logs():
    global django_process

    try:
        for line in django_process.stdout:
            log_terminal.insert(tk.END, line)
            log_terminal.see(tk.END)

    except Exception as e:
        log_terminal.insert(tk.END, f"\nError reading logs: {e}\n")


# =========================
# OPEN BROWSER LINKS
# =========================
def open_admin():

    # ==========================================
    # CHANGE THIS URL IF YOUR ADMIN URL DIFFERS
    # ==========================================
    url = f"http://127.0.0.1:{DJANGO_PORT}/admin/"

    webbrowser.open(url)


def open_results():

    # ==================================================
    # CHANGE THIS URL TO YOUR RESULTS PANEL URL
    # Example:
    # /results/
    # /dashboard/
    # /teacher/results/
    # ==================================================
    url = f"http://127.0.0.1:{DJANGO_PORT}/results/"

    webbrowser.open(url)


# =========================
# CLOSE APP SAFELY
# =========================
def on_close():
    stop_server()
    root.destroy()


# =========================
# HOVER EFFECTS
# =========================
def on_enter(e):
    e.widget["background"] = SECOND_BG


def on_leave(e):
    e.widget["background"] = BUTTON_BG


# =========================
# TKINTER UI
# =========================

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

root = tk.Tk()

root.title("Marvel - Mock Test Server Launcher")

# ==========================================
# CHANGE WINDOW ICON HERE
# Put your .ico file in the same directory
# Example: marvel.ico
# ==========================================
# root.iconbitmap("marvel.ico")

# Modern higher resolution
root.geometry("900x600")

# Disable resizing
root.resizable(False, False)

# Main background
root.configure(bg=MAIN_BG)

# =========================
# HEADER
# =========================

ip_address = get_local_ip()

header_frame = tk.Frame(
    root,
    bg=MAIN_BG
)

header_frame.pack(fill="x", pady=(20, 10))

title_label = tk.Label(
    header_frame,
    text="Marvel Mock Test Server",
    font=("Segoe UI", 22, "bold"),
    bg=MAIN_BG,
    fg="white"
)

title_label.pack()

ip_label = tk.Label(
    header_frame,
    text=f"IPv4 Address: {ip_address}",
    font=("Segoe UI", 12),
    bg=MAIN_BG,
    fg=TEXT_COLOR
)

ip_label.pack(pady=(5, 0))

# =========================
# TERMINAL CONTAINER
# =========================

terminal_frame = tk.Frame(
    root,
    bg=SECOND_BG,
    bd=0,
    height=350
)

terminal_frame.pack(
    padx=30,
    pady=20,
    fill="both",
    expand=False
)

terminal_frame.pack_propagate(False)

log_terminal = scrolledtext.ScrolledText(
    terminal_frame,
    width=140,
    height=35,
    bg=SECOND_BG,
    fg=TERMINAL_TEXT,
    insertbackground=TEXT_COLOR,
    relief="flat",
    borderwidth=0,
    font=("Consolas", 11),
    padx=15,
    pady=15
)

log_terminal.pack(fill="both", expand=True)

# =========================
# BUTTON SECTION
# =========================

bottom_frame = tk.Frame(
    root,
    bg=MAIN_BG
)

bottom_frame.pack(pady=(0, 25))

button_style = {
    "font": ("Segoe UI", 11, "bold"),
    "width": 18,
    "height": 2,
    "bg": BUTTON_BG,
    "fg": TEXT_COLOR,
    "activebackground": SECOND_BG,
    "activeforeground": "white",
    "relief": "flat",
    "borderwidth": 0,
    "cursor": "hand2"
}

start_button = tk.Button(
    bottom_frame,
    text="Launch Server",
    command=start_server,
    **button_style
)

start_button.grid(row=0, column=0, padx=8)

admin_button = tk.Button(
    bottom_frame,
    text="Open Admin Panel",
    command=open_admin,
    **button_style
)

admin_button.grid(row=0, column=1, padx=8)

results_button = tk.Button(
    bottom_frame,
    text="Open Results Panel",
    command=open_results,
    **button_style
)

results_button.grid(row=0, column=2, padx=8)

stop_button = tk.Button(
    bottom_frame,
    text="Stop Server",
    command=stop_server,
    **button_style
)

stop_button.grid(row=0, column=3, padx=8)

# =========================
# BUTTON HOVER EFFECTS
# =========================

buttons = [
    start_button,
    admin_button,
    results_button,
    stop_button
]

for button in buttons:
    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)

# =========================
# WINDOW CLOSE EVENT
# =========================

root.protocol("WM_DELETE_WINDOW", on_close)

# =========================
# START TKINTER LOOP
# =========================

root.mainloop()