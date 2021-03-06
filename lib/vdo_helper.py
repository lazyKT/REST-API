import os
import youtube_dl


# url_helper function helps to validate the url and remove the playlist information from url
# : for example, if a user request a song from youtube playlist, only the song requested will be processed,
# : removing playlist id from url. This is being done because of Youtube-dl feature.
# : Youtube-dl converts all the songs from playlist if the url contain playlist id
def url_helper(url):
    if 'youtube.com' in url and '?v=' in url:
        # avoid youtube playlist url and take only a single song
        return url.split('&')[0]
    return None

"""
 : This is a helper function for the app.task(url)
 : The conversion of the Youtube Video to MP3 with the help of youtube_dl
 : Upon Successful Conversion, the mp3 files will be saved as youtube video id name (watch?v=video_ID) under static/audios
"""
def convert_mp3(url):
    # If url is invalid, raise an exception
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
        raise Exception(e)


"""
: This is a helper function for the '/listen/<song>' route.
: This function simply returns the audio file(mp3) which matches the <song> in url.
: Before returning anything, the function checks the existence of the audio file in targeted folder.
"""
def find_file(file):
    print(file)
    folder = "audios"
    target_folder = os.path.join("static", folder)
    mp3_path = os.path.join(target_folder, f"{file}.mp3")
    # !!! Check mp3 file path is valid and does exist, return the path of mp3 file
    if os.path.isfile(mp3_path):
        return mp3_path
    return None