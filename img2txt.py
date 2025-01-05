import argparse
import cv2
import numpy as np
from utils import get_data
import os


def get_args():
    # Set up argument parser for command line inputs
    parser = argparse.ArgumentParser("Image to ASCII")
    parser.add_argument("--input", type=str, default="data/input.jpg", help="Path to input image")
    parser.add_argument("--output", type=str, default="txt_output.txt", help="Path to output text file")
    parser.add_argument("--mode", type=str, default="complex", choices=["simple", "complex"],
                        help="10 or 70 different characters")
    parser.add_argument("--num_cols", type=int, default=200, help="Number of characters for output's width")
    return parser.parse_args()


def execute_conversion(options):
    # Create results directory if it doesn't exist
    os.makedirs("results", exist_ok=True)

    # Define character sets based on the selected mode
    if options.mode == "simple":
        CHAR_LIST = '@%#*+=-:. '
    else:
        CHAR_LIST = r"$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. "
    
    num_chars = len(CHAR_LIST)
    image = cv2.imread(options.input)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    height, width = image.shape

    # Calculate cell dimensions for ASCII representation
    cell_width = width / options.num_cols
    cell_height = 2 * cell_width
    num_rows = int(height / cell_height)

    # Adjust cell dimensions if they exceed image dimensions
    if options.num_cols > width or num_rows > height:
        print("Too many columns or rows. Using default settings.")
        cell_width = 6
        cell_height = 12
        options.num_cols = int(width / cell_width)
        num_rows = int(height / cell_height)

    # Open output file to write ASCII characters
    with open(os.path.join("results", options.output), 'w') as output_file:
        for i in range(num_rows):
            for j in range(options.num_cols):
                # Calculate average brightness for the current cell
                avg_brightness = np.mean(image[int(i * cell_height):min(int((i + 1) * cell_height), height),
                                                int(j * cell_width):min(int((j + 1) * cell_width), width)])
                
                # Determine the character to write based on brightness
                char_index = min(int(avg_brightness * num_chars / 255), num_chars - 1)
                output_file.write(CHAR_LIST[char_index])
            output_file.write("\n")


if __name__ == '__main__':
    options = get_args()
    execute_conversion(options)