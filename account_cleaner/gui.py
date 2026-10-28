"""Small tkinter window for double-click use (no console needed)."""

from __future__ import annotations

import os
import queue
import sys
import threading
from typing import Callable

from . import __version__
from .backends import RegistryError, WinRegistryBackend
from .backups import default_backup_dir
from .core import clean, restore


def main() -> int:
    import tkinter as tk
    from tkinter import messagebox, ttk

    try:
        backend = WinRegistryBackend()
    except RegistryError as exc:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Account Record Cleaner", str(exc))
        return 2

    root = tk.Tk()
    root.title(f"Account Record Cleaner {__version__}")
    root.geometry("560x400")
    root.minsize(460, 320)

    kill_var = tk.BooleanVar(value=True)
    backup_var = tk.BooleanVar(value=True)
    events: "queue.Queue[tuple[str, str]]" = queue.Queue()
    busy = {"on": False}

    frame = ttk.Frame(root, padding=12)
    frame.pack(fill="both", expand=True)

    ttk.Label(
        frame,
        text="Removes the local 'expired account' record of the Windscribe client.",
        wraplength=520,
    ).pack(anchor="w")
    opts = ttk.Frame(frame)
    opts.pack(anchor="w", pady=(8, 4))
    ttk.Checkbutton(opts, text="Close Windscribe first", variable=kill_var).pack(anchor="w")
    ttk.Checkbutton(opts, text="Create a .reg backup before deleting", variable=backup_var).pack(anchor="w")

    buttons = ttk.Frame(frame)
    buttons.pack(anchor="w", pady=6)

    text = tk.Text(frame, height=10, wrap="word", state="disabled", font=("Consolas", 9))
    scroll = ttk.Scrollbar(frame, command=text.yview)
    text.configure(yscrollcommand=scroll.set)
    scroll.pack(side="right", fill="y")
    text.pack(fill="both", expand=True)
    for tag, color in (("ok", "#1a7f37"), ("warn", "#9a6700"), ("error", "#cf222e")):
        text.tag_configure(tag, foreground=color)

    def append(level: str, message: str) -> None:
        text.configure(state="normal")
        text.insert("end", message + "\n", level)
        text.see("end")
        text.configure(state="disabled")

    def pump() -> None:
        try:
            while True:
                append(*events.get_nowait())
        except queue.Empty:
            pass
        root.after(100, pump)

    def log(level: str, message: str) -> None:  # called from the worker thread
        events.put((level, message))

    def run(job: Callable[[], int], title: str) -> None:
        if busy["on"]:
            return
        busy["on"] = True
        for b in all_buttons:
            b.state(["disabled"])

        def worker() -> None:
            try:
                code = job()
            except Exception as exc:  # never leave the UI stuck
                log("error", f"Unexpected error: {exc}")
                code = 1
            events.put(("ok" if code == 0 else "error", f"{title}: finished ({'success' if code == 0 else 'failed'})"))
            root.after(0, done)

        def done() -> None:
            busy["on"] = False
            for b in all_buttons:
                b.state(["!disabled"])

        threading.Thread(target=worker, daemon=True).start()

    def on_clean() -> None:
        if not messagebox.askyesno(
            "Confirm", "Delete the local account record now?"
            + ("\nA backup will be created first." if backup_var.get() else "\nNo backup will be created!")
        ):
            return
        run(lambda: clean(backend, backup=backup_var.get(), kill_client=kill_var.get(), log=log), "Clean")

    def on_restore() -> None:
        if not messagebox.askyesno("Confirm", "Restore the newest backup?"):
            return
        run(lambda: restore(backend, log=log), "Restore")

    def on_open() -> None:
        folder = default_backup_dir()
        if sys.platform == "win32":
            os.startfile(str(folder))  # type: ignore[attr-defined]

    b_clean = ttk.Button(buttons, text="Clear account record", command=on_clean)
    b_restore = ttk.Button(buttons, text="Restore latest backup", command=on_restore)
    b_open = ttk.Button(buttons, text="Open backups folder", command=on_open)
    all_buttons = [b_clean, b_restore, b_open]
    for b in all_buttons:
        b.pack(side="left", padx=(0, 6))

    append("info", "Local cleanup only - server-side state is not changed.")
    pump()
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
