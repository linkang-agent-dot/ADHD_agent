from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "qc" / "watermark_check_v08" / "ai_generated_logo_mask.png"
FONT = Path(r"C:\Windows\Fonts\msyh.ttc")


def main() -> None:
    # The source is 720x1280. White pixels mark only the fixed logo strokes;
    # FFmpeg's removelogo filter then fills those strokes from nearby pixels.
    mask = Image.new("L", (720, 1280), 0)
    draw = ImageDraw.Draw(mask)

    draw.rounded_rectangle((15, 15, 121, 67), radius=13, outline=255, width=2)
    font = ImageFont.truetype(str(FONT), 27)
    draw.text((23, 22), "AI生成", font=font, fill=255, stroke_width=1, stroke_fill=255)

    # Slight dilation covers compression halos around the translucent source logo.
    mask = mask.filter(ImageFilter.MaxFilter(5))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    mask.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    main()
