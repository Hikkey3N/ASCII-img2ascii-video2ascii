# ASCII Art Generator

Converts images and videos into ASCII art. Supports color output, multilingual character sets (Latin, CJK, Korean, and more), and three export formats: image, video, and plain text.

![Demo](demo.gif)

## How it works

Each input frame is divided into pixel blocks. The average luminance of each block is computed, then mapped to a character from the active charset using a prebuilt lookup table — lighter characters go to bright pixels, heavier ones to dark pixels. For color output, the dominant color of each block is sampled and applied to the rendered character.

## Usage

```bash
pip install -r requirements.txt

# Image → ASCII image (no color)
python img2img.py

# Image → ASCII image (with color)
python img2img_color.py

# Image → plain text file
python img2txt.py

# Video → ASCII video (no color)
python video2video.py

# Video → ASCII video (with color)
python video2video_color.py
```

Input/output paths and resolution are set at the top of each script.

## Example output

**Image (non-color)**
<p align="center">
  <img src="demo/img_demo.jpg" width=800><br/>
</p>

**Image (color)**
<p align="center">
  <img src="demo/img_color_demo.jpg" width=800><br/>
</p>

**Korean character set**
<p align="center">
  <img src="demo/demo_korean.jpg" width=800><br/>
</p>

**Video (color)**
<p align="center">
  <img src="demo/demo_complex_color_160.gif" width=800><br/>
</p>

**Video (monochrome)**
<p align="center">
  <img src="demo/demo_simple_white_150.gif" width=800><br/>
</p>

## Tech

- Python 3
- OpenCV — frame extraction and image I/O
- Pillow — image rendering
- Custom `alphabets.py` for multilingual charset definitions ranked by visual ink density
