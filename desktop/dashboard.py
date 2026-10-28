"""Five-page themed desktop dashboard. Preserves original bot subprocess."""
import queue
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox

from appearance import DEFAULT_THEME, THEMES, load_theme, save_theme
from radio_config import read_radio, save_radio


def launch(root_path, bot_path, tcp_probe):
    root = tk.Tk()
    root.title("Meshing Around")
    root.geometry("1000x680")
    root.minsize(800, 540)
    selected_theme = tk.StringVar(value=load_theme())
    status = tk.StringVar(value="Stopped")
    current_page = tk.StringVar(value="Dashboard")
    config = root_path / "config.ini"
    template = root_path / "config.template"
    transport, address = read_radio(config if config.exists() else template)
    mode = tk.StringVar(value=transport)
    endpoint = tk.StringVar(value=address or "meshtastic.local")
    events = queue.Queue()
    process = [None]
    colored = []
    pages = {}
    nav_buttons = []

    def frame(parent, role="panel"):
        widget = tk.Frame(parent, bd=0)
        colored.append((widget, role))
        return widget

    def label(parent, text=None, variable=None, size=12, muted=False):
        widget = tk.Label(parent, text=text, textvariable=variable, anchor="w",
                          font=("Helvetica", size, "normal"))
        colored.append((widget, "muted" if muted else "text"))
        return widget

    def button(parent, text, command):
        widget = tk.Button(parent, text=text, command=command, relief="flat",
                           bd=0, padx=15, pady=9, cursor="hand2")
        colored.append((widget, "button"))
        return widget

    shell = frame(root, "bg")
    shell.pack(fill="both", expand=True)
    sidebar = frame(shell, "sidebar")
    sidebar.pack(side="left", fill="y")
    label(sidebar, "MESHING AROUND", size=18).pack(padx=22, pady=(32, 12))
    label(sidebar, "DESKTOP CONTROL", muted=True).pack(padx=22, pady=(0, 28))
    workspace = frame(shell, "bg")
    workspace.pack(side="left", fill="both", expand=True, padx=25, pady=24)
    header = frame(workspace, "bg")
    header.pack(fill="x")
    label(header, variable=current_page, size=22).pack(side="left")
    label(header, variable=status, muted=True).pack(side="right")
    body = frame(workspace, "bg")
    body.pack(fill="both", expand=True, pady=25)
    names = ("Dashboard", "Connection", "Bot Controls", "Logs", "Settings")
    for name in names:
        pages[name] = frame(body, "bg")

    def show(name):
        for page in pages.values():
            page.pack_forget()
        current_page.set(name)
        pages[name].pack(fill="both", expand=True)

    for name in names:
        widget = button(sidebar, name, lambda name=name: show(name))
        widget.pack(fill="x", padx=12, pady=3)
        nav_buttons.append(widget)

    def heading(page, title, description):
        card = frame(page)
        card.pack(fill="x", pady=(0, 20))
        label(card, title, size=17).pack(anchor="w", padx=18, pady=(18, 5))
        label(card, description, muted=True).pack(anchor="w", padx=18, pady=(0, 18))

    heading(pages["Dashboard"], "System overview",
            "Bot process status and desktop diagnostics")
    label(pages["Dashboard"], variable=status, size=16).pack(anchor="w", pady=12)
    label(pages["Dashboard"], "A running process does not prove radio connectivity.",
          muted=True).pack(anchor="w")

    heading(pages["Connection"], "Radio connection",
            "Select TCP, Bluetooth LE or USB/serial and save before starting")
    ttk.Combobox(pages["Connection"], textvariable=mode,
                 values=("tcp", "ble", "serial"), state="readonly").pack(anchor="w", pady=10)
    label(pages["Connection"], "Hostname:port, BLE address, or serial device path").pack(anchor="w")
    entry = tk.Entry(pages["Connection"], textvariable=endpoint, bd=6, relief="flat")
    colored.append((entry, "input"))
    entry.pack(fill="x", pady=(8, 20))

    def log(message):
        output.configure(state="normal")
        output.insert("end", message.rstrip() + "\n")
        output.see("end")
        output.configure(state="disabled")

    def save():
        if process[0] is not None and process[0].poll() is None:
            messagebox.showwarning("Bot running", "Stop the bot before editing radio settings.")
            return
        try:
            save_radio(config, template, mode.get(), endpoint.get())
            log("Radio settings saved. A backup is kept for existing configurations.")
        except (OSError, ValueError) as exc:
            messagebox.showerror("Save failed", str(exc))

    def test():
        if mode.get() != "tcp":
            log("TCP test applies to TCP connections only.")
            return
        address = endpoint.get()
        def worker():
            try:
                tcp_probe(address)
                events.put(("log", f"TCP reachable: {address}; radio handshake unverified"))
            except (OSError, ValueError) as exc:
                events.put(("log", f"TCP test failed: {exc}"))
        threading.Thread(target=worker, daemon=True).start()

    actions = frame(pages["Connection"], "bg")
    actions.pack(anchor="w")
    button(actions, "Save radio settings", save).pack(side="left", padx=(0, 10))
    button(actions, "Test TCP", test).pack(side="left")

    def start():
        if process[0] is not None and process[0].poll() is None:
            return
        try:
            command = [str(bot_path)] if getattr(sys, "frozen", False) else [sys.executable, "-u", str(bot_path)]
            child = subprocess.Popen(command,
                                     cwd=root_path, stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT, text=True, bufsize=1)
        except OSError as exc:
            messagebox.showerror("Launch failed", str(exc))
            return
        process[0] = child
        status.set("Running • radio unverified")
        log("Started original mesh_bot.py using saved radio settings.")
        def reader():
            for line in child.stdout:
                events.put(("log", line))
            events.put(("exit", str(child.wait())))
        threading.Thread(target=reader, daemon=True).start()

    def stop():
        if process[0] is not None and process[0].poll() is None:
            process[0].terminate()
            log("Stop requested")

    heading(pages["Bot Controls"], "Bot controls",
            "Start and stop the original Meshtastic bot")
    actions = frame(pages["Bot Controls"], "bg")
    actions.pack(anchor="w")
    button(actions, "Start bot", start).pack(side="left", padx=(0, 10))
    button(actions, "Stop bot", stop).pack(side="left")

    label(pages["Logs"], "Bot output and diagnostics", muted=True).pack(anchor="w", pady=(0, 10))
    output = tk.Text(pages["Logs"], state="disabled", bd=0, padx=12, pady=12,
                     font=("Menlo", 11), wrap="word")
    colored.append((output, "input"))
    output.pack(fill="both", expand=True)

    heading(pages["Settings"], "Appearance",
            "Choose a color theme; your selection persists across restarts")
    ttk.Combobox(pages["Settings"], textvariable=selected_theme,
                 values=tuple(THEMES), state="readonly", width=26).pack(anchor="w", pady=10)

    def apply_theme(persist=False):
        colors = THEMES[selected_theme.get()]
        root.configure(bg=colors["bg"])
        # First paint all containers, then text so label backgrounds follow parents.
        for widget, role in colored:
            if role in ("bg", "panel", "sidebar"):
                widget.configure(bg=colors[role])
        for widget, role in colored:
            if role == "text":
                widget.configure(bg=widget.master.cget("bg"), fg=colors["fg"])
            elif role == "muted":
                widget.configure(bg=widget.master.cget("bg"), fg=colors["muted"])
            elif role == "button":
                widget.configure(bg=colors["panel"], fg=colors["accent"],
                                 activebackground=colors["input"], activeforeground=colors["fg"])
            elif role == "input":
                widget.configure(bg=colors["input"], fg=colors["fg"],
                                 insertbackground=colors["fg"])
        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("TCombobox", fieldbackground=colors["input"],
                        background=colors["panel"], foreground=colors["fg"],
                        arrowcolor=colors["accent"])
        if persist:
            try:
                save_theme(selected_theme.get())
            except OSError as exc:
                messagebox.showerror("Theme not saved", str(exc))

    def reset_theme():
        selected_theme.set(DEFAULT_THEME)
        apply_theme(True)

    # Attach after combobox creation; only the theme chooser changes appearance.
    theme_chooser = pages["Settings"].winfo_children()[-1]
    theme_chooser.bind("<<ComboboxSelected>>", lambda event: apply_theme(True))
    button(pages["Settings"], "Restore default", reset_theme).pack(anchor="w", pady=12)

    def poll():
        try:
            while True:
                kind, value = events.get_nowait()
                if kind == "log":
                    log(value)
                else:
                    status.set(f"Stopped • exit code {value}")
                    process[0] = None
        except queue.Empty:
            pass
        root.after(100, poll)

    def close():
        stop()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", close)
    apply_theme()
    show("Dashboard")
    root.after(100, poll)
    root.mainloop()
