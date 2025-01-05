import argparse
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageOps
import os
from utils import get_data


def get_args():
    # Set up argument parser for command line inputs
    parser = argparse.ArgumentParser("Image to ASCII")
    parser.add_argument("--input", type=str, default="data/input.jpg", help="Path to input image")
    parser.add_argument("--output", type=str, default="img_output.jpg", help="Path to output image")
    parser.add_argument("--language", type=str, default="english")
    parser.add_argument("--mode", type=str, default="standard")
    parser.add_argument("--background", type=str, default="black", choices=["black", "white"],
                        help="Background color for output image")
    parser.add_argument("--num_cols", type=int, default=600, help="Number of characters for output's width")
    args = parser.parse_args()
    return args


def execute_conversion(options):
    # Create results directory if it doesn't exist
    os.makedirs("results", exist_ok=True)

    # Determine background color based on user input
    bg_color = 255 if options.background == "white" else 0

    # Get character set and font based on language and mode
    char_list, font, sample_character, scale = get_data(options.language, options.mode)
    num_chars = len(char_list)
    num_cols = options.num_cols

    # Read and preprocess the input image
    image = cv2.imread(options.input)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    height, width = image.shape

    # Calculate cell dimensions for ASCII representation
    cell_width = width / num_cols
    cell_height = scale * cell_width
    num_rows = int(height / cell_height)

    # Adjust cell dimensions if they exceed image dimensions
    if num_cols > width or num_rows > height:
        print("Too many columns or rows. Using default settings.")
        cell_width = 6
        cell_height = 12
        num_cols = int(width / cell_width)
        num_rows = int(height / cell_height)

    # Get character dimensions for drawing
    char_bbox = font.getbbox(sample_character)
    char_width, char_height = char_bbox[2], char_bbox[3]

    # Create a new image for the output
    out_width = char_width * num_cols
    out_height = scale * char_height * num_rows
    out_image = Image.new("L", (out_width, out_height), bg_color)

    draw = ImageDraw.Draw(out_image)

    # Loop through each cell to calculate average brightness and draw characters
    for i in range(num_rows):
        line = "".join([char_list[min(int(np.mean(image[int(i * cell_height):min(int((i + 1) * cell_height), height),
                                                  int(j * cell_width):min(int((j + 1) * cell_width),
                                                                          width)]) / 255 * num_chars), num_chars - 1)]
                        for j in range(num_cols)]) + "\n"
        draw.text((0, i * char_height), line, fill=255 - bg_color, font=font)

    # Crop the output image based on background color
    cropped_area = out_image.getbbox() if options.background == "black" else ImageOps.invert(out_image).getbbox()
    out_image = out_image.crop(cropped_area)

    # Save the final output image
    out_image.save(os.path.join("results", options.output))


if __name__ == '__main__':
    options = get_args()
    execute_conversion(options)