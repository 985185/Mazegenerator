import glob
import os
from PIL import Image, ImageDraw, ImageFont

def load_font(px: int):
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", px)
    except Exception:
        return ImageFont.load_default()

def draw_label(draw: ImageDraw.ImageDraw, xy, text, px, font):
    # black text with white outline for B/W print clarity
    stroke_w = max(2, px // 10)
    # Pillow supports stroke_width/stroke_fill on modern versions
    try:
        draw.text(xy, text, font=font, fill=(0,0,0),
                  stroke_width=stroke_w, stroke_fill=(255,255,255))
    except TypeError:
        # fallback manual stroke
        x, y = xy
        for dx in range(-stroke_w, stroke_w+1):
            for dy in range(-stroke_w, stroke_w+1):
                if dx == 0 and dy == 0:
                    continue
                draw.text((x+dx, y+dy), text, font=font, fill=(255,255,255))
        draw.text((x, y), text, font=font, fill=(0,0,0))

def stamp(path: str):
    img = Image.open(path).convert("RGB")
    w, h = img.size
    draw = ImageDraw.Draw(img)

    pad = int(min(w, h) * 0.05)              # 5% margin
    px  = max(24, int(min(w, h) * 0.05))     # font size ~5%, min 24
    font = load_font(px)

    # START near top-left
    start_xy = (pad, pad)

    # FINISH near bottom-right (account for text size)
    try:
        bbox = draw.textbbox((0,0), "FINISH", font=font)
        tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    except Exception:
        tw, th = draw.textsize("FINISH", font=font)
    finish_xy = (w - pad - tw, h - pad - th)

    draw_label(draw, start_xy, "START", px, font)
    draw_label(draw, finish_xy, "FINISH", px, font)

    img.save(path, dpi=(300,300))

def main():
    outdir = "mazes_output"
    paths = sorted(glob.glob(os.path.join(outdir, "*.png")))
    if not paths:
        print(f"No PNGs found in ./{outdir}")
        return
    for p in paths:
        try:
            stamp(p)
            print("stamped", os.path.basename(p))
        except Exception as e:
            print("failed to stamp", os.path.basename(p), "-", e)
    print(f"Stamped {len(paths)} PNG(s) in ./{outdir}")

if __name__ == "__main__":
    main()