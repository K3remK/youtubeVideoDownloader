import yt_dlp
import urllib.parse


def get_streams(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        thumbnail_url = info.get('thumbnail')
        title = info.get('title')
        formats = info.get('formats', [])
        streams = []

        for f in formats:
            if f.get('vcodec') != 'none' and f.get('height') and f.get('acodec') != 'none':
                filesize, duration = extract_video_size_and_duration_from_url(f.get('url'))
                resolution = f"{f.get('height')}p"
                if not filesize:
                    filesize = f.get("filesize") or f.get("filesize_approx") or 0
                streams.append((resolution, f['format_id'], filesize or 0, duration))

        # Sort by resolution (descending)
        streams.sort(key=lambda x: int(x[0].replace('p', '')), reverse=False)
        return streams, thumbnail_url, title

def extract_video_size_and_duration_from_url(url):
    decoded = urllib.parse.unquote(url)

    size_info = list(filter(lambda x: 'clen' in x, decoded.split('/')))

    if len(size_info) < 2:
        return 0, 0

    total_size = 0
    duration = size_info[0].split(';')[1].split('=')[1]
    for info in size_info:
        total_size += int(info.split(';')[0].split('=')[1])

    return total_size, int(float(duration))


def download_stream(selected_tuple, url, output_path='.', filename=None, progress_hook=None):
    """
    Download a stream from the tuple returned by get_streams

    Args:
        selected_tuple: A tuple of (resolution, format_id, filesize) from get_streams
        url: The video URL
        output_path: Directory to save the file
        filename: Optional custom filename
        progress_hook:
    """
    resolution, format_id, filesize = selected_tuple

    ydl_opts = {
        'format': format_id,
        'outtmpl': f'{output_path}/{filename}' if filename else f'{output_path}/%(title)s.%(ext)s',
        'progress_hooks': [progress_hook],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])