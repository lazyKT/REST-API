import os
import youtube_dl

"""
 : This is a helper function for the app.task(url)
 : The conversion of the Youtube Video to MP3 with the help of youtube_dl
 : Upon Successful Conversion, the mp3 files will be saved as youtube video id name (watch?v=video_ID) under static/audios
"""
def convert_mp3(url):
    dl_path = os.path.join('static','audios') # destination folder
    audio_name = url.split('=')[1]  # geting youtube video id from url
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
    except Exception as e:
        print(e)