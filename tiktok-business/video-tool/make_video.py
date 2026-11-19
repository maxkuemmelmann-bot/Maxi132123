"""
Baut TikTok-Videos (1080x1920, 9:16) aus Produktbildern + Texten.

Aufruf:
    python3 make_video.py woche1.json            -> rendert alle Videos, deren Bilder vorhanden sind
    python3 make_video.py woche1.json 05         -> rendert nur Video mit id "05"

Bilder liegen in:  tiktok-business/produkte/<produkt>/1.jpg, 2.jpg, ... (jpg, jpeg, png oder webp)
Optionale KI-Szene: tiktok-business/produkte/<produkt>/problem.jpg (fehlt sie, wird die Folie übersprungen)
Ausgabe:           tiktok-business/videos/fertig/<id>_<name>.mp4
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920          # TikTok-Format
FPS = 30
BASE = Path(__file__).resolve().parent.parent   # Ordner tiktok-business
PRODUKTE = Path(os.environ.get("PRODUKTE_DIR", BASE / "produkte"))      # zum Testen überschreibbar
AUSGABE = Path(os.environ.get("AUSGABE_DIR", BASE / "videos" / "fertig"))
FONT_BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
FONT_MED = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"


def find_image(key):
    """'fugenstift/1' -> Pfad zur Bilddatei oder None, wenn nicht vorhanden."""
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        p = PRODUKTE / (key + ext)
        if p.exists():
            return p
    return None


def wrap(draw, text, font, max_w):
    """Bricht Text in Zeilen um, damit er nicht über den Rand geht."""
    lines, line = [], ""
    for word in text.split():
        test = (line + " " + word).strip()
        if draw.textlength(test, font=font) <= max_w:
            line = test
        else:
            lines.append(line)
            line = word
    lines.append(line)
    return lines


def text_box(img, text, y, size=68):
    """Weißer Kasten mit schwarzer Schrift (typischer TikTok-Textstil)."""
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT_BOLD, size)
    lines = wrap(draw, text, font, W - 220)
    line_h = int(size * 1.25)
    for i, line in enumerate(lines):
        tw = draw.textlength(line, font=font)
        x = (W - tw) / 2
        ly = y + i * (line_h + 10)
        draw.rounded_rectangle([x - 28, ly - 12, x + tw + 28, ly + line_h], radius=18, fill="white")
        draw.text((x, ly), line, font=font, fill="black")


def label(img, text):
    """Kleine Kennzeichnung oben links, z. B. 'Werbung | Herstellerbild'."""
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT_MED, 34)
    tw = draw.textlength(text, font=font)
    draw.rounded_rectangle([40, 110, 40 + tw + 40, 170], radius=30, fill=(0, 0, 0, 160))
    draw.text((60, 120), text, font=font, fill="white")


def make_frame(image_path, text, label_text, out_path):
    """Ein Standbild 1080x1920: unscharfer Hintergrund + Produktbild mittig + Text oben."""
    src = Image.open(image_path).convert("RGB")
    # Hintergrund: Bild auf volle Größe ziehen und weichzeichnen
    scale = max(W / src.width, H / src.height)
    bg = src.resize((int(src.width * scale) + 1, int(src.height * scale) + 1))
    bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
    bg = bg.filter(ImageFilter.GaussianBlur(40))
    bg = Image.blend(bg, Image.new("RGB", (W, H), "black"), 0.25)
    # Vordergrund: Bild komplett sichtbar, max. 1000 px breit / 1150 px hoch
    s = min(1000 / src.width, 1150 / src.height)
    fg = src.resize((int(src.width * s), int(src.height * s)))
    bg.paste(fg, ((W - fg.width) // 2, 560 + (1150 - fg.height) // 2))
    img = bg.convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if label_text:
        label(overlay, label_text)
    if text:
        text_box(overlay, text, 250)
    Image.alpha_composite(img, overlay).convert("RGB").save(out_path, quality=95)


def render(video, tmp):
    """Rendert ein Video. Gibt den Ausgabepfad zurück oder None, wenn Bilder fehlen."""
    frames = []
    for i, slide in enumerate(video["slides"]):
        path = find_image(slide["bild"])
        if path is None:
            if slide.get("optional"):
                continue                      # KI-Szene fehlt -> Folie weglassen
            print(f"  ⏭  Video {video['id']}: Bild fehlt: produkte/{slide['bild']}.jpg")
            return None
        f = Path(tmp) / f"{video['id']}_{i}.jpg"
        make_frame(path, slide.get("text", ""), slide.get("label", "Werbung | Herstellerbild"), f)
        frames.append((f, float(slide.get("sek", 3))))

    # Jede Folie mit langsamem Zoom (Ken-Burns-Effekt), dann alle aneinanderhängen
    inputs, filters = [], []
    for i, (f, sek) in enumerate(frames):
        n = int(sek * FPS)
        inputs += ["-i", str(f)]   # ein einzelnes Bild; zoompan macht daraus n Frames
        filters.append(
            f"[{i}:v]scale=1620:2880,zoompan=z='min(zoom+0.0007,1.06)':d={n}"
            f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS},setsar=1[v{i}]"
        )
    concat = "".join(f"[v{i}]" for i in range(len(frames))) + f"concat=n={len(frames)}:v=1:a=0[out]"
    AUSGABE.mkdir(parents=True, exist_ok=True)
    out = AUSGABE / f"{video['id']}_{video['name']}.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", *inputs,
           "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",     # stille Tonspur (für CapCut/TikTok)
           "-filter_complex", ";".join(filters) + ";" + concat,
           "-map", "[out]", "-map", f"{len(frames)}:a", "-shortest",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-c:a", "aac", str(out)]
    subprocess.run(cmd, check=True)
    return out


def main():
    plan = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    only = sys.argv[2] if len(sys.argv) > 2 else None
    with tempfile.TemporaryDirectory() as tmp:
        for video in plan["videos"]:
            if only and video["id"] != only:
                continue
            out = render(video, tmp)
            if out:
                print(f"  ✅ {out}")


if __name__ == "__main__":
    main()
