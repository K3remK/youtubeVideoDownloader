import ffmpeg.audio
from pytubefix import YouTube
from pytubefix.cli import on_progress
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os
import urllib.request
import io
from PIL import ImageTk, Image 
from pytubefix import Stream

class WebImage:
    def __init__(self, url):
        with urllib.request.urlopen(url) as u:
            raw_data = u.read()
        image = Image.open(io.BytesIO(raw_data))
        self.image = ImageTk.PhotoImage(image=image)

    def get(self):
        return self.image

class VideoTechInfo:
    def __init__(self, subtype, resolution, size):
        self.subtype = subtype
        self.resolution = resolution
        self.size = size

    def __repr__(self):
        return f"(Type: {self.subtype}, Res: {self.resolution}, Size: {self.size} mb)"

    def __str__(self):
        return f"Type: {self.subtype}, Res: {self.resolution}, Size: {self.size} mb"

class Video:
    def __init__(self, url):
        try:
            yt = YouTube(url, on_progress_callback=on_progress)
            self.url = url
            self.title = yt.title
            self.thumbnail_img = WebImage(yt.thumbnail_url).get()
            self.duration = [yt.length // 60, yt.length % 60]
            self.techInfos = list()
            for stream in yt.streams.filter(adaptive=True, only_video=True).order_by('resolution').desc():
                self.techInfos.append(VideoTechInfo(stream.subtype,
                                                    stream.resolution,
                                                    stream.filesize_mb))
        except Exception as e:
            raise Exception("Invalid URL!")
    def get_video(self, videoTechInfo : VideoTechInfo):
        yt = YouTube(self.url, on_progress_callback=on_progress)
        return yt.streams.filter(adaptive=True, only_video=True,
                                   file_extension=videoTechInfo.subtype,
                                   res=videoTechInfo.resolution).first()
        
    def get_audio(self, videoTechInfo: VideoTechInfo):
        yt = YouTube(self.url, on_progress_callback=on_progress)
        return yt.streams.filter(adaptive=True, only_audio=True, subtype=videoTechInfo.subtype).first()

def download_video(video_stream):
    save_path = open_file_dialog()
    if save_path:
        video_stream.download(save_path)
        return save_path
    else:
        raise Exception("Please select a location!")

def to_windows_path(path : str):
    path.replace('/', '\\')

def download_audio(audio_stream : Stream, save_path):
    audio_stream.download(output_path=save_path)

def combine_video_and_audio(save_path : str, video_name : str, audio_name : str):
    #print(f'ffmpeg -i "{video_path}" -i "{audio_path}" -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 "{video_path}"')
    os.system(f'ffmpeg -i {save_path + '/"' + video_name + '"'} -i {save_path + '/"' + audio_name + '"'} -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 {save_path + '/"Combined ' + video_name}"')
    os.remove(save_path + '/' + video_name)
    os.remove(save_path + '/' + audio_name)

def open_file_dialog():
    folder = filedialog.askdirectory()
    return folder

def handle_download_button(video_stream : Stream, audio_stream: Stream):
    save_path = download_video(video_stream)
    if save_path:
        download_audio(audio_stream, save_path)

    video_name = video_stream.title + '.' + video_stream.subtype
    audio_name = audio_stream.title + '.' + audio_stream.subtype

    combine_video_and_audio(save_path=save_path, video_name=video_name, audio_name=audio_name)


if __name__ == "__main__": # all the staff below will run if we directly run this python file
    root = tk.Tk()

    def get_video():
        if video_url.get():
            try:
                video = Video(video_url.get())

                img = video.thumbnail_img
                imageLab = tk.Label(root, image=img)
                imageLab.grid(row=1, column=1)

                title = tk.Label(root, text=video.title, font="Arial 20")
                title.grid(row=2, column=1)

                combobox = ttk.Combobox(root, width=100, values=video.techInfos)
                combobox.set(video.techInfos[0])
                combobox.grid(row=3, column=1, columnspan=1)

                downloadBT = tk.Button(root, text="Download", command= lambda: handle_download_button(video.get_video(video.techInfos[combobox.current()]), 
                                                                                                      video.get_audio(video.techInfos[combobox.current()])))
                downloadBT.grid(row=3, column=2)
            except Exception as e:
                tk.messagebox.showerror(title="Error", message=e)
            root.mainloop()
                    

    tk.Label(root, text="URL:").grid(row=0, column=0)
    video_url = tk.Entry(root, width=100)
    video_url.grid(row=0, column=1)
    button = tk.Button(root, text="Get Video", command=get_video)
    button.grid(row=0, column=2)

    root.mainloop()

    #video_url2 = "https://www.youtube.com/watch?v=74FJ8TTMM5E&ab_channel=GreenCode"
    #video_stream = YouTube(video_url2).streams.filter(adaptive=True, only_video=True, file_extension='mp4').order_by('resolution').desc().first()
    #audio_streams = YouTube(video_url2).streams.filter(adaptive=True, only_audio=True, subtype='mp4').first()
#
    #video_stream.download()
    #audio_streams.download()
    #print(video_stream)
    #print(audio_streams)