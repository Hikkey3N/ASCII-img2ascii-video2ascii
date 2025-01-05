import numpy as np
from PIL import Image, ImageFont, ImageDraw, ImageOps


def arrange_characters(char_list, font, lang):
    # Determine character dimensions based on the language
    if lang == "chinese":
        char_w, char_h = font.getbbox("制")[2], font.getbbox("制")[3]
    elif lang == "korean":
        char_w, char_h = font.getbbox("ㅊ")[2], font.getbbox("ㅊ")[3]
    elif lang == "japanese":
        char_w, char_h = font.getbbox("あ")[2], font.getbbox("あ")[3]
    elif lang in ["english", "german", "french", "spanish", "italian", "portuguese", "polish"]:
        char_w, char_h = font.getbbox("A")[2], font.getbbox("A")[3]
    elif lang == "russian":
        char_w, char_h = font.getbbox("A")[2], font.getbbox("A")[3]
    
    max_chars = min(len(char_list), 100)
    img_w = char_w * len(char_list)
    img_h = char_h

    # Create a new image to draw characters
    img_output = Image.new("L", (img_w, img_h), 255)
    draw = ImageDraw.Draw(img_output)
    draw.text((0, 0), char_list, fill=0, font=font)

    # Crop the image to remove excess whitespace
    cropped_img = ImageOps.invert(img_output).getbbox()
    img_output = img_output.crop(cropped_img)

    # Calculate brightness for each character
    brightness = [np.mean(np.array(img_output)[:, 10 * i:10 * (i + 1)]) for i in range(len(char_list))]
    char_list = list(char_list)
    paired_lists = zip(brightness, char_list)
    paired_lists = sorted(paired_lists)

    result = ""
    count = 0
    step_increment = (paired_lists[-1][0] - paired_lists[0][0]) / max_chars
    current_val = paired_lists[0][0]

    # Build the result string based on brightness
    for value, char in paired_lists:
        if value >= current_val:
            result += char
            count += 1
            current_val += step_increment
        if count == max_chars:
            break

    # Ensure the last character is included
    if result[-1] != paired_lists[-1][1]:
        result += paired_lists[-1][1]

    return result


def get_data(language, mode):
    # Load character sets and fonts based on the specified language
    if language == "general":
        from alphabets import GENERAL as characters
        font = ImageFont.truetype("fonts/DejaVuSansMono-Bold.ttf", size=20)
        sample_char = "A"
        scale = 2
    elif language == "english":
        from alphabets import ENGLISH as characters
        font = ImageFont.truetype("fonts/DejaVuSansMono-Bold.ttf", size=20)
        sample_char = "A"
        scale = 2
    elif language == "german":
        from alphabets import GERMAN as characters
        font = ImageFont.truetype("fonts/DejaVuSansMono-Bold.ttf", size=20)
        sample_char = "A"
        scale = 2
    elif language == "french":
        from alphabets import FRENCH as characters
        font = ImageFont.truetype("fonts/DejaVuSansMono-Bold.ttf", size=20)
        sample_char = "A"
        scale = 2
    elif language == "italian":
        from alphabets import ITALIAN as characters
        font = ImageFont.truetype("fonts/DejaVuSansMono-Bold.ttf", size=20)
        sample_char = "A"
        scale = 2
    elif language == "polish":
        from alphabets import POLISH as characters
        font = ImageFont.truetype("fonts/DejaVuSansMono-Bold.ttf", size=20)
        sample_char = "A"
        scale = 2
    elif language == "portuguese":
        from alphabets import PORTUGUESE as characters
        font = ImageFont.truetype("fonts/DejaVuSansMono-Bold.ttf", size=20)
        sample_char = "A"
        scale = 2
    elif language == "spanish":
        from alphabets import SPANISH as characters
        font = ImageFont.truetype("fonts/DejaVuSansMono-Bold.ttf", size=20)
        sample_char = "A"
        scale = 2
    elif language == "russian":
        from alphabets import RUSSIAN as characters
        font = ImageFont.truetype("fonts/DejaVuSansMono-Bold.ttf", size=20)
        sample_char = "Ш"
        scale = 2
    elif language == "chinese":
        from alphabets import CHINESE as characters
        font = ImageFont.truetype("fonts/simsun.ttc", size=10)
        sample_char = "制"
        scale = 1
    elif language == "korean":
        from alphabets import KOREAN as characters
        font = ImageFont.truetype("fonts/arial-unicode.ttf", size=10)
        sample_char = "ㅊ"
        scale = 1
    elif language == "japanese":
        from alphabets import JAPANESE as characters
        font = ImageFont.truetype("fonts/arial-unicode.ttf", size=10)
        sample_char = "お"
        scale = 1
    else:
        print("Invalid language")
        return None, None, None, None

    # Load character list based on mode
    try:
        if len(characters) > 1:
            char_list = characters[mode]
        else:
            char_list = characters["standard"]
    except:
        print("Invalid mode for {}".format(language))
        return None, None, None, None

    # Arrange characters if not in general mode
    if language != "general":
        char_list = arrange_characters(char_list, font, language)

    return char_list, font, sample_char, scale