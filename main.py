import yt_dlp
import os
import json

def get_cookies_from_browser(output_cookies_file):
    """
    Extract cookies from the browser and save them to a JSON file for use in yt-dlp.
    
    :param output_cookies_file: Path to save the cookies in JSON format.
    """
    # yt-dlp options to extract cookies from browser (Chrome example)
    ydl_opts = {
        'extractor_args': {
            'youtube': ['cookies_from_browser'],  # Extract cookies
        },
        'cookiefile': output_cookies_file,  # Save cookies to file
        'quiet': False,  # Display progress
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("Extracting cookies from your browser...")
            ydl.extract_info('https://www.youtube.com', download=False)  # No need to download, just extract cookies
        print(f"Cookies saved to: {output_cookies_file}")
    except Exception as e:
        print(f"Error extracting cookies: {e}")

def download_mp3(video_url, output_audio_path, cookies_file):
    """
    Download audio from an age-restricted video using yt-dlp without using ffmpeg for postprocessing.

    :param video_url: URL of the video to download.
    :param output_audio_path: Path to save the extracted audio file.
    :param cookies_file: Path to the cookies file for authentication.
    """
    # Ensure cookies file exists
    if not os.path.isfile(cookies_file):
        print(f"Error: Cookies file '{cookies_file}' not found.")
        return

    # Ensure output directory exists
    output_dir = os.path.dirname(output_audio_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # yt-dlp options
    ydl_opts = {
        'format': 'bestaudio/best',  # Download best available audio
        'outtmpl': output_audio_path,  # Output file path template
        'cookies': cookies_file,  # Use cookies for authentication
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',  # Mimic a browser
        'extractor_args': {'youtube': ['player-client=ios']},  # Use a specific client for better compatibility
        'noplaylist': True,  # Ensure only the single video is downloaded
        'quiet': False,  # Display progress
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        print(f"Audio downloaded successfully: {output_audio_path}")
    except yt_dlp.utils.DownloadError as e:
        print(f"Download error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Example usage
if __name__ == "__main__":
    cookies_file = 'cookies.json'  # Path to save cookies
    video_url = 'https://www.youtube.com/watch?v=UPkMkIOzej8&ab_channel=FeelGood'
    output_audio_path = 'downloaded_audio.mp3'

    # Extract cookies if not already available
    if not os.path.isfile(cookies_file):
        get_cookies_from_browser(cookies_file)  # Extract cookies if necessary

    # Call the function to download the video
    download_mp3(video_url, output_audio_path, cookies_file)