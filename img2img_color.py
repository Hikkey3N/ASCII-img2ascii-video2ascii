import argparse
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageOps
from utils import get_data


def parse_arguments():
    # Set up argument parser for command line inputs
    parser = argparse.ArgumentParser("Image to ASCII")
    parser.add_argument("--input", type=str, default="data/input.jpg", help="Path to input image")
    parser.add_argument("--output", type=str, default="data/output.jpg", help="Path to output image")
    parser.add_argument("--language", type=str, default="english")
    parser.add_argument("--mode", type=str, default="standard")
    parser.add_argument("--background", type=str, default="black", choices=["black", "white"],
                        help="Background color for output image")
    parser.add_argument("--num_cols", type=int, default=300, help="Number of characters for output's width")
    parser.add_argument("--scale", type=int, default=2, help="Upsize output")
    return parser.parse_args()


def execute_conversion(options):
    # Determine background color based on user input
    bg_color = (255, 255, 255) if options.background == "white" else (0, 0, 0)

    # Get character set and font based on language and mode
    characters, font, sample_char, scale_factor = get_data(options.language, options.mode)
    total_chars = len(characters)
    cols = options.num_cols

    # Read and preprocess the input image
    img = cv2.imread(options.input, cv2.IMREAD_COLOR)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_height, img_width, _ = img.shape

    # Calculate cell dimensions for ASCII representation
    cell_w = img_width / options.num_cols
    cell_h = scale_factor * cell_w
    rows = int(img_height / cell_h)

    # Adjust cell dimensions if they exceed image dimensions
    if cols > img_width or rows > img_height:
        print("Too many columns or rows. Using default settings.")
        cell_w, cell_h = 6, 12
        cols = int(img_width / cell_w)
        rows = int(img_height / cell_h)

    # Get character dimensions for drawing
    char_bbox = font.getbbox(sample_char)
    char_w, char_h = char_bbox[2], char_bbox[3]

    # Create a new image for the output
    output_w = char_w * cols
    output_h = scale_factor * char_h * rows
    output_img = Image.new("RGB", (output_w, output_h), bg_color)
    draw = ImageDraw.Draw(output_img)

    # Loop through each cell to calculate average color and draw characters
    for row in range(rows):
        for col in range(cols):
            partial_img = img[int(row * cell_h):min(int((row + 1) * cell_h), img_height),
                            int(col * cell_w):min(int((col + 1) * cell_w), img_width), :]

            # Calculate average color for the current cell
            avg_color = np.sum(np.sum(partial_img, axis=0), axis=0) / (cell_h * cell_w)
            avg_color = tuple(avg_color.astype(np.int32).tolist())

            # Determine the character to draw based on average brightness
            char = characters[min(int(np.mean(partial_img) * total_chars / 255), total_chars - 1)]
            draw.text((col * char_w, row * char_h), char, fill=avg_color, font=font)

    # Crop the output image based on background color
    cropped_area = output_img.getbbox() if options.background == "black" else ImageOps.invert(output_img).getbbox()
    output_img = output_img.crop(cropped_area)

    # Save the final output image
    output_img.save(options.output)


if __name__ == '__main__':
    options = parse_arguments()
    execute_conversion(options)