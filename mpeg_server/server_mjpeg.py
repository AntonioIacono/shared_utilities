import os
import subprocess
from flask import Flask, Response, request, jsonify

app = Flask(__name__)

VIDEO_DIRECTORY = 'videos'  # Directory to store uploaded videos

# Ensure the directory exists
if not os.path.exists(VIDEO_DIRECTORY):
    os.makedirs(VIDEO_DIRECTORY)

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({"message": "No video part in the request"}), 400

    file = request.files['video']
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400

    file_path = os.path.join(VIDEO_DIRECTORY, file.filename)
    file.save(file_path)
    return jsonify({"message": "File uploaded successfully", "filename": file.filename}), 200

@app.route('/stream/<filename>')
def stream_video(filename):
    video_path = os.path.join(VIDEO_DIRECTORY, filename)

    if not os.path.exists(video_path):
        return jsonify({"message": "Video not found"}), 404

    return Response(generate_stream(video_path), mimetype='video/mp4')

def generate_stream(video_path):
    
    command = [
        'ffmpeg',
        '-stream_loop', '-1',  # Loop indefinito
        '-i', video_path,
        '-f', 'avi',           # Formato di output
        '-vcodec', 'mjpeg',    # Codec video
        '-r', '30',            # Frame rate
        '-q:v', '5',           # Qualità del video (1-31, 1 è la migliore qualità)
        'pipe:1'               # Output su stdout
    ]


    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    while True:
        data = process.stdout.read(1024)
        if not data:
            break
        yield data

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)