import os, imageio
import uuid
from flask import Flask, jsonify, request, send_from_directory, make_response, render_template
from engine.utils.resize import Resize
import zipfile

app = Flask(__name__)
output_dir = 'output'

# Disable caching for the output directory
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Clear the output directory if it exists [Remove all subdirectories]
if os.path.exists(output_dir):
    for item in os.listdir(output_dir):
        item_path = os.path.join(output_dir, item)
        if os.path.isdir(item_path):
            os.system(f'rm -rf {item_path}')
        else:
            os.remove(item_path)
    


if not os.path.exists(output_dir):
    os.makedirs(output_dir)

@app.route('/', methods=['GET'])
def home():
    return send_from_directory('public', 'index.html')

@app.route('/upload', methods=['POST'])
def upload_gif():
    if 'gif' not in request.files:
        return 'No file uploaded.', 400

    gif_file = request.files['gif']

    session_id = uuid.uuid4().hex
    store_dir = os.path.join(output_dir, session_id)
    
    # Read the GIF and process it
    gif_path = os.path.join(output_dir, 'uploaded.gif')
    gif_file.save(gif_path)

    # Load the GIF
    Resize.gif(gif_file, gif_path, 360, 216)
    gif = imageio.mimread(gif_path)

    # Split the GIF into 15 slices
    width, height = gif[0].shape[1], gif[0].shape[0]
    frame_width = width // 5
    frame_height = height // 3

    # Create a folder to store the slices
    if not os.path.exists(store_dir):
        os.makedirs(store_dir)
    
    slices = []
    for slice_index in range(15):
        x = (slice_index % 5) * frame_width
        y = (slice_index // 5) * frame_height

        # Create a new list for the current slice
        slice_gif = []
        for frame in gif:
            # Create a slice from each frame
            slice_frame = frame[y:y + frame_height, x:x + frame_width]
            slice_gif.append(slice_frame)

        # Save the current slice as a GIF
        slice_path = os.path.join(store_dir, f'slice{slice_index + 1}.gif')
        imageio.mimsave(slice_path, slice_gif, duration=0.1, loop=0)
        slices.append(f'/output/{session_id}/slice{slice_index + 1}.gif')

    return render_template('slices.html', slices=slices, session_id=session_id)

@app.route('/output/<path:filename>', methods=['GET'])
def get_output(filename):
    response = make_response(send_from_directory(output_dir, filename))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/download/<path:session_id>', methods=['GET'])
def download_zip(session_id):
    # Create a ZIP file with all the slices
    with zipfile.ZipFile(os.path.join(output_dir, session_id, 'slices.zip'), 'w') as zipf:
        for slice_index in range(15):
            slice_path = os.path.join(output_dir, session_id, f'slice{slice_index + 1}.gif')
            zipf.write(slice_path, f'slice{slice_index + 1}.gif')
        
    response = make_response(jsonify({'message': 'ZIP file created.'}))
    response.headers['HX-Redirect'] = '/' + os.path.join(output_dir, session_id, 'slices.zip')
    return response

if __name__ == '__main__':
    app.run(debug=True, port=3000)