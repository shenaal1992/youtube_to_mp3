from flask import Flask, render_template, request, send_file
import yt_dlp
import os

app = Flask(__name__)

# Define constants for file storage
UPLOAD_FOLDER = 'uploads'
COOKIES_FILE = os.path.join(UPLOAD_FOLDER, 'cookies.json')
OUTPUT_AUDIO_PATH = os.path.join(UPLOAD_FOLDER, 'downloaded_audio.mp3')

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_cookies_from_browser(output_cookies_file, browser_name='chrome'):
    """
    Extract cookies from the browser and save to a JSON file.
    """
    ydl_opts = {
        'cookiesfrombrowser': browser_name,
        'cookiefile': output_cookies_file,
        'quiet': False,  # Verbose for debugging
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info('https://www.youtube.com', download=False)
        print(f"Cookies successfully saved to: {output_cookies_file}")
    except Exception as e:
        print(f"Error extracting cookies from {browser_name}: {e}")
        raise


def download_mp3(video_url, output_audio_path, cookies_file):
    """
    Download audio from YouTube using yt-dlp and provided cookies.
    """
    # Ensure the cookies file exists
    if not os.path.isfile(cookies_file):
        return f"Cookies file '{cookies_file}' not found."

    # yt-dlp options
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': output_audio_path,
        'cookiefile': cookies_file,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'noplaylist': True,
        'quiet': True,
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

    # Extract cookies if not already available
    if not os.path.isfile(COOKIES_FILE):
        try:
            get_cookies_from_browser(COOKIES_FILE)
        except Exception as e:
            return f"Error extracting cookies: {e}"

    # Download the video as MP3
    error = download_mp3(video_url, OUTPUT_AUDIO_PATH, COOKIES_FILE)

    # Remove cookies file only if it exists
    if os.path.isfile(COOKIES_FILE):
        os.remove(COOKIES_FILE)

    # If download was successful, send the file to the user
    if error is None:
        try:
            return send_file(OUTPUT_AUDIO_PATH, as_attachment=True)
        finally:
            if os.path.isfile(OUTPUT_AUDIO_PATH):
                os.remove(OUTPUT_AUDIO_PATH)
    else:
        return f"Error: {error}"


if __name__ == '__main__':
    app.run(debug=True)