from nonebot import logger
from pathlib import Path
from typing import Tuple
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import random
import base64
import json

_fortune_assets_path = Path(__file__).parent.parent / "assets/fortune"
_fortune_assets_version: str = ''
_copywriting: list[dict] = []
_specific_rules: dict[str, list[str]] = {}
_themes: dict[str, list[str]] = {}


def _load_fortune_assets() -> None:
    global _fortune_assets_version
    global _copywriting
    global _specific_rules
    global _themes

    if not _fortune_assets_version or not _copywriting:
        with open(_fortune_assets_path / "fortune_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            _fortune_assets_version = str(data['version'])
            logger.info(f"fortune version: {_fortune_assets_version}")
            _copywriting = data['copywriting']
            logger.info(f"fortune copywriting: {len(_copywriting)}")

    if not _specific_rules:
        with open(_fortune_assets_path / "specific_rules.json", "r", encoding="utf-8") as f:
            _specific_rules = json.load(f)
            logger.info(f"fortune specific rules: {len(_specific_rules)}")

    if not _themes:
        with open(_fortune_assets_path / "themes.json", "r", encoding="utf-8") as f:
            _themes = json.load(f)
            logger.info(f"fortune themes: {len(_themes)}")


def _get_random_base_image(theme: str = 'random') -> Path:
    if theme == 'random' or theme not in _themes:
        theme = random.choice(list(_themes.keys()))
    theme_path = _fortune_assets_path / 'image' / theme
    return random.choice(list(theme_path.iterdir()))


def _decrement(text: str) -> Tuple[int, list[str]]:
    """
            Split the text, return the number of columns and text list
            TODO: Now, it ONLY fit with 2 columns of text
    """
    length: int = len(text)
    result: list[str] = []
    cardinality = 9
    if length > 4 * cardinality:
        raise Exception

    col_num: int = 1
    while length > cardinality:
        col_num += 1
        length -= cardinality

    # Optimize for two columns
    space = " "
    length = len(text)  # Value of length is changed!

    if col_num == 2:
        if length % 2 == 0:
            # even
            fill_in = space * int(9 - length / 2)
            return col_num, [text[: int(length / 2)] + fill_in, fill_in + text[int(length / 2):]]
        else:
            # odd number
            fill_in = space * int(9 - (length + 1) / 2)
            return col_num, [text[: int((length + 1) / 2)] + fill_in, fill_in + space + text[int((length + 1) / 2):]]

    for i in range(col_num):
        if i == col_num - 1 or col_num == 1:
            result.append(text[i * cardinality:])
        else:
            result.append(text[i * cardinality: (i + 1) * cardinality])

    return col_num, result


def get_theme_key_from_name(name: str) -> str:
    for k, v in _themes.items():
        if name == k or name in v:
            return k
    return 'random'


def generate_fortune(theme: str = 'random') -> Tuple[str, str, str, int]:
    """
    generate fortune image with theme

    returns (base64 encoded image, title, content, rank)
    """
    if theme == 'random' or theme not in _themes:
        theme = random.choice(list(_themes.keys()))
    # choose copywriting
    copywriting = random.choice(_copywriting)
    title = copywriting['good-luck']
    rank = copywriting['rank']
    text = random.choice(copywriting['content'])

    # choose base image
    base_image_path = _get_random_base_image(theme)
    generated_image: Image.Image = Image.open(base_image_path)

    # draw title
    image_font_center = [140, 99]
    font = ImageFont.truetype(str(_fortune_assets_path / 'font/Mamelon.otf'), 45)
    font_bbox = font.getbbox(title)
    font_length = (font_bbox[2] - font_bbox[0], font_bbox[3] - font_bbox[1])
    draw = ImageDraw.Draw(generated_image)
    draw.text(
        (
            image_font_center[0] - font_length[0] / 2,
            image_font_center[1] - font_length[1] / 2,
        ),
        title,
        fill='#F5F5F5',
        font=font,
    )

    # draw content
    font_size = 25
    color = "#323232"
    image_font_center = [140, 297]
    ttfront = ImageFont.truetype(str(_fortune_assets_path / 'font/sakura.ttf'), font_size)
    slices, result = _decrement(text)

    for i in range(slices):
        font_height: int = len(result[i]) * (font_size + 4)
        text_vertical: str = "\n".join(result[i])
        x: int = int(
            image_font_center[0]
            + (slices - 2) * font_size / 2
            + (slices - 1) * 4
            - i * (font_size + 4)
        )
        y: int = int(image_font_center[1] - font_height / 2)
        draw.text((x, y), text_vertical, fill=color, font=ttfront)

    # save image
    buffer = BytesIO()
    generated_image.save(buffer, format='png')
    bytes_data = buffer.getvalue()
    buffer.close()
    base64_str = base64.b64encode(bytes_data).decode('utf-8')
    return base64_str, title, text, rank


_load_fortune_assets()

if __name__ == '__main__':
    with open('test.txt', 'w') as f:
        f.write(generate_fortune()[0])
