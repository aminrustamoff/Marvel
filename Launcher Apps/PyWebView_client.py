import sys
import time
import urllib.request
import tkinter as tk
from tkinter import simpledialog, messagebox

import webview


# =========================
# CONFIG
# =========================

EXAM_URL = "http://127.0.0.1:8000/"  # Django local server URL
ENTER_PASSWORD = "12345"
EXIT_PASSWORD = "admin123"

APP_TITLE = "Marvel Academy IELTS Mock Test"


# =========================
# TKINTER PASSWORD WINDOW
# =========================

def ask_password(title, message):
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    password = simpledialog.askstring(
        title,
        message,
        show="*",
        parent=root
    )

    root.destroy()
    return password


def show_error(message):
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    messagebox.showerror("Error", message, parent=root)
    root.destroy()


def check_django_server(url, retries=10, delay=1):
    for _ in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status < 500:
                    return True
        except Exception:
            time.sleep(delay)

    return False


# =========================
# LOCKDOWN JAVASCRIPT
# =========================

LOCKDOWN_JS = r"""
(function () {
    console.log("Exam lockdown JS loaded");

    // Disable right click
    document.addEventListener("contextmenu", function (e) {
        e.preventDefault();
        return false;
    }, true);

    // Disable dragging
    document.addEventListener("dragstart", function (e) {
        e.preventDefault();
        return false;
    }, true);

    // Prevent opening new windows/tabs from JS
    window.open = function () {
        console.log("window.open blocked");
        return null;
    };

    // Block common cheating/browser shortcuts inside the WebView
    document.addEventListener("keydown", function (e) {
        const key = e.key;
        const lowerKey = key.toLowerCase();

        const target = e.target;
        const isTyping =
            target.tagName === "INPUT" ||
            target.tagName === "TEXTAREA" ||
            target.isContentEditable;

        // Block F1-F12
        if (/^F\d{1,2}$/.test(key)) {
            e.preventDefault();
            e.stopPropagation();
            return false;
        }

        // Block Alt combinations: Alt+Left, Alt+Right, Alt+Tab etc.
        // Note: OS-level Alt+Tab may be captured by Windows before JS sees it.
        if (e.altKey) {
            e.preventDefault();
            e.stopPropagation();
            return false;
        }

        // Block Ctrl/Cmd shortcuts
        if (e.ctrlKey || e.metaKey) {
            const blockedKeys = [
                "t", // new tab
                "n", // new window
                "w", // close tab/window
                "r", // refresh
                "l", // address bar
                "p", // print
                "s", // save
                "o", // open file
                "u", // view source
                "h", // history
                "j", // downloads
                "d", // bookmark
                "f", // find
                "+",
                "-",
                "0"
            ];

            if (blockedKeys.includes(lowerKey)) {
                e.preventDefault();
                e.stopPropagation();
                return false;
            }
        }

        // Block Backspace navigation only when not typing
        if (key === "Backspace" && !isTyping) {
            e.preventDefault();
            e.stopPropagation();
            return false;
        }

        // Block Escape
        if (key === "Escape") {
            e.preventDefault();
            e.stopPropagation();
            return false;
        }
    }, true);

    // Prevent browser back button behaviour
    try {
        history.pushState(null, "", location.href);
        window.addEventListener("popstate", function () {
            history.pushState(null, "", location.href);
        });
    } catch (err) {
        console.log("History lock failed", err);
    }
})();
"""


# =========================
# PYWEBVIEW API
# =========================

class ExamApi:
    def __init__(self):
        self.window = None
        self.authorized_exit = False

    def set_window(self, window):
        self.window = window

    def request_exit(self):
        """
        This can be called from Django template:
        window.pywebview.api.request_exit()
        """
        password = ask_password(
            "Exit Password",
            "Enter admin password to exit the exam:"
        )

        if password == EXIT_PASSWORD:
            self.authorized_exit = True
            if self.window:
                self.window.destroy()
            return {"ok": True}

        return {"ok": False, "message": "Wrong password"}


api = ExamApi()


def inject_lockdown_js(window):
    try:
        window.evaluate_js(LOCKDOWN_JS)
    except Exception as e:
        print("Failed to inject lockdown JS:", e)


def on_closing(*args):
    """
    If user tries Alt+F4 or closes the window,
    ask password before allowing exit.
    pywebview allows cancelling close by returning False.
    """
    if api.authorized_exit:
        return True

    password = ask_password(
        "Exit Password",
        "Enter admin password to close the exam app:"
    )

    if password == EXIT_PASSWORD:
        api.authorized_exit = True
        return True

    return False


def main():
    # 1. Ask password before opening exam
    password = ask_password(
        "Exam Login",
        "Enter password to start the exam:"
    )

    if password != ENTER_PASSWORD:
        show_error("Wrong password. Access denied.")
        sys.exit(1)

    # 2. Check Django server
    if not check_django_server(EXAM_URL):
        show_error(
            f"Django server is not running.\n\n"
            f"Please start Django first:\n"
            f"python manage.py runserver 127.0.0.1:8000\n\n"
            f"Then run this app again."
        )
        sys.exit(1)

    # 3. Create exam window
    window = webview.create_window(
        title=APP_TITLE,
        url=EXAM_URL,
        js_api=api,
        fullscreen=True,
        frameless=True,
        easy_drag=False,
        on_top=True,
        confirm_close=False,
        text_select=False,
        zoomable=False,
        draggable=False
    )

    api.set_window(window)

    # pywebview supports window events such as loaded and closing. 
    # returning False from closing event cancels closing.
    window.events.loaded += inject_lockdown_js
    window.events.closing += on_closing

    webview.start(debug=False)


if __name__ == "__main__":
    main()