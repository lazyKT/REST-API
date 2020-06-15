import os
import youtube_dl


def convert_mp3(url):
    dl_path = os.path.join('static','audios')
    audio_name = url.split('=')[1]  # youtube video id
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': dl_path+'/'+audio_name+'.%(ext)s',
        'postprocessors': [{
            'key' : 'FFmpegExtractAudio',
            'preferredcodec' : 'mp3',
            'preferredquality' : '320'
        }]
    }
    try:
        with  youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except:
        pass