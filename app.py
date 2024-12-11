from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import json
import shutil

app = Flask(__name__)

def get_cookies_from_browser(output_cookies_file):
    """
    Extract cookies from the browser and save them to a JSON file for use in yt-dlp.
    """
    ydl_opts = {
        'extractor_args': {
            'youtube': ['cookies_from_browser'],  # Extract cookies
        },
        'cookiefile': output_cookies_file,  # Save cookies to file
        'quiet': True,  # Hide progress
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info('https://www.youtube.com', download=False)  # Extract cookies
        print(f"Cookies saved to: {output_cookies_file}")
    except Exception as e:
        print(f"Error extracting cookies: {e}")

def download_mp3(video_url, output_audio_path, cookies_file):
    """
    Download audio from YouTube using yt-dlp, using cookies for authentication.
    """
    if not os.path.isfile(cookies_file):
        return f"Cookies file '{cookies_file}' not found."

    # Ensure output directory exists
    output_dir = os.path.dirname(output_audio_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # yt-dlp options
    ydl_opts = {
        'format': 'bestaudio/best',  # Download best available audio
        'outtmpl': output_audio_path,  # Output file path template
        'cookies': cookies_file,  # Use cookies for authentication
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',  # Mimic browser
        'noplaylist': True,  # Ensure only the single video is downloaded
        'quiet': True,  # Hide progress
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        return None  # Success
    except yt_dlp.utils.DownloadError as e:
        return f"Download error: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    video_url = request.form['url']
    cookies_file = 'cookies.json'
    output_audio_path = 'downloaded_audio.mp3'

    # Extract cookies if not already available
    if not os.path.isfile(cookies_file):
        get_cookies_from_browser(cookies_file)

    # Download the video as MP3
    error = download_mp3(video_url, output_audio_path, cookies_file)
    
    # Remove the cookies file after the download
    if os.path.isfile(cookies_file):
        os.remove(cookies_file)

    # If download was successful, send the file to the user
    if error is None:
        return send_file(output_audio_path, as_attachment=True)
    else:
        return f"Error: {error}"

if __name__ == '__main__':
    app.run(debug=True, port=5001)