from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "overlays" / "effect_text_v01"
FONT_PATH = Path(r"C:\Windows\Fonts\msyhbd.ttc")


SPECS = [
    ("T01_军训显痕.png", "军训最尴尬的是显痕", 46, "yellow"),
    ("T02_学姐安利.png", "学姐安利的粉底肤无痕款", 40, "white"),
    ("T03_跑跳无痕.png", "跑跳也不显痕", 58, "white"),
    ("T04_平整杯面.png", "一片式平整杯面", 54, "white"),
    ("T05_冰丝透气.png", "冰丝透气不黏身", 54, "white"),
    ("T06_白T无痕.png", "穿白T不透色不显痕", 46, "white"),
    ("T07_军训必备.png", "军训必备", 58, "cta"),
]


def draw_centered_text(text: str, font_size: int, style: str) -> Image.Image:
    canvas = Image.new("RGBA", (720, 150), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype(str(FONT_PATH), font_size)
    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=0)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    x = (720 - width) // 2
    y = 10 - bbox[1]

    if style == "yellow":
        fill = "#FFD83D"
        inner = "#D93520"
        outer = "#7B201A"
    elif style == "cta":
        fill = "#FFFDF2"
        inner = "#E72E22"
        outer = "#FFD43A"
    else:
        fill = "#FFFDF2"
        inner = "#F04A22"
        outer = "#FFD43A"

    # Soft dark offset, golden outer rim, red/orange inner rim, then bright face.
    draw.text(
        (x + 4, y + 7), text, font=font, fill="#5B1B1680",
        stroke_width=10, stroke_fill="#5B1B1680",
    )
    draw.text(
        (x, y), text, font=font, fill=fill,
        stroke_width=11 if style == "cta" else 9, stroke_fill=outer,
    )
    draw.text(
        (x, y), text, font=font, fill=fill,
        stroke_width=7 if style == "cta" else 6, stroke_fill=inner,
    )

    underline_y = y + height + 18
    line_left = max(42, x + 10)
    line_right = min(678, x + width - 10)
    draw.rounded_rectangle(
        (line_left, underline_y, line_right, underline_y + 6),
        radius=3,
        fill="#FFD43A",
    )
    draw.ellipse((line_left - 14, underline_y - 4, line_left - 6, underline_y + 4), fill="#FFF5A6")
    draw.ellipse((line_right + 6, underline_y - 4, line_right + 14, underline_y + 4), fill="#FFF5A6")
    return canvas


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for filename, text, font_size, style in SPECS:
        image = draw_centered_text(text, font_size, style)
        image.save(OUTPUT / filename)
        print(OUTPUT / filename)


if __name__ == "__main__":
    main()
