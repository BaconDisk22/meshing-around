"""Five-page themed desktop dashboard. Preserves original bot subprocess."""
import queue
import subprocess
import sys
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

from appearance import DEFAULT_THEME, THEMES, load_theme, save_theme
from radio_config import read_radio, save_radio
import radio_probe
from startup_preflight import check_paths
from log_export import export_logs


def launch(root_path, bot_path, tcp_probe):
    root = tk.Tk()
    root.title("Meshing Around")
    root.geometry("1120x740")
    root.minsize(940, 620)
    selected_theme = tk.StringVar(value=load_theme())
    status = tk.StringVar(value="Stopped")
    radio_status = tk.StringVar(value="Radio not tested yet. Use Connection → Test connection.")
    last_event = tk.StringVar(value="No radio events yet")
    current_page = tk.StringVar(value="Dashboard")
    config = root_path / "config.ini"
    template = root_path / "config.template"
    transport, address = read_radio(config if config.exists() else template)
    mode = tk.StringVar(value=transport)
    endpoint = tk.StringVar(value=address or "meshtastic.local")
    events = queue.Queue()
    process = [None]
    probe_active = [False]
    probe_settings = [None]
    closing = [False]
    stopping = [False]
    colored = []
    pages = {}
    nav_buttons = []

    def frame(parent, role="panel"):
        widget = tk.Frame(parent, bd=0)
        colored.append((widget, role))
        return widget

    def label(parent, text=None, variable=None, size=12, muted=False):
        widget = tk.Label(parent, text=text, textvariable=variable, anchor="w",
                          font=("Helvetica Neue", size + (1 if muted else 2), "normal" if muted else "bold"))
        colored.append((widget, "muted" if muted else "text"))
        return widget

    def button(parent, text, command):
        widget = tk.Button(parent, text=text, command=command, relief="flat",
                           bd=0, padx=18, pady=12, cursor="hand2",
                           font=("Helvetica Neue", 14, "bold"), anchor="w")
        colored.append((widget, "button"))
        return widget

    shell = frame(root, "bg")
    shell.pack(fill="both", expand=True)
    sidebar = frame(shell, "sidebar")
    sidebar.pack(side="left", fill="y")
    sidebar.configure(width=246)
    sidebar.pack_propagate(False)
    label(sidebar, "MESHING AROUND", size=16).pack(anchor="w", padx=20, pady=(32, 12))
    label(sidebar, "RADIO CONTROL CENTER", muted=True).pack(anchor="w", padx=20, pady=(0, 30))
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
        for nav_name, nav_widget in nav_buttons:
            nav_widget.configure(relief="sunken" if nav_name == name else "flat",
                                 bd=2 if nav_name == name else 0)
        for page in pages.values():
            page.pack_forget()
        current_page.set(name)
        pages[name].pack(fill="both", expand=True)

    for name in names:
        widget = button(sidebar, name, lambda name=name: show(name))
        widget.pack(fill="x", padx=12, pady=5)
        nav_buttons.append((name, widget))

    def heading(page, title, description):
        card = frame(page)
        card.pack(fill="x", pady=(0, 20))
        label(card, title, size=17).pack(anchor="w", padx=18, pady=(18, 5))
        label(card, description, muted=True).pack(anchor="w", padx=18, pady=(0, 18))

    heading(pages["Dashboard"], "System overview",
            "Bot process status and desktop diagnostics")
    def status_card(title, variable):
        card = frame(pages["Dashboard"])
        card.pack(fill="x", pady=8)
        label(card, title, size=12, muted=True).pack(anchor="w", padx=22, pady=(18, 5))
        label(card, variable=variable, size=15).pack(anchor="w", padx=22, pady=(0, 20))

    status_card("BOT STATUS", status)
    status_card("RADIO CONNECTION", radio_status)
    status_card("RECENT ACTIVITY", last_event)

    quick_actions = frame(pages["Dashboard"], "bg")
    quick_actions.pack(fill="x", pady=(18, 8))
    label(quick_actions, "QUICK NAVIGATION", size=11, muted=True).pack(anchor="w", pady=(0, 10))
    quick_buttons = frame(quick_actions, "bg")
    quick_buttons.pack(anchor="w")
    button(quick_buttons, "Radio setup", lambda: show("Connection")).pack(side="left", padx=(0, 12))
    button(quick_buttons, "Bot controls", lambda: show("Bot Controls")).pack(side="left", padx=(0, 12))
    button(quick_buttons, "View logs", lambda: show("Logs")).pack(side="left")

    heading(pages["Connection"], "Radio connection",
            "Select TCP, Bluetooth LE or USB/serial, test it, then save before starting")
    label(pages["Connection"], "CONNECTION TYPE", size=11, muted=True).pack(anchor="w", pady=(4, 6))
    ttk.Combobox(pages["Connection"], textvariable=mode, width=28,
                 values=("tcp", "ble", "serial"), state="readonly",
                 font=("Helvetica Neue", 14)).pack(anchor="w", pady=(0, 18))
    label(pages["Connection"], "RADIO ADDRESS", size=11, muted=True).pack(anchor="w")
    label(pages["Connection"], "TCP: hostname:4403  •  BLE: device address  •  USB: serial path", muted=True).pack(anchor="w", pady=(4, 8))
    entry = tk.Entry(pages["Connection"], textvariable=endpoint, bd=8, relief="flat",
                     font=("Helvetica Neue", 15))
    colored.append((entry, "input"))
    entry.pack(fill="x", pady=(8, 20))

    def log(message):
        output.configure(state="normal")
        output.insert("end", message.rstrip() + "\n")
        # Bound memory usage during long-running sessions with verbose bot logs.
        line_count = int(output.index("end-1c").split(".")[0])
        if line_count > 5000:
            output.delete("1.0", f"{line_count - 4000}.0")
        output.see("end")
        output.configure(state="disabled")

    def save():
        if process[0] is not None and process[0].poll() is None:
            messagebox.showwarning("Bot running", "Stop the bot before editing radio settings.")
            return
        try:
            save_radio(config, template, mode.get(), endpoint.get())
            radio_status.set("Radio settings changed • connection not verified")
            log("Radio settings saved. A backup is kept for existing configurations.")
        except (OSError, ValueError) as exc:
            messagebox.showerror("Save failed", str(exc))

    def test():
        if process[0] is not None and process[0].poll() is None:
            log("Stop the bot before testing; a radio accepts one client at a time.")
            return
        if probe_active[0]:
            log("A radio connection test is already in progress.")
            return
        transport, address = mode.get(), endpoint.get()
        probe_settings[0] = (transport, address)
        probe_active[0] = True
        radio_status.set("Testing radio connection…")
        log(f"Testing {transport} connection to {address}…")
        def worker():
            try:
                if transport == "tcp":
                    tcp_probe(address)
                summary = radio_probe.describe(radio_probe.probe_with_retry(transport, address))
                events.put(("radio", summary))
            except Exception as exc:  # radio libraries raise many error types
                events.put(("radio_error", f"Connection test failed: {type(exc).__name__}: {exc}"))
        threading.Thread(target=worker, daemon=True).start()

    def find_usb():
        try:
            ports = radio_probe.serial_ports()
        except Exception as exc:
            log(f"USB scan failed: {exc}")
            return
        if not ports:
            log("No USB radios found. Check the cable and that the radio is powered.")
            return
        mode.set("serial")
        endpoint.set(ports[0])
        log("USB devices found: " + ", ".join(ports) + f". Selected {ports[0]}.")

    actions = frame(pages["Connection"], "bg")
    actions.pack(anchor="w", pady=(12, 0))
    button(actions, "Save radio settings", save).pack(side="left", padx=(0, 10))
    button(actions, "Test connection", test).pack(side="left", padx=(0, 10))
    button(actions, "Find USB radios", find_usb).pack(side="left")

    def start():
        if closing[0] or stopping[0]:
            log("Wait for the previous bot to finish stopping before restarting.")
            return
        if process[0] is not None and process[0].poll() is None:
            return
        if probe_active[0]:
            log("Wait for the radio connection test to finish before starting the bot.")
            return
        try:
            check_paths(root_path, bot_path)
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
            events.put(("exit", (child, child.wait())))
        threading.Thread(target=reader, daemon=True).start()

    def stop(wait=False):
        child = process[0]
        if child is None or child.poll() is not None:
            return
        if stopping[0]:
            return
        stopping[0] = True
        child.terminate()
        log("Stop requested")
        def ensure_stopped():
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill()
                events.put(("log", "Bot did not stop within 5 seconds; force-stopped."))
        if wait:
            ensure_stopped()
        else:
            threading.Thread(target=ensure_stopped, daemon=True).start()

    heading(pages["Bot Controls"], "Bot controls",
            "Manage the bot process without interrupting the desktop interface")
    bot_panel = frame(pages["Bot Controls"])
    bot_panel.pack(fill="x", pady=(0, 18))
    label(bot_panel, "PROCESS STATUS", size=11, muted=True).pack(anchor="w", padx=20, pady=(18, 6))
    label(bot_panel, variable=status, size=17).pack(anchor="w", padx=20, pady=(0, 18))
    actions = frame(pages["Bot Controls"], "bg")
    actions.pack(anchor="w", pady=(8, 16))
    button(actions, "Start bot", start).pack(side="left", padx=(0, 14))
    button(actions, "Stop bot", stop).pack(side="left")
    label(pages["Bot Controls"], "Starting uses your saved radio settings. Stop the bot before testing or editing the radio.", muted=True).pack(anchor="w", pady=(4, 12))

    heading(pages["Logs"], "Live diagnostics",
            "Review recent bot output and export a copy when troubleshooting")
    output = tk.Text(pages["Logs"], state="disabled", bd=0, padx=12, pady=12,
                     font=("Menlo", 14), wrap="word")
    colored.append((output, "input"))
    output.pack(fill="both", expand=True)

    def save_logs():
        try:
            target = export_logs(Path.home() / "Documents" / "Meshing Around Logs", output.get("1.0", "end-1c"))
            log(f"Exported diagnostics to {target}")
        except OSError as exc:
            messagebox.showerror("Log export failed", str(exc))

    logs_actions = frame(pages["Logs"], "bg")
    logs_actions.pack(fill="x", pady=(10, 0))
    button(logs_actions, "Export logs", save_logs).pack(side="left", padx=(0, 12))
    def clear_logs():
        output.configure(state="normal")
        output.delete("1.0", "end")
        output.configure(state="disabled")
    button(logs_actions, "Clear visible logs", clear_logs).pack(side="left")

    heading(pages["Settings"], "Appearance",
            "Choose a color theme; your selection persists across restarts")
    label(pages["Settings"], "COLOR THEME", size=11, muted=True).pack(anchor="w", pady=(8, 8))
    ttk.Combobox(pages["Settings"], textvariable=selected_theme,
                 values=tuple(THEMES), state="readonly", width=30,
                 font=("Helvetica Neue", 14)).pack(anchor="w", pady=(0, 16))

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
                widget.configure(bg=colors["panel"], fg=colors["fg"],
                                 activebackground=colors["accent"], activeforeground=colors["bg"],
                                 highlightthickness=1, highlightbackground=colors["input"])
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
                    if "disconnect" in value.lower() or "connection lost" in value.lower():
                        last_event.set("Radio disconnected • check Logs for recovery details")
                    elif "reconnect" in value.lower() and ("success" in value.lower() or "connected" in value.lower()):
                        last_event.set("Radio reconnect reported • verify connection")
                elif kind == "close":
                    root.destroy()
                    return
                elif kind == "radio":
                    probe_active[0] = False
                    log(value)
                    if probe_settings[0] == (mode.get(), endpoint.get()):
                        radio_status.set(value)
                    else:
                        radio_status.set("Radio settings changed • test again")
                elif kind == "radio_error":
                    probe_active[0] = False
                    log(value)
                    if probe_settings[0] == (mode.get(), endpoint.get()):
                        radio_status.set(value)
                    else:
                        radio_status.set("Radio settings changed • test again")
                elif kind == "exit":
                    child, code = value
                    if process[0] is child:
                        stopping[0] = False
                        status.set(f"Stopped • exit code {code}")
                        process[0] = None
        except queue.Empty:
            pass
        root.after(100, poll)

    def close():
        if closing[0]:
            return
        closing[0] = True
        status.set("Stopping bot…")
        # Waiting on the UI thread freezes the window during slow shutdown.
        child = process[0]
        def shutdown():
            if child is not None and child.poll() is None:
                try:
                    child.terminate()
                    child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait()
                except OSError as exc:
                    events.put(("log", f"Shutdown error: {exc}"))
            events.put(("close", None))
        threading.Thread(target=shutdown, daemon=True).start()

    root.protocol("WM_DELETE_WINDOW", close)
    apply_theme()
    show("Dashboard")
    root.after(100, poll)
    root.mainloop()
