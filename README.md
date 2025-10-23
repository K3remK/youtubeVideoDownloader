# YouTube Downloader GUI

A simple **Tkinter GUI application** that allows users to download YouTube videos. Users can enter a YouTube video URL, select a specific resolution, and download the video using **`yt_dlp`**.

---

<h2>🧐 Features</h2>

* Easy-to-use Tkinter GUI
* Enter YouTube video URL
* Select desired video resolution
* Download videos using `yt_dlp`
* Cross-platform (Windows, macOS, Linux)
* Modern Python packaging with `pyproject.toml` and console script

---

## Project Structure

📦 YoutubeVideoDownloader/\
├── 📄 pyproject.toml\
├── 📂 youtube_downloader/\
├── 📄 .gitignore\
│   ├── 📄 __init__.py\
│   ├── 📄 main.py\
│   ├── 📄 gui.py\
│   └── 📄 youtube_service.py\
├── 📂 venv/ # optional, ignored by git\
└── 📄 README.md

---

## Installation

1. **Clone the repository**

```bash
git clone https://github.com/K3remK/youtubeVideoDownloader.git
cd YoutubeVideoDownloader
```

2. **Create a virtual environment**
```bash
python -m venv venv
```
3. **Activate it:**
````bash
# windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
````
4. **Install the package in editable mode**\
This will also install all required dependencies (yt_dlp, tkinter, etc.) automatically.
````bash
pip install -e .
````

## Usage
After installation, run the program from anywhere:
```bash
youtube-downloader
```
This will launch the Tkinter GUI where you can:
* Enter a YouTube video URL
* Select a desired resolution
* Download the video to your computer

## Deployment
* Modify code under `src/youtube_downloader/`
* The console script reflects changes immediately because of editable install `(-e)`