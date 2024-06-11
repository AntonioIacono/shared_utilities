import os
import subprocess
from flask import Flask, Response, request

app = Flask(__name__)

VIDEO_DIRECTORY = 'videos'  # Directory to store uploaded videos

# Ensure the directory exists
if not os.path.exists(VIDEO_DIRECTORY):
    os.makedirs(VIDEO_DIRECTORY)

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return "No video part in the request", 400

    file = request.files['video']
    if file.filename == '':
        return "No selected file", 400

    file_path = os.path.join(VIDEO_DIRECTORY, file.filename)
    file.save(file_path)
    return "File uploaded successfully", 200

@app.route('/stream')
def stream_video():
    video_path = os.path.join(VIDEO_DIRECTORY, 'video.mp4')  # Adjust to your uploaded video file

    if not os.path.exists(video_path):
        return "Video not found", 404

    return Response(generate_stream(video_path),
                    mimetype='video/mp4')

def generate_stream(video_path):
    command = [
        'ffmpeg',
        '-i', video_path,
        '-f', 'mp4',
        '-vcodec', 'libx264',
        '-preset', 'fast',
        '-r', '15',  # Frame rate
        '-s', '1280x720',  # Resolution
        '-b:v', '1M',  # Bitrate (adjust as needed)
        '-bufsize', '2M',
        '-pix_fmt', 'yuv420p',
        '-movflags', 'frag_keyframe+empty_moov+default_base_moof',
        '-an',
        '-sn',
        'pipe:1'
    ]

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    while True:
        data = process.stdout.read(1024)
        if not data:
            break
        yield data

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
