"""
Hintergrund "clips": deine eigenen Videoclips, eine pro Szene.
(z. B. aus einer KI-Video-App oder aufgenommen in Roblox)

Im Skript markierst du mit [1], [2], [3] ..., wo eine neue Szene beginnt.
Die Clips liegen in einem Ordner mit dem gleichen Namen wie das Skript:
    ki_videos/frucht_01_kiwi.txt       <- Skript
    ki_videos/frucht_01_kiwi/01.mp4    <- Clip für Szene [1]
    ki_videos/frucht_01_kiwi/02.mp4    <- Clip für Szene [2]  ...
Ist ein Clip kürzer als die Szene, wird er etwas verlangsamt (höchstens auf 70 %)
und danach bleibt das letzte Bild stehen. Ist er länger, wird er abgeschnitten.
"""
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw

B, H, FPS = 1080, 1920, 30
BILD_BYTES = B * H * 3
ENDUNGEN = (".mp4", ".mov", ".webm", ".mkv", ".m4v")
MIN_TEMPO = 0.7


def finde_clip(ordner, nr):
    """Sucht z. B. für Szene 3 die Datei 3.mp4, 03.mp4 oder 03_kampf.mp4."""
    if not ordner.is_dir():
        return None
    for datei in sorted(ordner.iterdir()):
        if datei.suffix.lower() in ENDUNGEN:
            nummer = "".join(z for z in datei.stem.split("_")[0] if z.isdigit())
            if nummer and int(nummer) == nr:
                return datei
    return None


def clip_laenge(pfad):
    ausgabe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                              "-of", "csv=p=0", str(pfad)], capture_output=True, text=True).stdout
    try:
        return float(ausgabe.strip())
    except ValueError:
        return 0.0


class ClipFilm:
    def __init__(self, ordner, szenen, dauer, font):
        """szenen = Liste (nummer, startzeit) in Sekunden, nach Zeit sortiert."""
        self.ordner, self.font = Path(ordner), font
        self.szenen = []
        for i, (nr, start) in enumerate(szenen):
            ende = szenen[i + 1][1] if i + 1 < len(szenen) else dauer
            self.szenen.append((nr, start, ende))
        self.aktiv, self.proc, self.letztes = -1, None, None
        fehlen = [nr for nr, _, _ in self.szenen if finde_clip(self.ordner, nr) is None]
        if fehlen:
            print(f"  ACHTUNG: Clips fehlen für Szene {fehlen} in {self.ordner}/ "
                  f"-> Platzhalter (gut zum Testen des Timings)")

    def _platzhalter(self, nr, start, ende):
        bild = Image.new("RGB", (B, H), (35, 35, 50))
        d = ImageDraw.Draw(bild)
        d.text((B / 2, 700), f"SZENE {nr}", font=self.font, fill=(255, 210, 0), anchor="mm")
        klein = self.font.font_variant(size=44)
        d.text((B / 2, 820), f"Clip fehlt: {self.ordner.name}/{nr:02d}.mp4", font=klein,
               fill="white", anchor="mm")
        d.text((B / 2, 890), f"braucht ca. {ende - start:.1f} Sekunden", font=klein,
               fill=(180, 180, 180), anchor="mm")
        return bild

    def _stoppe(self):
        if self.proc:
            self.proc.kill()
            self.proc.wait()
            self.proc = None

    def _starte(self, i):
        self._stoppe()
        nr, start, ende = self.szenen[i]
        clip = finde_clip(self.ordner, nr)
        self.letztes = self._platzhalter(nr, start, ende)   # falls der Clip kaputt ist
        if clip is None:
            return
        laenge, dauer = clip_laenge(clip), ende - start
        tempo = 1.0 if laenge >= dauer else max(laenge / dauer, MIN_TEMPO)
        # Clip auf 9:16 zuschneiden (füllt das Bild, Ränder werden abgeschnitten)
        filter_ = (f"setpts=PTS/{tempo:.4f},scale={B}:{H}:force_original_aspect_ratio=increase,"
                   f"crop={B}:{H},fps={FPS}")
        self.proc = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-i", str(clip), "-an", "-vf", filter_,
             "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
        hinweis = "" if tempo == 1.0 else f", verlangsamt auf {tempo:.0%}"
        if laenge * (1 / tempo) < dauer - 0.2:
            hinweis += f", letztes Bild steht {dauer - laenge / tempo:.1f} s"
        print(f"  Szene {nr}: {clip.name} ({laenge:.1f} s Clip für {dauer:.1f} s{hinweis})")

    def bild(self, zeit):
        """Gibt das Bild für diesen Zeitpunkt zurück (muss der Reihe nach aufgerufen werden)."""
        i = 0
        while i + 1 < len(self.szenen) and self.szenen[i + 1][1] <= zeit:
            i += 1
        if i != self.aktiv:
            self._starte(i)
            self.aktiv = i
        if self.proc:
            daten = self.proc.stdout.read(BILD_BYTES)
            if len(daten) == BILD_BYTES:
                self.letztes = Image.frombytes("RGB", (B, H), daten)
            else:                  # Clip zu Ende -> letztes Bild bleibt stehen
                self._stoppe()
        return self.letztes.copy()
