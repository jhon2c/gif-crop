from PIL import Image

class Resize:
    
    @classmethod
    def gif(cls, input_path, output_path, new_width, new_height):
        gif = Image.open(input_path)
        frames = []

        for frame in range(gif.n_frames):
            gif.seek(frame)
            resized_frame = gif.copy().resize((new_width, new_height))
            frames.append(resized_frame)

        frames[0].save(
            output_path, save_all=True, append_images=frames[1:], loop=0, duration=gif.info['duration']
        )
