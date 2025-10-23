import io
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from youtube_downloader.youtube_service import get_streams, download_stream
from PIL import Image, ImageTk
import tkinter.font as tkFont
import urllib.request
from tkinter import filedialog


class YoutubeDownloaderApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("YouTube Video Downloader")
        self.window.geometry("800x820")

        # URL input
        tk.Label(self.window, text="YouTube URL:").pack(pady=5)
        self.url_entry = tk.Entry(self.window, width=50)
        self.url_entry.pack()

        # fetch button
        self.fetch_button = tk.Button(self.window, text="Fetch Resolutions", command=self.fetch_video_threaded)
        self.fetch_button.pack(pady=5)

        # title label
        self.title_font = tkFont.Font(family="Times New Roman", size=20)
        self.title_label = tk.Label(self.window, font=self.title_font)
        self.title_label.pack(pady=5)

        # Thumbnail display
        self.thumbnail_label = tk.Label(self.window)
        self.thumbnail_label.pack(pady=10)

        # Resolution dropdown
        self.resolution_var = tk.StringVar()
        self.resolution_menu = ttk.Combobox(self.window, textvariable=self.resolution_var, state="readonly")
        self.resolution_menu.pack(pady=5)

        # Download button
        self.download_button = tk.Button(self.window, text="Download", command=self.download_video_threaded)
        self.download_button.pack(pady=10, padx=10)

        # Progress bar
        self.progress_bar = ttk.Progressbar(self.window, orient="horizontal", mode="determinate", length=300)
        self.progress_bar.pack(pady=10)

        # Status label
        self.status_label = ttk.Label(self.window, text="Status: Ready")
        self.status_label.pack(pady=5)

        self.streams = []

    def fetch_video_threaded(self):
        """Run fetch_resolutions in a thread"""
        self.fetch_button.config(state='disabled')
        self.status_label.config(text="Fetching resolutions...")
        threading.Thread(target=self.fetch_video, daemon=True).start()

    def fetch_video(self):
        url = self.url_entry.get()
        try:
            self.streams, thumbnail_url, title = get_streams(url)
            res_and_size = [f"{res} - {size / 1024 / 1024:.2f} MB - {int(duration / 60)}:{duration % 60}" if size > 0 else res
                            for res, _, size, duration in self.streams]

            # Update UI from main thread
            self.window.after(0, self.update_title, title)
            self.window.after(0, self.load_thumbnail, thumbnail_url)
            self.window.after(0, self.update_video_info, res_and_size)

        except Exception as e:
            self.window.after(0, messagebox.showerror, "Error", f"Failed to fetch video resolutions:\n{e}")
            self.window.after(0, self.fetch_button.config, {'state': 'normal'})

    def update_title(self, title):
        self.title_label.config(text=title)

    def update_video_info(self, res_and_size):
        """Update UI with resolutions (called on main thread)"""
        self.resolution_menu.config(values=res_and_size)
        if res_and_size:
            self.resolution_menu.current(0)

        self.status_label.config(text=f"Found {len(res_and_size)} resolutions")
        self.fetch_button.config(state='normal')

    def download_video_threaded(self):
        """Run download_video in a thread"""

        # Get the download path
        download_path = filedialog.askdirectory()
        if not download_path:
            messagebox.showerror("Error", "No directory selected")
            return
        self.download_button.config(state='disabled')
        self.progress_bar['value'] = 0
        threading.Thread(target=self.download_video, args=(download_path, ), daemon=True).start()

    def download_video(self, download_path):
        selection = self.resolution_var.get()
        url = self.url_entry.get()

        if not selection:
            self.window.after(0, messagebox.showwarning, "Warning", "Please select a resolution")
            self.window.after(0, self.download_button.config, {'state': 'normal'})
            return

        try:
            for res, format_id, filesize, duration in self.streams:
                if (f"{res} - {filesize / 1024 / 1024:.2f} MB - {int(duration / 60)}:{duration % 60}" if filesize > 0 else res) == selection:
                    download_stream((res, format_id, filesize), url, output_path=download_path, progress_hook=self.on_progress)
                    self.window.after(0, messagebox.showinfo, "Success", "Video Downloaded Successfully!")
                    self.window.after(0, self.download_button.config, {'state': 'normal'})
                    return
        except Exception as e:
            self.window.after(0, messagebox.showerror, "Error", f"Download failed:\n{e}")
            self.window.after(0, self.download_button.config, {'state': 'normal'})

    def load_thumbnail(self, thumbnail_url):
        """Load and display thumbnail image"""

        try:
            with urllib.request.urlopen(thumbnail_url) as response:
                raw_data = response.read()

            image = Image.open(io.BytesIO(raw_data))
            image = image.resize((600, 450))
            image = ImageTk.PhotoImage(image)
            self.thumbnail_label.configure(image=image)
            self.thumbnail_label.image = image
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load thumbnail:\n{e}")


    def on_progress(self, d):
        """Progress hook called by yt-dlp (runs in download thread)"""
        if d['status'] == 'downloading':
            if 'total_bytes' in d:
                total = d['total_bytes']
            elif 'total_bytes_estimate' in d:
                total = d['total_bytes_estimate']
            else:
                return

            downloaded = d.get('downloaded_bytes', 0)
            percentage = (downloaded / total) * 100

            eta = d.get('eta', 0)
            elapsed = d.get('elapsed', 0)
            speed = d.get('speed', 0)

            if speed:
                speed = speed / 1024 / 1024
            else:
                speed = 0

            if not eta:
                eta = 0

            # Schedule UI update on main thread
            self.window.after(0, self.update_progress, percentage, total, downloaded, eta, elapsed, speed)

    def update_progress(self, percentage, total, downloaded, eta, elapsed, speed):
        """Update progress bar (called on main thread)"""
        self.progress_bar.config(value=percentage)
        downloaded_mb = downloaded / 1024 ** 2
        total_mb = total / 1024 ** 2
        self.status_label.config(text=f"Downloading: {percentage:.1f}% ({downloaded_mb:.1f}/{total_mb:.1f} MiB) Speed:{speed:.2f}Mbps/sec \nElapsed Time:{elapsed:.1f}s (ETA: {eta:.1f}s)")
        self.window.update_idletasks()

    def run(self):
        self.window.mainloop()