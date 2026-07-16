import os
import yt_dlp # Installed under 3.12.10 not myEnv 
import time
import random

# def download_audio(youtube_url: str, output_format="mp3"):

#     # Options for yt-dlp
#     ydl_opts = {
#         "format": "bestaudio/best",
#         "outtmpl": "%(title)s.%(ext)s",  # saves with video title
#         "postprocessors": [
#             {
#                 "key": "FFmpegExtractAudio",
#                 "preferredcodec": output_format,  # mp3, m4a, wav, etc.
#                 "preferredquality": "192",       # bitrate in kbps
#             }
#         ],
#         # Optional: suppress non-error console output
#         "quiet": False,
#         "no_warnings": True,
#     }

#     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#         print(f"Downloading audio for: {youtube_url}")
#         ydl.download([youtube_url])
        
# def download_audio(youtube_url: str, name, output_format="mp3"):
def download_audio(youtube_url: str, output_format="mp3"):
    # Options for yt-dlp
    ydl_opts = {
        "format": "bestaudio/best",
        # "outtmpl": f"{name}.%(ext)s",  # saves with video title
        "outtmpl": "%(title)s.%(ext)s",

        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": output_format,  # mp3, m4a, wav, etc.
                "preferredquality": "192",       # bitrate in kbps
            }
        ],
        # Optional: suppress non-error console output
        "quiet": False,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        print(f"Downloading audio for: {youtube_url}")
        ydl.download([youtube_url])
        
import time
import random
def generate_number():
    number = random.random() * 60 * 3 # at a random time between 0-3 minutes 
    if number < 10: 
        number = generate_number() # Try again 
    return number 

def download_videos_audio(videos):
    for title, url in videos.items():
        number = generate_number()
        print(f'Waiting {number}s')

        time.sleep(number)
        download_audio(url, title)
        

def download_video_mp4(youtube_url: str):
    ydl_opts = {
        "format": "bv*+ba/best",   # best video + best audio
        "merge_output_format": "mp4",
        "outtmpl": "%(title)s.%(ext)s",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])


if __name__ == "__main__":
    video = "C:/Users/robby/Downloads/Third_Eye_Blind_Semi-Charmed_Life/Third_Eye_Blind_Semi-Charmed_Life.mp4"
#     videos = { 
#     'Sing': "https://www.youtube.com/watch?v=tlYcUqEPN58" ,
#     'Semi-Charmed Life': "https://www.youtube.com/watch?v=uEm0ug03Mzw" ,
#     'One Night': "https://www.youtube.com/watch?v=VzSxAQWGhAM",
#     'Bad Things': "https://www.youtube.com/watch?v=QpbQ4I3Eidg", 
#     'King and Lionheart': "https://www.youtube.com/watch?v=A76a_LNIYwE", 
#     'Imaginary': "https://www.youtube.com/watch?v=dpjz5uRCXTg",
# }
    # download_videos_audio(videos) # I think this is blocked... Error code 'in trouble' 
    download_audio( "https://www.youtube.com/watch?v=AhGaVtHjIuA" )  # yt_dlp.utils.DownloadError: ERROR: unable to download video data: HTTP Error 403: Forbidden


    # download_audio("https://www.youtube.com/watch?v=tlYcUqEPN58")

    # download_video_mp4("")
    
    # download_video_mp4("https://www.youtube.com/watch?v=95vLhRfMEGU")
    # download_video_mp4("https://www.youtube.com/watch?v=1IVxUCXyJ6Q")
    # download_video_mp4("https://www.youtube.com/watch?v=KVhWxJ-fGrY")
    # download_video_mp4("https://www.youtube.com/watch?v=CDV86pJkAZs")
    # 
    # download_audio(https://www.youtube.com/watch?v=oCaOSz13h_o)

