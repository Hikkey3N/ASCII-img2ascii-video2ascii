import argparse
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageOps, ImageFont
import os

def parse_arguments():
    # Set up argument parser for command line inputs
    parser = argparse.ArgumentParser("Video to ASCII")
    parser.add_argument("--input", type=str, default="data/input.mp4", help="Path to input video")
    parser.add_argument("--output", type=str, default="vid_Color_output.mp4", help="Path to output video")
    parser.add_argument("--mode", type=str, default="complex", choices=["simple", "complex"],
                        help="10 or 70 different characters")
    parser.add_argument("--background", type=str, default="black", choices=["black", "white"],
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
        char_list = r"$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "

    # Determine background color based on user input
    bg_color = (255, 255, 255) if options.background == "white" else (0, 0, 0)

    # Load font
    font = ImageFont.truetype("fonts/DejaVuSansMono-Bold.ttf", size=int(10 * options.scale))

    # Open video capture
    cap = cv2.VideoCapture(options.input)

    # Get FPS
    fps = int(cap.get(cv2.CAP_PROP_FPS)) if options.fps == 0 else options.fps

    num_chars = len(char_list)
    num_cols = options.num_cols

    while cap.isOpened():
        flag, frame = cap.read()

        if flag:
            # Use the original color frame, don't convert to grayscale
            image = frame
        else:
            break

        height, width, _ = image.shape
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
        out_image = Image.new("RGB", (out_width, out_height), bg_color)

        draw = ImageDraw.Draw(out_image)

        # Loop through each cell to calculate average color and draw characters
        for i in range(num_rows):
            for j in range(num_cols):
                partial_image = image[int(i * cell_height):min(int((i + 1) * cell_height), height),
                                      int(j * cell_width):min(int((j + 1) * cell_width), width)]

                # Calculate the average color for the region (from the original color frame)
                avg_color = np.mean(partial_image, axis=(0, 1))  # Averaging across rows and columns (height and width)

                # Convert to a tuple and make sure the color values are integers (between 0 and 255)
                avg_color = tuple(np.clip(avg_color.astype(int), 0, 255))  # Ensure the color values are between 0-255

                # Select the character based on the grayscale value
                char = char_list[min(int(np.mean(partial_image) * num_chars / 255), num_chars - 1)]
                
                # Draw the character on the output image
                draw.text((j * char_width, i * char_height), char, fill=avg_color, font=font)

        # Crop the output image based on background color
        cropped_area = out_image.getbbox() if options.background == "black" else ImageOps.invert(out_image).getbbox()
        out_image = out_image.crop(cropped_area)

        # Convert to BGR for video writing
        out_image = cv2.cvtColor(np.array(out_image), cv2.COLOR_RGB2BGR)

        # Initialize video writer
        if 'out' not in locals():
            out = cv2.VideoWriter("results/" + options.output, cv2.VideoWriter_fourcc(*"mp4v"), fps,
                                   (out_image.shape[1], out_image.shape[0]))

        # Overlay if specified
        if options.overlay_ratio:
            height, width, _ = out_image.shape
            overlay = cv2.resize(frame, (int(width * options.overlay_ratio), int(height * options.overlay_ratio)))
            out_image[height - int(height * options.overlay_ratio):, width - int(width * options.overlay_ratio):, :] = overlay

        out.write(out_image)

    cap.release()
    out.release()


if __name__ == '__main__':
    options = parse_arguments()
    execute_conversion(options)
