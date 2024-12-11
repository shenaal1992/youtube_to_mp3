from flask import Flask, render_template, request, send_file
import yt_dlp
import io

app = Flask(__name__)

def download_mp3(video_url):
    """
    Download audio from YouTube using yt-dlp and return the audio as a byte stream (in memory).
    """
    # yt-dlp options for downloading audio without cookies
    ydl_opts = {
        'format': 'bestaudio/best',  # Download best available audio
        'quiet': True,  # Hide progress
        'extractaudio': True,  # Extract audio
        'audioquality': 1,  # Highest audio quality
        'outtmpl': '-',  # Output to stdout (use '-' to avoid saving it to a file)
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Download the video and return the audio file as a byte stream
            info_dict = ydl.extract_info(video_url, download=True)
            # Get the URL of the best audio format and download it
            audio_url = info_dict['formats'][0]['url']
            # Download the audio directly to memory (in bytes)
            with yt_dlp.YoutubeDL({'quiet': True, 'extractaudio': True, 'outtmpl': '-', 'format': 'bestaudio/best'}) as ydl:
                audio_bytes = ydl.urlopen(audio_url).read()
            return audio_bytes
    except Exception as e:
        print(f"Error: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    video_url = request.form['url']
    
    # Download the video as MP3 in memory (without saving to a file)
    audio_data = download_mp3(video_url)

    if audio_data:
        # Create an in-memory file using BytesIO
        audio_stream = io.BytesIO(audio_data)
        audio_stream.seek(0)  # Ensure the stream is at the start

        # Send the audio file to the user as a downloadable file
        return send_file(audio_stream, as_attachment=True, download_name='downloaded_audio.mp3', mimetype='audio/mp3')
    else:
        return "Error: Could not download the video."

if __name__ == '__main__':
    app.run(debug=True)