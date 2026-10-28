"""First desktop foundation for Meshing Around. Original bot remains unchanged."""
from __future__ import annotations
import pathlib
import queue
import socket
import subprocess
import sys
import threading
from radio_config import read_radio, save_radio

ROOT = pathlib.Path(__file__).resolve().parent.parent
BOT = ROOT / "mesh_bot.py"

def check_tcp(host: str, port: int = 4403) -> bool:
    """TCP reachability only; not a Meshtastic protocol handshake."""
    if not host.strip() or not 1 <= port <= 65535:
        raise ValueError("Invalid TCP hostname or port")
    with socket.create_connection((host.strip(), port), timeout=4):
        return True

def main() -> None:
    if not BOT.is_file():
        raise FileNotFoundError(BOT)
    if "--check" in sys.argv:
        print("DESKTOP_FOUNDATION_OK")
        return
    import tkinter as tk
    from tkinter import ttk, messagebox
    root = tk.Tk()
    root.title("Meshing Around • Desktop")
    root.geometry("850x600")
    config_path = ROOT / "config.ini"
    template_path = ROOT / "config.template"
    initial_mode, initial_endpoint = read_radio(config_path if config_path.exists() else template_path)
    mode = tk.StringVar(value=initial_mode)
    host = tk.StringVar(value=initial_endpoint or "meshtastic.local")
    status = tk.StringVar(value="Bot stopped")
    events = queue.Queue()
    process = [None]
    frame = ttk.Frame(root, padding=20)
    frame.pack(fill="both", expand=True)
    ttk.Label(frame, text="MESHING AROUND", font=("Helvetica", 22, "bold")).pack(anchor="w")
    ttk.Label(frame, textvariable=status).pack(anchor="w", pady=10)
    ttk.Combobox(frame, textvariable=mode, values=("tcp", "ble", "serial"), state="readonly").pack(anchor="w")
    ttk.Entry(frame, textvariable=host).pack(fill="x")
    output = tk.Text(frame, height=20, bg="#192637", fg="#e5edf7", state="disabled")
    output.pack(fill="both", expand=True, pady=12)
    def log(line):
        output.configure(state="normal")
        output.insert("end", line.rstrip() + "\n")
        output.see("end")
        output.configure(state="disabled")
    def save():
        if process[0] is not None and process[0].poll() is None:
            messagebox.showwarning("Stop bot", "Stop bot before saving radio settings")
            return
        try:
            save_radio(config_path, template_path, mode.get(), host.get())
            log("Radio configuration saved")
        except (OSError, ValueError) as exc:
            messagebox.showerror("Save failed", str(exc))
    def test():
        if mode.get() != "tcp":
            log("TCP test only applies to TCP mode")
            return
        address = host.get()
        def worker():
            try:
                check_tcp(address)
                events.put(("log", "TCP reachable (radio protocol unverified)"))
            except (OSError, ValueError) as exc:
                events.put(("log", f"TCP test failed: {exc}"))
        threading.Thread(target=worker, daemon=True).start()
    def start():
        if process[0] is not None and process[0].poll() is None:
            return
        try:
            p = subprocess.Popen([sys.executable, "-u", str(BOT)], cwd=ROOT,
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 text=True, bufsize=1)
        except OSError as exc:
            messagebox.showerror("Launch failed", str(exc))
            return
        process[0] = p
        status.set("Bot running • radio connection unverified")
        log("Using existing bot configuration; hostname above is TCP test only.")
        def reader():
            for line in p.stdout:
                events.put(("log", line))
            events.put(("exit", str(p.wait())))
        threading.Thread(target=reader, daemon=True).start()
    def stop():
        if process[0] is not None and process[0].poll() is None:
            process[0].terminate()
    buttons = ttk.Frame(frame)
    buttons.pack(fill="x")
    for label, callback in (("Test TCP", test), ("Save radio", save), ("Start bot", start), ("Stop bot", stop)):
        ttk.Button(buttons, text=label, command=callback).pack(side="left", padx=4)
    def poll():
        try:
            while True:
                kind, value = events.get_nowait()
                if kind == "log":
                    log(value)
                else:
                    status.set(f"Bot exited ({value})")
                    process[0] = None
        except queue.Empty:
            pass
        root.after(100, poll)
    def close():
        stop()
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", close)
    root.after(100, poll)
    root.mainloop()

if __name__ == "__main__":
    main()
