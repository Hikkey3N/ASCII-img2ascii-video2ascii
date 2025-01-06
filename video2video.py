import argparse
import cv2
import numpy as np
from PIL import Image, ImageFont, ImageDraw, ImageOps
import os


def get_args():
    # Set up argument parser for command line inputs
    parser = argparse.ArgumentParser("Video to ASCII")
    parser.add_argument("--input", type=str, default="data/input.mp4", help="Path to input video")
    parser.add_argument("--output", type=str, default="vid_output.mp4", help="Path to output video")
    parser.add_argument("--mode", type=str, default="simple", choices=["simple", "complex"],
                        help="10 or 70 different characters")
    parser.add_argument("--background", type=str, default="white", choices=["black", "white"],
                        help="Background color for output video")
    parser.add_argument("--num_cols", type=int, default=100, help="Number of characters for output's width")
    parser.add_argument("--scale", type=int, default=1, help="Upsize output")
    parser.add_argument("--fps", type=int, default=0, help="Frames per second")
    parser.add_argument("--overlay_ratio", type=float, default=0.2, help="Overlay width ratio")
    return parser.parse_args()


def execute_conversion(options):
    # Create results directory if it doesn't exist
    os.makedirs("results", exist_ok=True)

    # Determine character set based on mode
    if options.mode == "simple":
        char_list = r'@%#*+=-:. '
    else:
        char_list = r"$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^'. "

    # Determine background color based on user input
    bg_color = 255 if options.background == "white" else 0

    # Load font
    font = ImageFont.truetype("fonts/DejaVuSansMono-Bold.ttf", size=int(10 * options.scale))

    # Open video capture
    cap = cv2.VideoCapture(options.input)

    # Get input video properties
    input_fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = input_fps if options.fps == 0 else options.fps

    # Calculate frame duration to process frames at the correct rate
    frame_duration = 1.0 / input_fps

    print(f"Input FPS: {input_fps}, Total frames: {frame_count}, Output FPS: {fps}")

    num_chars = len(char_list)
    num_cols = options.num_cols

    # Initialize variables for video writer and time tracking
    out = None
    frame_idx = 0

    while cap.isOpened():
        flag, frame = cap.read()

        if not flag:
            break

        # Process the current frame
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        height, width = image.shape
        cell_width = width / num_cols
        cell_height = 2 * cell_width
        num_rows = int(height / cell_height)

        # Adjust cell dimensions if they exceed image dimensions
        if num_cols > width or num_rows > height:
            print("Too many columns or rows. Using default settings.")
            cell_width = 6
            cell_height = 12
            num_cols = int(width / cell_width)
            num_rows = int(height / cell_height)

        # Get character dimensions for drawing
        char_bbox = font.getbbox("A")
        char_width, char_height = char_bbox[2], char_bbox[3]

        # Create a new image for the output
        out_width = char_width * num_cols
        out_height = 2 * char_height * num_rows
        out_image = Image.new("L", (out_width, out_height), bg_color)

        draw = ImageDraw.Draw(out_image)

        # Loop through each cell to calculate average brightness and draw characters
        for i in range(num_rows):
            line = "".join([char_list[min(int(np.mean(
                image[int(i * cell_height):min(int((i + 1) * cell_height), height),
                int(j * cell_width):min(int((j + 1) * cell_width), width)]) * num_chars / 255), num_chars - 1)] for j in
                            range(num_cols)]) + "\n"
            draw.text((0, i * char_height), line, fill=255 - bg_color, font=font)

        # Crop the output image based on background color
        cropped_area = out_image.getbbox() if options.background == "black" else ImageOps.invert(out_image).getbbox()
        out_image = out_image.crop(cropped_area)

        # Convert to BGR for video writing
        out_image = cv2.cvtColor(np.array(out_image), cv2.COLOR_GRAY2BGR)

        # Initialize video writer if not already done
        if out is None:
            out = cv2.VideoWriter("results/" + options.output, cv2.VideoWriter_fourcc(*"mp4v"), fps,
                                  (out_image.shape[1], out_image.shape[0]))

        # Overlay if specified
        if options.overlay_ratio:
            overlay_width = int(out_image.shape[1] * options.overlay_ratio)
            overlay_height = int(out_image.shape[0] * options.overlay_ratio)
            overlay = cv2.resize(frame, (overlay_width, overlay_height))
            out_image[-overlay_height:, -overlay_width:, :] = overlay

        # Write the frame to the output video
        out.write(out_image)

        # Increment time and frame index
        time_elapsed += frame_duration
        frame_idx += 1

        print(f"Processed frame {frame_idx}/{frame_count}")

    cap.release()
    if out:
        out.release()

    print("Video conversion completed successfully!")



if __name__ == '__main__':
    options = get_args()
    execute_conversion(options)