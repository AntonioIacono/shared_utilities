from flask import Flask, send_from_directory, request, abort
import os

app = Flask(__name__)

# Directory where the DASH segments and manifest are stored
DASH_DIRECTORY = 'dash_content'

@app.route('/<path:filename>', methods=['GET'])
def serve_file(filename):
    if not os.path.isfile(os.path.join(DASH_DIRECTORY, filename)):
        abort(404)
    return send_from_directory(DASH_DIRECTORY, filename)

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        abort(400, 'No file part in the request')
    
    file = request.files['file']
    if file.filename == '':
        abort(400, 'No file selected for uploading')
    
    if file:
        input_path = os.path.join(DASH_DIRECTORY, 'input.mp4')
        file.save(input_path)
        
        # Segment the video using ffmpeg
        os.system(f"ffmpeg -i {input_path} -map 0 -seg_duration 10 -f dash {DASH_DIRECTORY}/output.mpd")
        
        return 'File successfully uploaded and processed', 200

if __name__ == '__main__':
    if not os.path.exists(DASH_DIRECTORY):
        os.makedirs(DASH_DIRECTORY)
    
    app.run(host='0.0.0.0', port=8080)
