from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import json
import shutil

app = Flask(__name__)




def get_cookies_from_browser(output_cookies_file, browser_name='chrome'):
    """
    Extract cookies from the browser and save them to a file for use in yt-dlp.

    Args:
        output_cookies_file (str): The path to save the cookies file.
        browser_name (str): The name of the browser to extract cookies from. Default is 'chrome'.
    """
    ydl_opts = {
        'cookiesfrombrowser': browser_name,  # Extract cookies from the specified browser
        'cookiefile': output_cookies_file,  # Save cookies to this file
        'quiet': True,  # Suppress yt-dlp progress messages
    }

    try:
        # Extract cookies using yt-dlp and save to the file
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info('https://www.youtube.com', download=False)
        print(f"Cookies successfully saved to: {output_cookies_file}")
    except Exception as e:
        print(f"Error extracting cookies from {browser_name}: {e}")
        

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
    UPLOAD_FOLDER = 'uploads'  # Folder to store uploaded files
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure folder exists
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    video_url = request.form.get('url')
    if not video_url:
        return "Error: No video URL provided.", 400

    # Specify paths for cookies file and output audio
    cookies_file = os.path.join(app.config['UPLOAD_FOLDER'], 'cookies.json')
    output_audio_path = os.path.join(app.config['UPLOAD_FOLDER'], 'downloaded_audio.mp3')

    # Save cookies.json if provided in the request
    cookies_data = request.form.get('cookies')  # Expecting cookies data as a JSON string
    if cookies_data:
        try:
            cookies = json.loads(cookies_data)  # Parse JSON data
            with open(cookies_file, 'w') as f:
                json.dump(cookies, f, indent=4)  # Save to cookies.json
        except json.JSONDecodeError:
            return "Error: Invalid JSON data for cookies.", 400
    else:
        # Generate cookies dynamically if not provided
        if not os.path.isfile(cookies_file):
            get_cookies_from_browser(cookies_file)  # Make sure this writes to cookies_file

    # Try to download the video as MP3
    try:
        error = download_mp3(video_url, output_audio_path, cookies_file)
    finally:
        # Cleanup: Remove the cookies file after use
        if os.path.isfile(cookies_file):
            os.remove(cookies_file)

    # Respond to the user
    if error is None:
        if os.path.isfile(output_audio_path):
            return send_file(output_audio_path, as_attachment=True)
        else:
            return "Error: Audio file not found after download.", 500
    else:
        return f"Error: {error}"

if __name__ == '__main__':
    app.run(debug=True)