from __future__ import annotations

import os
import queue
import sys
import threading
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image

from downloader import DownloadCancelled, Progress, download, is_youtube_url


APP_NAME = "TubeDrop"


@dataclass(frozen=True)
class Season:
    name: str
    icon: str
    accent: str
    accent_hover: str
    card: str
    panel: str
    border: str
    muted: str


SEASONS = {
    "Summer": Season("Summer", "☀", "#19c6c3", "#10aaa8", "#102b39", "#0a1f2b", "#2d7280", "#a9cdd4"),
    "Winter": Season("Winter", "❄", "#63a9ff", "#438ee9", "#0c2448", "#071a36", "#315d93", "#b8d5f5"),
    "Halloween": Season("Halloween", "◈", "#ff7a1a", "#e96300", "#231229", "#160b1b", "#65306a", "#c9a9cf"),
    "Fall": Season("Fall", "◆", "#e9862f", "#ca681d", "#32190e", "#211008", "#784325", "#dec0a2"),
    "Spring": Season("Spring", "✿", "#e46f9e", "#ca5584", "#173a3b", "#0d292a", "#4f8881", "#c4ded7"),
}


def resource_path(*parts: str) -> Path:
    root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return root.joinpath(*parts)


class TubeDrop(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        ctk.set_appearance_mode("dark")
        self.title(APP_NAME)
        self.geometry("920x680")
        self.minsize(760, 680)
        self._events: queue.Queue[tuple[str, object]] = queue.Queue()
        self._cancel = threading.Event()
        self._worker: threading.Thread | None = None
        self._resize_job: str | None = None
        self._background_source: Image.Image | None = None
        self._background_image: ctk.CTkImage | None = None

        self.url_var = ctk.StringVar()
        self.kind_var = ctk.StringVar(value="mp3")
        self.folder_var = ctk.StringVar(value=str(Path.home() / "Downloads"))
        self.status_var = ctk.StringVar(value="Ready when you are")
        self.detail_var = ctk.StringVar(value="Paste a YouTube link to get started")
        self.season_var = ctk.StringVar(value="☀  Summer")
        self.browser_var = ctk.StringVar(value="Not signed in")

        self._build_ui()
        self._apply_season("Summer")
        self.bind("<Configure>", self._queue_background_resize)
        self.after(100, self._drain_events)

    def _build_ui(self) -> None:
        self.background = ctk.CTkLabel(self, text="")
        self.background.place(x=0, y=0, relwidth=1, relheight=1)

        self.topbar = ctk.CTkFrame(self, fg_color="transparent")
        self.topbar.place(relx=0.5, y=22, anchor="n", relwidth=0.9)
        self.brand = ctk.CTkLabel(
            self.topbar, text="▶  TubeDrop", font=ctk.CTkFont("Segoe UI", 24, "bold"), text_color="#ffffff"
        )
        self.brand.pack(side="left")
        self.season_menu = ctk.CTkOptionMenu(
            self.topbar,
            variable=self.season_var,
            values=[f"{s.icon}  {s.name}" for s in SEASONS.values()],
            command=self._season_selected,
            width=154,
            height=38,
            corner_radius=19,
            font=ctk.CTkFont("Segoe UI", 13, "bold"),
            dropdown_font=ctk.CTkFont("Segoe UI", 13),
        )
        self.season_menu.pack(side="right")

        self.card = ctk.CTkFrame(self, width=610, height=590, corner_radius=30, border_width=1)
        self.card.place(relx=0.5, rely=0.55, anchor="center")
        self.card.pack_propagate(False)

        content = ctk.CTkFrame(self.card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=36, pady=31)
        self.heading = ctk.CTkLabel(content, text="Download something great", anchor="w", font=ctk.CTkFont("Segoe UI", 25, "bold"))
        self.heading.pack(fill="x")
        self.subtitle = ctk.CTkLabel(content, text="Audio or video, saved exactly where you want it.", anchor="w", font=ctk.CTkFont("Segoe UI", 13))
        self.subtitle.pack(fill="x", pady=(2, 22))

        self.link_label = self._field_label(content, "YOUTUBE LINK")
        self.link_label.pack(fill="x", pady=(0, 7))
        self.url_entry = ctk.CTkEntry(content, textvariable=self.url_var, height=46, corner_radius=14, border_width=1, placeholder_text="https://youtube.com/watch?v=…", font=ctk.CTkFont("Segoe UI", 13))
        self.url_entry.pack(fill="x")
        self.url_entry.focus_set()

        self.format_label = self._field_label(content, "CHOOSE A FORMAT")
        self.format_label.pack(fill="x", pady=(19, 7))
        self.format_switch = ctk.CTkSegmentedButton(
            content,
            values=["♫  MP3 Audio", "▣  MP4 · Up to 1080p"],
            command=lambda value: self.kind_var.set("mp3" if "MP3" in value else "mp4"),
            height=44,
            corner_radius=14,
            font=ctk.CTkFont("Segoe UI", 13, "bold"),
        )
        self.format_switch.pack(fill="x")
        self.format_switch.set("♫  MP3 Audio")

        self.folder_label = self._field_label(content, "SAVE LOCATION")
        self.folder_label.pack(fill="x", pady=(19, 7))
        folder_row = ctk.CTkFrame(content, fg_color="transparent")
        folder_row.pack(fill="x")
        self.folder_entry = ctk.CTkEntry(folder_row, textvariable=self.folder_var, height=44, corner_radius=14, border_width=1, font=ctk.CTkFont("Segoe UI", 12))
        self.folder_entry.pack(side="left", fill="x", expand=True)
        self.browse_button = ctk.CTkButton(folder_row, text="Browse", command=self._choose_folder, width=88, height=44, corner_radius=14, font=ctk.CTkFont("Segoe UI", 12, "bold"))
        self.browse_button.pack(side="left", padx=(9, 0))

        self.browser_label = self._field_label(content, "YOUTUBE SIGN-IN (OPTIONAL)")
        self.browser_label.pack(fill="x", pady=(17, 7))
        self.browser_menu = ctk.CTkOptionMenu(
            content,
            variable=self.browser_var,
            values=["Not signed in", "Chrome", "Edge"],
            height=42,
            corner_radius=14,
            font=ctk.CTkFont("Segoe UI", 12),
            dropdown_font=ctk.CTkFont("Segoe UI", 12),
        )
        self.browser_menu.pack(fill="x")

        self.progress = ctk.CTkProgressBar(content, height=8, corner_radius=4)
        self.progress.pack(fill="x", pady=(20, 0))
        self.progress.set(0)
        status_row = ctk.CTkFrame(content, fg_color="transparent")
        status_row.pack(fill="x", pady=(8, 19))
        self.status_label = ctk.CTkLabel(status_row, textvariable=self.status_var, font=ctk.CTkFont("Segoe UI", 12, "bold"))
        self.status_label.pack(side="left")
        self.detail_label = ctk.CTkLabel(status_row, textvariable=self.detail_var, font=ctk.CTkFont("Segoe UI", 11))
        self.detail_label.pack(side="right")

        self.action = ctk.CTkButton(content, text="Download now  ↓", command=self._toggle_download, height=49, corner_radius=15, font=ctk.CTkFont("Segoe UI", 14, "bold"))
        self.action.pack(fill="x")

    @staticmethod
    def _field_label(parent: ctk.CTkFrame, text: str) -> ctk.CTkLabel:
        return ctk.CTkLabel(parent, text=text, anchor="w", height=15, font=ctk.CTkFont("Segoe UI", 10, "bold"))

    def _season_selected(self, selected: str) -> None:
        self._apply_season(selected.split()[-1])

    def _apply_season(self, name: str) -> None:
        season = SEASONS[name]
        self.season_var.set(f"{season.icon}  {season.name}")
        self._background_source = Image.open(resource_path("assets", "seasons", f"{name.lower()}.png")).convert("RGB")
        self.card.configure(fg_color=season.card, border_color=season.border)
        self.season_menu.configure(fg_color=season.card, button_color=season.accent, button_hover_color=season.accent_hover, dropdown_fg_color=season.card, dropdown_hover_color=season.panel)
        self.subtitle.configure(text_color=season.muted)
        for label in (self.link_label, self.format_label, self.folder_label, self.browser_label, self.detail_label):
            label.configure(text_color=season.muted)
        for entry in (self.url_entry, self.folder_entry):
            entry.configure(fg_color=season.panel, border_color=season.border)
        self.format_switch.configure(
            fg_color=season.panel,
            unselected_color=season.panel,
            unselected_hover_color=season.border,
            selected_color=season.accent,
            selected_hover_color=season.accent_hover,
        )
        self.browse_button.configure(fg_color=season.panel, hover_color=season.border, border_width=1, border_color=season.border)
        self.browser_menu.configure(
            fg_color=season.panel,
            button_color=season.border,
            button_hover_color=season.accent_hover,
            dropdown_fg_color=season.card,
            dropdown_hover_color=season.panel,
        )
        self.progress.configure(progress_color=season.accent, fg_color=season.panel)
        self.action.configure(fg_color=season.accent, hover_color=season.accent_hover)
        self._resize_background()

    def _queue_background_resize(self, event: object = None) -> None:
        if self._resize_job:
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(80, self._resize_background)

    def _resize_background(self) -> None:
        self._resize_job = None
        if not self._background_source:
            return
        width, height = max(1, self.winfo_width()), max(1, self.winfo_height())
        source = self._background_source
        scale = max(width / source.width, height / source.height)
        resized = source.resize((round(source.width * scale), round(source.height * scale)), Image.Resampling.LANCZOS)
        left = max(0, (resized.width - width) // 2)
        top = max(0, (resized.height - height) // 2)
        cropped = resized.crop((left, top, left + width, top + height))
        self._background_image = ctk.CTkImage(light_image=cropped, dark_image=cropped, size=(width, height))
        self.background.configure(image=self._background_image)

    def _choose_folder(self) -> None:
        chosen = filedialog.askdirectory(initialdir=self.folder_var.get(), title="Choose download folder")
        if chosen:
            self.folder_var.set(chosen)

    def _toggle_download(self) -> None:
        if self._worker and self._worker.is_alive():
            self._cancel.set()
            self.action.configure(state="disabled", text="Cancelling…")
            return
        url = self.url_var.get().strip()
        if not is_youtube_url(url):
            messagebox.showerror(APP_NAME, "Paste a valid YouTube video, Short, or live-video link.")
            return
        folder = Path(self.folder_var.get()).expanduser()
        try:
            folder.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            messagebox.showerror(APP_NAME, f"That save folder cannot be used.\n\n{exc}")
            return
        self._cancel.clear()
        self._set_busy(True)
        browser = self.browser_var.get().lower() if self.browser_var.get() != "Not signed in" else None
        self._worker = threading.Thread(
            target=self._run_download,
            args=(url, self.kind_var.get(), folder, browser),
            daemon=True,
        )
        self._worker.start()

    def _run_download(self, url: str, kind: str, folder: Path, browser: str | None) -> None:
        try:
            download(
                url,
                kind,  # type: ignore[arg-type]
                folder,
                lambda p: self._events.put(("progress", p)),
                self._cancel.is_set,
                browser,  # type: ignore[arg-type]
            )
            self._events.put(("success", folder))
        except DownloadCancelled:
            self._events.put(("cancelled", None))
        except Exception as exc:
            self._events.put(("error", str(exc)))

    def _drain_events(self) -> None:
        try:
            while True:
                event, payload = self._events.get_nowait()
                if event == "progress":
                    self._show_progress(payload)  # type: ignore[arg-type]
                elif event == "success":
                    self._set_busy(False)
                    self.status_var.set("Download complete")
                    self.detail_var.set("Saved successfully")
                    if messagebox.askyesno(APP_NAME, "Download complete. Open the destination folder?"):
                        os.startfile(payload)  # type: ignore[arg-type,attr-defined]
                elif event == "cancelled":
                    self._set_busy(False)
                    self.status_var.set("Cancelled")
                    self.detail_var.set("The download was stopped")
                elif event == "error":
                    self._set_busy(False)
                    self.status_var.set("Couldn’t download")
                    self.detail_var.set("Check the link and connection")
                    messagebox.showerror(APP_NAME, f"The download failed.\n\n{payload}")
        except queue.Empty:
            pass
        self.after(100, self._drain_events)

    def _show_progress(self, progress: Progress) -> None:
        self.status_var.set(progress.status)
        self.detail_var.set(progress.detail)
        if progress.percent is None:
            self.progress.configure(mode="indeterminate")
            self.progress.start()
        else:
            self.progress.stop()
            self.progress.configure(mode="determinate")
            self.progress.set(max(0, min(1, progress.percent / 100)))

    def _set_busy(self, busy: bool) -> None:
        state = "disabled" if busy else "normal"
        self.url_entry.configure(state=state)
        self.folder_entry.configure(state=state)
        self.format_switch.configure(state=state)
        self.browse_button.configure(state=state)
        self.browser_menu.configure(state=state)
        self.season_menu.configure(state=state)
        self.action.configure(state="normal", text="Cancel download" if busy else "Download now  ↓")
        if not busy:
            self.progress.stop()


if __name__ == "__main__":
    TubeDrop().mainloop()
