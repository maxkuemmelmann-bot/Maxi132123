"""
Brainrot-Video-Generator
------------------------
Macht aus einem Skript (Textdatei) ein fertiges TikTok-Video:
  - Format 9:16 (1080x1920), immer über 1 Minute lang
  - Stimme: Edge-TTS (natürliche Stimme, braucht Internet).
    Ohne Internet bricht das Programm ab (oder: --stimme espeak für Roboterstimme)
  - Hintergrund: selbst berechnete "Ball im Kreis"-Animation
    (komplett selbst gemacht -> keine Urheberrechtsprobleme)
  - Untertitel: große Wörter, das gerade gesprochene Wort ist gelb

Benutzung:
  python generator/make_video.py skripte/01_toaster.txt
  python generator/make_video.py skripte            (alle Skripte im Ordner)
  python generator/make_video.py skripte --stimme espeak
"""
import argparse
import asyncio
import colorsys
import math
import random
import re
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ---------------- Einstellungen ----------------
B, H = 1080, 1920          # Breite, Höhe des Videos
FPS = 30                   # Bilder pro Sekunde
SR = 24000                 # Audio-Samplerate
MIN_SEKUNDEN = 62          # TikTok zahlt nur für Videos ÜBER 1 Minute -> Puffer
START_TEMPO = 10           # Sprechtempo in % (positiv = schneller)
MIN_TEMPO = -8             # langsamer als das klingt komisch
EDGE_STIMME = "de-DE-ConradNeural"
CX, CY, RADIUS = B // 2, 1010, 440   # Kreis-Arena für die Bälle

FONT_PFADE = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]


def lade_font(groesse):
    for pfad in FONT_PFADE:
        if Path(pfad).exists():
            return ImageFont.truetype(pfad, groesse)
    sys.exit("Keine fette Schriftart gefunden. Trag einen Pfad in FONT_PFADE ein.")


# ---------------- 1. Skript lesen ----------------
def lese_skript(pfad):
    """Liest TITEL, BESCHREIBUNG und den Sprechtext (alles nach '---')."""
    titel, beschreibung, text = "", "", []
    im_text = False
    for zeile in Path(pfad).read_text(encoding="utf-8").splitlines():
        if im_text:
            text.append(zeile)
        elif zeile.startswith("TITEL:"):
            titel = zeile[6:].strip()
        elif zeile.startswith("BESCHREIBUNG:"):
            beschreibung = zeile[13:].strip()
        elif zeile.strip() == "---":
            im_text = True
    sprechtext = " ".join(" ".join(text).split())   # Zeilenumbrüche weg
    if not sprechtext:
        sys.exit(f"{pfad}: Kein Text gefunden. Hast du die Zeile '---' vergessen?")
    return titel, beschreibung, sprechtext


def in_saetze(text):
    return [s for s in re.split(r"(?<=[.!?:])\s+", text) if s.strip()]


# ---------------- 2. Stimme erzeugen ----------------
def datei_zu_array(pfad):
    """Wandelt mp3/wav mit ffmpeg in ein Zahlen-Array (mono, SR Hz) um."""
    roh = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(pfad), "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"],
        capture_output=True, check=True).stdout
    return np.frombuffer(roh, dtype=np.int16).astype(np.float32) / 32768


def stille_abschneiden(a, schwelle=0.01):
    laut = np.where(np.abs(a) > schwelle)[0]
    return a[laut[0]:laut[-1] + 1] if len(laut) else a


def tts_edge(satz, pfad, tempo=0):
    import edge_tts   # nur laden, wenn gebraucht
    rate = f"{tempo:+d}%"          # z. B. "+10%" = 10 % schneller, "-5%" = langsamer
    asyncio.run(edge_tts.Communicate(satz, EDGE_STIMME, rate=rate).save(str(pfad)))


def tts_espeak(satz, pfad, tempo=0):
    woerter_pro_min = str(int(160 * (1 + tempo / 100)))
    subprocess.run(["espeak-ng", "-v", "de", "-s", woerter_pro_min, "-w", str(pfad), satz],
                   check=True, capture_output=True)


def sprich(saetze, stimme, tmp, tempo=0):
    """Spricht Satz für Satz. Gibt Audio, Liste (wort, start, ende) und die Stimme zurück."""
    if stimme in ("edge", "auto"):
        try:
            tts_edge("Test.", tmp / "test.mp3")
            stimme = "edge"
        except Exception as fehler:
            if stimme == "edge":     # gute Stimme verlangt -> lieber abbrechen als Roboter
                sys.exit(f"Edge-TTS nicht erreichbar ({fehler}). Internet prüfen!")
            print(f"  Edge-TTS nicht erreichbar ({type(fehler).__name__}) -> nutze espeak-ng")
            stimme = "espeak"
    print(f"  Stimme: {stimme}")

    teile, woerter, t = [], [], 0.0
    pause = np.zeros(int(SR * 0.12), dtype=np.float32)
    for i, satz in enumerate(saetze):
        datei = tmp / f"satz{i}.{'mp3' if stimme == 'edge' else 'wav'}"
        tts_edge(satz, datei, tempo) if stimme == "edge" else tts_espeak(satz, datei, tempo)
        audio = stille_abschneiden(datei_zu_array(datei))
        dauer = len(audio) / SR
        # Wörter nach ihrer Länge über den Satz verteilen (lange Wörter = mehr Zeit)
        ws = satz.split()
        gewichte = [len(w) + 2 for w in ws]
        start = t
        for w, g in zip(ws, gewichte):
            laenge = dauer * g / sum(gewichte)
            woerter.append((w, start, start + laenge))
            start += laenge
        teile += [audio, pause]
        t += dauer + len(pause) / SR
    return np.concatenate(teile), woerter, stimme


# ---------------- 3. Ball-Physik ----------------
class Ball:
    def __init__(self, rng, r):
        self.x, self.y = CX + rng.uniform(-100, 100), CY - 150
        self.vx, self.vy = rng.uniform(-500, 500), rng.uniform(-200, 0)
        self.r, self.farbe = r, rng.random()   # farbe = Farbton (0..1)


def simuliere(n_frames, stil, rng):
    """Berechnet für jedes Bild die Ball-Positionen. Gibt auch die Aufprall-Zeiten zurück."""
    baelle = [Ball(rng, 30)] if stil == "wachsen" else [Ball(rng, 38) for _ in range(4)]
    schritte = 4                       # Unterschritte pro Bild -> stabilere Physik
    dt, schwerkraft = 1 / (FPS * schritte), 1500
    bilder, aufpralle = [], []
    for f in range(n_frames):
        for s in range(schritte):
            for b in baelle:
                b.vy += schwerkraft * dt
                b.x += b.vx * dt
                b.y += b.vy * dt
                dx, dy = b.x - CX, b.y - CY
                abstand = math.hypot(dx, dy) or 1
                if abstand + b.r < RADIUS:
                    continue
                # Ball berührt den Rand: zurückschieben und abprallen lassen
                nx, ny = dx / abstand, dy / abstand
                b.x, b.y = CX + nx * (RADIUS - b.r), CY + ny * (RADIUS - b.r)
                punkt = b.vx * nx + b.vy * ny
                if punkt <= 0:
                    continue
                b.vx -= 2 * punkt * nx
                b.vy -= 2 * punkt * ny
                # leicht zufällig drehen + Tempo im guten Bereich halten
                winkel = rng.uniform(-0.15, 0.15)
                b.vx, b.vy = (b.vx * math.cos(winkel) - b.vy * math.sin(winkel),
                              b.vx * math.sin(winkel) + b.vy * math.cos(winkel))
                tempo = math.hypot(b.vx, b.vy)
                ziel = min(max(tempo, 1100), 2000)
                b.vx, b.vy = b.vx / tempo * ziel, b.vy / tempo * ziel
                b.farbe = (b.farbe + 0.06) % 1
                aufpralle.append(((f + s / schritte) / FPS, b.farbe))
                if stil == "wachsen":
                    b.r += 5
                    if b.r > RADIUS * 0.8:       # zu groß -> "Plopp", wieder klein
                        b.r = 30
                        b.x, b.y = CX, CY - 150
        bilder.append([(b.x, b.y, b.r, b.farbe) for b in baelle])
    return bilder, aufpralle


def farbe(farbton, hell=1.0):
    r, g, b = colorsys.hsv_to_rgb(farbton, 0.85, hell)
    return int(r * 255), int(g * 255), int(b * 255)


# ---------------- 4. Untertitel ----------------
def gruppiere(woerter, font, max_breite=960, max_woerter=3):
    """Packt 1-3 Wörter zu einer Untertitel-Zeile zusammen."""
    gruppen, aktuell = [], []
    for i, (w, _, _) in enumerate(woerter):
        test = " ".join(woerter[j][0] for j in aktuell + [i]).upper()
        if aktuell and (len(aktuell) == max_woerter or font.getlength(test) > max_breite):
            gruppen.append(aktuell)
            aktuell = []
        aktuell.append(i)
        if w[-1] in ".!?:":             # nach Satzende neue Zeile
            gruppen.append(aktuell)
            aktuell = []
    if aktuell:
        gruppen.append(aktuell)
    return gruppen


def zeichne_text_mittig(draw, teile, font, y, max_breite=1000):
    """teile = Liste (text, farbe). Zeichnet sie nebeneinander, zentriert."""
    leer = font.getlength(" ")
    breite = sum(font.getlength(t) for t, _ in teile) + leer * (len(teile) - 1)
    if breite > max_breite:            # zu breit (sehr langes Wort) -> Schrift kleiner
        font = font.font_variant(size=int(font.size * max_breite / breite))
        leer = font.getlength(" ")
        breite = sum(font.getlength(t) for t, _ in teile) + leer * (len(teile) - 1)
    x = (B - breite) / 2
    for t, f in teile:
        draw.text((x, y), t, font=font, fill=f, stroke_width=9, stroke_fill="black", anchor="lm")
        x += font.getlength(t) + leer


def zeichne_titel(draw, titel, font):
    """Weißer Kasten oben mit schwarzer Schrift (klassischer TikTok-Look)."""
    zeilen, zeile = [], ""
    # "Teil 1" soll zusammen bleiben (geschütztes Leerzeichen)
    for w in titel.replace("Teil ", "Teil\u00a0").split(" "):
        test = (zeile + " " + w).strip()
        if font.getlength(test) > 940 and zeile:
            zeilen.append(zeile)
            zeile = w
        else:
            zeile = test
    zeilen.append(zeile)
    zh = 74
    oben = 190
    breite = max(font.getlength(z) for z in zeilen) + 60
    draw.rounded_rectangle([(B - breite) / 2, oben, (B + breite) / 2, oben + zh * len(zeilen) + 30],
                           radius=24, fill="white")
    for i, z in enumerate(zeilen):
        draw.text((B / 2, oben + 15 + zh * i + zh / 2), z, font=font, fill="black", anchor="mm")


# ---------------- 5. Alles zusammenbauen ----------------
def aufprall_sound(aufpralle, n_samples):
    """Kurze 'Pling'-Töne bei jedem Aufprall (Tonhöhe je nach Ballfarbe)."""
    spur = np.zeros(n_samples, dtype=np.float32)
    t = np.arange(int(SR * 0.09)) / SR
    letzter = -1
    for zeit, farbton in aufpralle:
        if zeit - letzter < 0.06:      # nicht zu viele Töne auf einmal
            continue
        letzter = zeit
        ton = np.sin(2 * np.pi * (500 + farbton * 700) * t) * np.exp(-t * 45)
        i = int(zeit * SR)
        stueck = ton[: max(0, min(len(ton), n_samples - i))]
        spur[i:i + len(stueck)] += stueck
    return spur * 0.12


def speichere_wav(pfad, audio):
    audio = np.clip(audio, -1, 1)
    with wave.open(str(pfad), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((audio * 32767).astype(np.int16).tobytes())


def mache_video(skript, ausgabe_ordner, stimme, stil):
    titel, beschreibung, text = lese_skript(skript)
    print(f"\n>> {skript.name}: {titel}")
    rng = random.Random(skript.name)          # gleiches Skript -> gleiche Animation
    stil = stil or rng.choice(["wachsen", "chaos"])

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        # Erst zügig sprechen (Brainrot = schnell). Ist es zu kurz für über 1 Minute,
        # wird das Tempo automatisch so weit gesenkt, dass es passt (höchstens auf -8 %).
        tempo = START_TEMPO
        saetze = in_saetze(text)
        stimme_audio, woerter, stimme = sprich(saetze, stimme, tmp, tempo)
        sprech_dauer = len(stimme_audio) / SR
        ziel_dauer = MIN_SEKUNDEN - 1
        if sprech_dauer < ziel_dauer:
            noetig = math.floor(((1 + tempo / 100) * sprech_dauer / ziel_dauer - 1) * 100)
            if noetig >= MIN_TEMPO:
                print(f"  {sprech_dauer:.1f} s ist zu kurz -> spreche mit Tempo {noetig:+d} %")
                tempo = noetig
                stimme_audio, woerter, stimme = sprich(saetze, stimme, tmp, tempo)
                sprech_dauer = len(stimme_audio) / SR
        print(f"  Sprechdauer: {sprech_dauer:.1f} s (Tempo {tempo:+d} %)")
        if sprech_dauer < MIN_SEKUNDEN - 4:
            fehlen = math.ceil((MIN_SEKUNDEN - sprech_dauer) * 3)
            print(f"  FEHLER: Text zu kurz für über 1 Minute. Schreib ca. {fehlen} Wörter mehr.")
            return None
        dauer = max(MIN_SEKUNDEN, sprech_dauer + 1.5)
        n_frames = int(dauer * FPS)
        n_samples = int(n_frames / FPS * SR)

        # Audio: Stimme + Aufprall-Töne
        bilder, aufpralle = simuliere(n_frames, stil, rng)
        stimme_audio = stimme_audio / (np.abs(stimme_audio).max() + 1e-6) * 0.9
        audio = np.zeros(n_samples, dtype=np.float32)
        audio[: len(stimme_audio)] = stimme_audio[:n_samples]
        audio += aufprall_sound(aufpralle, n_samples)
        speichere_wav(tmp / "audio.wav", audio)

        ausgabe_ordner.mkdir(parents=True, exist_ok=True)
        ziel = ausgabe_ordner / (skript.stem + ".mp4")
        ffmpeg = subprocess.Popen(
            ["ffmpeg", "-y", "-v", "error",
             "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{B}x{H}", "-r", str(FPS), "-i", "-",
             "-i", str(tmp / "audio.wav"),
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", str(ziel)],
            stdin=subprocess.PIPE)

        font_unter = lade_font(100)
        font_titel = lade_font(56)
        gruppen = gruppiere(woerter, font_unter)
        g = 0                              # Index der aktuellen Untertitel-Gruppe
        spur = 10                          # Länge der Ball-Spur in Bildern

        for f in range(n_frames):
            zeit = f / FPS
            bild = Image.new("RGB", (B, H), (10, 10, 20))
            d = ImageDraw.Draw(bild)
            # Kreis-Arena mit wechselnder Farbe
            d.ellipse([CX - RADIUS - 8, CY - RADIUS - 8, CX + RADIUS + 8, CY + RADIUS + 8],
                      outline=farbe(zeit * 0.05 % 1), width=10)
            # Ball-Spur (ältere Positionen dunkler) und Bälle
            for k in range(spur, -1, -1):
                if f - k < 0:
                    continue
                for x, y, r, fb in bilder[f - k]:
                    d.ellipse([x - r, y - r, x + r, y + r], fill=farbe(fb, 1 - k / (spur + 2)),
                              outline="white" if k == 0 else None, width=4)
            # Titel oben
            if titel:
                zeichne_titel(d, titel, font_titel)
            # Untertitel
            if zeit < sprech_dauer:
                while g < len(gruppen) - 1 and woerter[gruppen[g + 1][0]][1] <= zeit:
                    g += 1
                teile = [(woerter[i][0].upper(),
                          (255, 230, 0) if woerter[i][1] <= zeit < woerter[i][2] else "white")
                         for i in gruppen[g]]
                zeichne_text_mittig(d, teile, font_unter, CY)
            else:
                zeichne_text_mittig(d, [("FOLG FÜR", (255, 230, 0))], font_unter, CY - 60)
                zeichne_text_mittig(d, [("TEIL 2!", (255, 230, 0))], font_unter, CY + 60)
            ffmpeg.stdin.write(bild.tobytes())
            if f % (FPS * 10) == 0:
                print(f"  rendere ... {zeit:.0f}/{dauer:.0f} s")

        ffmpeg.stdin.close()
        ffmpeg.wait()

    # Beschreibung zum Kopieren für TikTok
    (ausgabe_ordner / (skript.stem + "_beschreibung.txt")).write_text(
        beschreibung + "\n", encoding="utf-8")
    print(f"  fertig: {ziel} ({dauer:.0f} s)")
    return ziel


def main():
    p = argparse.ArgumentParser(description="Macht Brainrot-TikToks aus Textskripten.")
    p.add_argument("pfad", help="Skript-Datei (.txt) oder Ordner mit Skripten")
    p.add_argument("--out", default="videos", help="Ausgabe-Ordner (Standard: videos)")
    p.add_argument("--stimme", choices=["edge", "espeak", "auto"], default="edge",
                   help="edge = gute Stimme (Internet nötig), espeak = Roboter, auto = edge oder Roboter")
    p.add_argument("--stil", choices=["wachsen", "chaos"], help="Hintergrund (sonst zufällig)")
    args = p.parse_args()

    pfad = Path(args.pfad)
    skripte = sorted(pfad.glob("*.txt")) if pfad.is_dir() else [pfad]
    fehler = 0
    for s in skripte:
        if mache_video(s, Path(args.out), args.stimme, args.stil) is None:
            fehler += 1
    print(f"\nFertig: {len(skripte) - fehler} Videos, {fehler} Fehler.")
    sys.exit(1 if fehler else 0)


if __name__ == "__main__":
    main()
