import tkinter as tk
from tkinter import messagebox
import os
import sys
import ctypes
import winreg

# =====================
# COLORS
# =====================
MAIN_BG = "#272B35"
SECOND_BG = "#31353E"
BUTTON_BG = "#393F4C"
TEXT_COLOR = "#9C9FA6"

# =====================
# ADMIN CHECK
# =====================
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, __file__, None, 1
    )

if not is_admin():
    run_as_admin()
    sys.exit()

# =====================
# REGISTRY HELPERS
# =====================
REG_PATH = r"Software\Microsoft\Windows NT\CurrentVersion\Winlogon"

def set_shell(value):
    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        REG_PATH,
        0,
        winreg.KEY_SET_VALUE
    )
    winreg.SetValueEx(key, "Shell", 0, winreg.REG_SZ, value)
    winreg.CloseKey(key)

def get_shell():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            REG_PATH,
            0,
            winreg.KEY_READ
        )
        value, _ = winreg.QueryValueEx(key, "Shell")
        winreg.CloseKey(key)
        return value
    except:
        return "explorer.exe"

# =====================
# MAIN APP
# =====================
class KioskApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kiosk Chrome Setup")
        self.root.geometry("420x300")
        self.root.configure(bg=MAIN_BG)

        # Title
        tk.Label(
            root,
            text="Chrome Kiosk Manager",
            bg=MAIN_BG,
            fg=TEXT_COLOR,
            font=("Segoe UI", 14, "bold")
        ).pack(pady=10)

        # Input frame
        frame = tk.Frame(root, bg=SECOND_BG)
        frame.pack(padx=20, pady=10, fill="x")

        tk.Label(
            frame,
            text="Enter Local IP:",
            bg=SECOND_BG,
            fg=TEXT_COLOR
        ).pack(anchor="w", padx=10, pady=5)

        self.ip_entry = tk.Entry(
            frame,
            bg=BUTTON_BG,
            fg=TEXT_COLOR,
            insertbackground=TEXT_COLOR,
            relief="flat"
        )
        self.ip_entry.pack(fill="x", padx=10, pady=5)

        # Buttons frame
        btn_frame = tk.Frame(root, bg=MAIN_BG)
        btn_frame.pack(pady=10)

        tk.Button(
            btn_frame,
            text="Create Kiosk",
            bg=BUTTON_BG,
            fg=TEXT_COLOR,
            relief="flat",
            width=15,
            command=self.create_kiosk
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            btn_frame,
            text="Restore Desktop",
            bg=BUTTON_BG,
            fg=TEXT_COLOR,
            relief="flat",
            width=15,
            command=self.restore_desktop
        ).grid(row=0, column=1, padx=5)

        # Status
        self.status = tk.Label(
            root,
            text=f"Current shell: {get_shell()}",
            bg=MAIN_BG,
            fg=TEXT_COLOR
        )
        self.status.pack(pady=10)

    def create_kiosk(self):
        ip = self.ip_entry.get().strip()

        if not ip:
            messagebox.showerror("Error", "Enter IP address")
            return

        url = f"http://{ip}:8000"

        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        if not os.path.exists(chrome_path):
            chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

        if not os.path.exists(chrome_path):
            self.status.config(text="Status: Chrome not found")
            return

        try:
            os.makedirs(r"C:\KioskApp", exist_ok=True)
            bat_path = r"C:\KioskApp\launch_kiosk.bat"

            with open(bat_path, "w") as f:
                f.write(f'"{chrome_path}" --kiosk --app={url}')

            set_shell(bat_path)

            self.status.config(
                text=f"Kiosk set → {url}\n(Log out to apply)"
            )

        except Exception as e:
            self.status.config(text=f"Error: {e}")

    def restore_desktop(self):
        try:
            set_shell("explorer.exe")

            self.status.config(
                text="Desktop restored (explorer.exe)\n(Log out to apply)"
            )

        except Exception as e:
            self.status.config(text=f"Error: {e}")


# =====================
# RUN
# =====================
root = tk.Tk()
app = KioskApp(root)
root.mainloop()