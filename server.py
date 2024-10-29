from flask import Flask, request, send_from_directory, jsonify
from PIL import Image
import os
import imageio

app = Flask(__name__)
output_dir = 'output'

# Ensure the output directory exists
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
    
    # Read the GIF and process it
    gif_path = os.path.join(output_dir, 'uploaded.gif')
    gif_file.save(gif_path)

    # Load the GIF
    gif = imageio.mimread(gif_path)
    width, height = gif[0].shape[1], gif[0].shape[0]
    frame_width = width // 5
    frame_height = height // 3

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
        slice_path = os.path.join(output_dir, f'slice{slice_index + 1}.gif')
        imageio.mimsave(slice_path, slice_gif, duration=0.1, loop=0)
        slices.append(f'/output/slice{slice_index + 1}.gif')

    return jsonify({'message': 'GIF sliced successfully', 'slices': slices})

@app.route('/output/<path:filename>', methods=['GET'])
def get_output(filename):
    return send_from_directory(output_dir, filename)

if __name__ == '__main__':
    app.run(debug=True, port=3000)