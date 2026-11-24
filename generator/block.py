"""
Hintergrund "block": Storytime mit selbst gezeichneten Klötzchen-Figuren.
Jede Szene wird im Skript-Kopf beschrieben:

    SZENE 1: strasse | rennt | autos, leute_lachen
             ^Ort      ^was du machst  ^was sonst noch da ist

Orte:     strasse, nacht, park, haus, autohaus, buehne
Aktionen: steht, rennt, traurig, jubelt, springt, traegt, faehrt
Extras:   autos, stau, sportwagen, leute, leute_lachen, lacher, mama, typ, hund, katze,
          pferd, stein, tisch, pokal, jury, regen, konfetti
Jedes gesprochene "Huss" bekommt automatisch einen HUSS!-Effekt (Zoom, Text, Wumms).
"""
import colorsys
import math
import random

import numpy as np
from PIL import Image, ImageDraw

B, H, FPS = 1080, 1920, 30
FUSS_Y = 1650           # wo die Füße der Hauptfigur stehen
GROESSE = 1.25          # Größe der Hauptfigur
SCHWARZ, WEISS, GOLD = (0, 0, 0), (255, 255, 255), (255, 205, 0)

FARBEN = {
    "gelb": (245, 205, 50), "rot": (220, 45, 45), "blau": (40, 90, 220), "gruen": (50, 170, 70),
    "schwarz": (35, 35, 40), "weiss": (240, 240, 240), "orange": (250, 140, 30),
    "lila": (140, 70, 200), "pink": (240, 110, 180), "braun": (120, 75, 40), "grau": (130, 130, 140),
    "hell": (255, 220, 185), "mittel": (225, 170, 120), "dunkel": (140, 90, 60), "tuerkis": (40, 190, 190),
}


def dunkler(f, k=0.7):
    return tuple(int(c * k) for c in f)


def zufallsfarbe(rng):
    r, g, b = colorsys.hsv_to_rgb(rng.random(), rng.uniform(0.5, 0.85), rng.uniform(0.6, 0.95))
    return int(r * 255), int(g * 255), int(b * 255)


# ---------------- Grundformen ----------------
def kloetzchen(d, px, py, w, h, winkel, farbe):
    """Rechteck, das an (px, py) aufgehängt ist und um diesen Punkt gedreht wird (Arm/Bein)."""
    a = math.radians(winkel)
    ecken = [(-w / 2, 0), (w / 2, 0), (w / 2, h), (-w / 2, h)]
    punkte = [(px + x * math.cos(a) - y * math.sin(a), py + x * math.sin(a) + y * math.cos(a))
              for x, y in ecken]
    d.polygon(punkte, fill=farbe, outline=dunkler(farbe), width=4)
    # Endpunkt (Hand/Fuß) zurückgeben, z. B. um etwas festzuhalten
    return px - h * math.sin(a), py + h * math.cos(a)


def gesicht(d, x, y, s, art):
    """x, y = Mitte des Kopfes."""
    for ax in (x - 30 * s, x + 30 * s):
        d.ellipse([ax - 9 * s, y - 28 * s, ax + 9 * s, y - 2 * s], fill=SCHWARZ)
    if art in ("boese", "entschlossen"):
        d.line([x - 48 * s, y - 45 * s, x - 14 * s, y - 32 * s], fill=SCHWARZ, width=int(7 * s))
        d.line([x + 48 * s, y - 45 * s, x + 14 * s, y - 32 * s], fill=SCHWARZ, width=int(7 * s))
    breite = max(3, int(7 * s))
    if art == "froh":
        d.arc([x - 34 * s, y - 10 * s, x + 34 * s, y + 38 * s], 20, 160, fill=SCHWARZ, width=breite)
    elif art == "traurig":
        d.arc([x - 30 * s, y + 18 * s, x + 30 * s, y + 52 * s], 200, 340, fill=SCHWARZ, width=breite)
        d.ellipse([x + 22 * s, y, x + 34 * s, y + 20 * s], fill=(90, 170, 255))      # Träne
    elif art == "offen":          # schnaufen: Huss!
        d.ellipse([x - 16 * s, y + 10 * s, x + 16 * s, y + 44 * s], fill=SCHWARZ)
    elif art == "lachen":
        d.chord([x - 40 * s, y - 2 * s, x + 40 * s, y + 52 * s], 0, 180, fill=SCHWARZ)
        d.chord([x - 26 * s, y + 18 * s, x + 26 * s, y + 52 * s], 0, 180, fill=(220, 60, 70))
    elif art == "boese":
        d.line([x - 25 * s, y + 30 * s, x + 25 * s, y + 30 * s], fill=SCHWARZ, width=breite)
    else:                         # neutral / entschlossen
        d.line([x - 22 * s, y + 28 * s, x + 22 * s, y + 26 * s], fill=SCHWARZ, width=breite)


def heller(f, k=0.35):
    return tuple(int(c + (255 - c) * k) for c in f)


def glied(d, px, py, w, laenge, winkel, abschnitte):
    """Arm/Bein aus mehreren Farb-Abschnitten, aufgehängt an (px, py) und gedreht.
    abschnitte = Liste (von, bis, farbe) als Anteil der Länge (0..1)."""
    a = math.radians(winkel)

    def punkt(x, y):
        return px + x * math.cos(a) - y * math.sin(a), py + x * math.sin(a) + y * math.cos(a)

    for von, bis, farbe in abschnitte:
        ecken = [punkt(-w / 2, von * laenge), punkt(w / 2, von * laenge),
                 punkt(w / 2, bis * laenge), punkt(-w / 2, bis * laenge)]
        d.polygon(ecken, fill=farbe, outline=dunkler(farbe), width=3)
    return punkt(0, laenge)


def figur(d, x, fuss_y, s, farben, arme=(0, 0), beine=(0, 0), mimik="froh", kopf_dreh=0,
          hut="keiner", hutfarbe=(245, 245, 245)):
    """Klötzchen-Figur im Stil klassischer Roblox-Avatare:
    breiter Oberkörper, gleich lange Arme/Beine, kleiner runder Kopf, Ärmel mit Streifen."""
    haut, shirt, hose = farben
    lang = 190 * s                       # Länge von Armen, Beinen und Oberkörper
    huefte = fuss_y - lang
    oben = huefte - lang
    schuh = dunkler(hose, 0.45)
    for seite, winkel in ((-1, beine[0]), (1, beine[1])):
        glied(d, x + seite * 47.5 * s, huefte, 95 * s, lang, winkel,
              [(0, 0.84, hose), (0.84, 1, schuh)])
    # Oberkörper mit Kragen, Schatten-Seite und Gürtel
    d.rectangle([x - 95 * s, oben, x + 95 * s, huefte], fill=shirt, outline=dunkler(shirt), width=3)
    d.rectangle([x + 75 * s, oben + 3, x + 93 * s, huefte - 3], fill=dunkler(shirt, 0.88))
    d.polygon([(x - 32 * s, oben), (x + 32 * s, oben), (x, oben + 40 * s)], fill=dunkler(shirt, 0.72))
    d.rectangle([x - 95 * s, huefte - 16 * s, x + 95 * s, huefte], fill=dunkler(hose, 0.75))
    # Arme: Ärmel mit zwei Streifen, unten Hand
    streifen = heller(shirt, 0.55)
    aermel = [(0, 0.40, shirt), (0.40, 0.46, streifen), (0.46, 0.50, shirt), (0.50, 0.56, streifen),
              (0.56, 0.62, shirt), (0.62, 1, haut)]
    hand_l = glied(d, x - 142.5 * s, oben + 2 * s, 95 * s, lang, arme[0], aermel)
    hand_r = glied(d, x + 142.5 * s, oben + 2 * s, 95 * s, lang, arme[1], aermel)
    # Kopf: kleiner "Zylinder" mit Schattierung
    kw, kh = 118 * s, 112 * s
    kx, ky = x + kopf_dreh * s, oben - 4 * s - kh / 2
    d.rounded_rectangle([kx - kw / 2, ky - kh / 2, kx + kw / 2, ky + kh / 2], radius=int(34 * s),
                        fill=dunkler(haut, 0.85), outline=dunkler(haut, 0.7), width=3)
    d.rounded_rectangle([kx - kw / 2 + 12 * s, ky - kh / 2 + 3, kx + kw / 2 - 18 * s, ky + kh / 2 - 3],
                        radius=int(28 * s), fill=haut)
    gesicht(d, kx, ky + 4 * s, s * 0.72, mimik)
    kopf_oben = ky - kh / 2
    if hut == "cap":
        d.rounded_rectangle([kx - 62 * s, kopf_oben - 30 * s, kx + 62 * s, kopf_oben + 24 * s],
                            radius=int(24 * s), fill=hutfarbe, outline=dunkler(hutfarbe), width=3)
        d.ellipse([kx - 72 * s, kopf_oben + 8 * s, kx + 72 * s, kopf_oben + 34 * s],
                  fill=shirt, outline=dunkler(shirt), width=3)
        kopf_oben -= 30 * s
    elif hut == "haare":
        d.rounded_rectangle([kx - 63 * s, kopf_oben - 16 * s, kx + 63 * s, kopf_oben + 26 * s],
                            radius=int(14 * s), fill=hutfarbe)
        d.rectangle([kx - 63 * s, kopf_oben, kx - 48 * s, ky + 5 * s], fill=hutfarbe)
        d.rectangle([kx + 48 * s, kopf_oben, kx + 63 * s, ky + 5 * s], fill=hutfarbe)
        kopf_oben -= 16 * s
    return {"kopf": (kx, ky), "hand_l": hand_l, "hand_r": hand_r, "oben": kopf_oben}


def totenkopf(d, x, y, r):
    """Kleiner Totenkopf (für Beleidigungen aus dem Nichts)."""
    d.ellipse([x - r, y - r, x + r, y + r * 0.8], fill=WEISS, outline=SCHWARZ, width=6)
    d.rectangle([x - r * 0.55, y + r * 0.5, x + r * 0.55, y + r * 1.15], fill=WEISS, outline=SCHWARZ, width=6)
    for ax in (x - r * 0.42, x + r * 0.42):
        d.ellipse([ax - r * 0.28, y - r * 0.2, ax + r * 0.28, y + r * 0.32], fill=SCHWARZ)
    d.polygon([(x, y + r * 0.35), (x - r * 0.12, y + r * 0.58), (x + r * 0.12, y + r * 0.58)], fill=SCHWARZ)
    for zx in (-0.25, 0, 0.25):
        d.line([x + zx * r, y + r * 0.7, x + zx * r, y + r * 1.15], fill=SCHWARZ, width=5)


def auto(d, x, y, s, farbe, richtung=1, sport=False):
    """y = Unterkante der Räder."""
    hoehe = 70 if sport else 95
    d.rounded_rectangle([x - 160 * s, y - (35 + hoehe) * s, x + 160 * s, y - 35 * s], radius=int(18 * s),
                        fill=farbe, outline=dunkler(farbe), width=4)
    kab_x = x - 20 * s * richtung
    kab_h = 55 if sport else 75
    d.rounded_rectangle([kab_x - 85 * s, y - (35 + hoehe + kab_h) * s, kab_x + 85 * s, y - (30 + hoehe) * s],
                        radius=int(14 * s), fill=farbe, outline=dunkler(farbe), width=4)
    d.rectangle([kab_x - 70 * s, y - (25 + hoehe + kab_h) * s, kab_x + 70 * s, y - (38 + hoehe) * s],
                fill=(170, 220, 250))
    for rx in (x - 95 * s, x + 95 * s):
        d.ellipse([rx - 34 * s, y - 68 * s, rx + 34 * s, y], fill=(25, 25, 25))
        d.ellipse([rx - 14 * s, y - 48 * s, rx + 14 * s, y - 20 * s], fill=(160, 160, 160))
    lx = x + 150 * s * richtung
    d.rectangle([lx - 10 * s, y - (35 + hoehe * 0.8) * s, lx + 10 * s, y - (35 + hoehe * 0.55) * s], fill=(255, 240, 150))


def tier(d, art, x, fuss_y, t, farbe, redet=False):
    s = {"katze": 0.55, "hund": 1.0, "pferd": 1.6}[art]
    bob = abs(math.sin(t * 6)) * 6 * s
    koerper_y = fuss_y - 70 * s - bob
    for bx in (-55, -25, 25, 55):
        d.rectangle([x + bx * s - 12 * s, koerper_y, x + bx * s + 12 * s, fuss_y], fill=dunkler(farbe, 0.85))
    d.rectangle([x - 80 * s, koerper_y - 60 * s, x + 80 * s, koerper_y + 10 * s], fill=farbe, outline=dunkler(farbe), width=3)
    d.line([x - 80 * s, koerper_y - 50 * s, x - 120 * s, koerper_y - 90 * s - math.sin(t * 10) * 15 * s],
           fill=farbe, width=int(14 * s))
    kx, ky = x + 95 * s, koerper_y - 95 * s
    d.rectangle([kx - 45 * s, ky - 40 * s, kx + 45 * s, ky + 40 * s], fill=farbe, outline=dunkler(farbe), width=3)
    ohr = [(kx - 40 * s, ky - 40 * s), (kx - 15 * s, ky - 85 * s if art == "katze" else ky - 60 * s), (kx, ky - 40 * s)]
    d.polygon(ohr, fill=dunkler(farbe, 0.8))
    d.ellipse([kx + 5 * s, ky - 18 * s, kx + 19 * s, ky - 2 * s], fill=SCHWARZ)
    d.ellipse([kx + 30 * s, ky + 5 * s, kx + 46 * s, ky + 18 * s], fill=SCHWARZ)
    if redet and int(t * 8) % 2 == 0:            # Maul auf beim Sprechen
        d.rectangle([kx + 5 * s, ky + 24 * s, kx + 45 * s, ky + 38 * s], fill=SCHWARZ)


def stein(d, x, y, s):
    """Günther. y = Unterkante."""
    pkt = [(x - 90 * s, y), (x - 105 * s, y - 60 * s), (x - 60 * s, y - 115 * s), (x + 20 * s, y - 125 * s),
           (x + 95 * s, y - 85 * s), (x + 100 * s, y - 20 * s), (x + 60 * s, y)]
    d.polygon(pkt, fill=(140, 140, 150), outline=(90, 90, 100), width=5)
    for ax in (x - 30 * s, x + 25 * s):
        d.ellipse([ax - 18 * s, y - 85 * s, ax + 18 * s, y - 49 * s], fill=WEISS, outline=SCHWARZ, width=3)
        d.ellipse([ax - 6 * s, y - 74 * s, ax + 8 * s, y - 60 * s], fill=SCHWARZ)


def pokal(d, x, y, s):
    """y = Unterkante."""
    d.rectangle([x - 55 * s, y - 25 * s, x + 55 * s, y], fill=(120, 80, 30))
    d.rectangle([x - 15 * s, y - 70 * s, x + 15 * s, y - 25 * s], fill=GOLD)
    d.chord([x - 70 * s, y - 210 * s, x + 70 * s, y - 50 * s], 0, 180, fill=GOLD, outline=(190, 140, 0), width=4)
    d.rectangle([x - 70 * s, y - 140 * s, x + 70 * s, y - 130 * s], fill=GOLD)
    for seite in (-1, 1):
        d.arc([x + seite * 70 * s - 30 * s, y - 135 * s, x + seite * 70 * s + 30 * s, y - 85 * s],
              270 if seite > 0 else 90, 90 if seite > 0 else 270, fill=GOLD, width=int(10 * s))


# ---------------- Hintergründe ----------------
def himmel(oben, unten, hoehe=H):
    verlauf = np.linspace(0, 1, hoehe)[:, None]
    farbe = np.array(oben) * (1 - verlauf) + np.array(unten) * verlauf
    return Image.fromarray(np.repeat(farbe[:, None, :], B, axis=1).astype(np.uint8).reshape(hoehe, B, 3))


def hintergrund(ort, rng):
    """Gibt ein B x H Bild zurück. Bei Straße/Nacht/Park ist es nahtlos wiederholbar (zum Scrollen)."""
    nacht = ort == "nacht"
    if ort in ("strasse", "nacht", "park"):
        bild = himmel((20, 25, 70) if nacht else (90, 170, 245), (60, 60, 120) if nacht else (200, 230, 255))
        d = ImageDraw.Draw(bild)
        if nacht:
            for _ in range(70):
                sx, sy = rng.uniform(0, B), rng.uniform(380, 1000)
                d.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=WEISS)
        if ort == "park":
            d.rectangle([0, 1150, B, H], fill=(80, 170, 70))
            for bx in range(60, B, 270):
                d.rectangle([bx - 22, 900, bx + 22, 1200], fill=(110, 70, 35))
                d.rectangle([bx - 110, 730, bx + 110, 930], fill=(40, 130, 50), outline=(30, 100, 40), width=5)
            d.rectangle([0, 1420, B, H], fill=(215, 190, 130))
            return bild
        # Häuserreihe (nahtlos: genau 4 Häuser pro Bildbreite)
        for i in range(4):
            hx = i * B / 4
            top = rng.uniform(620, 900)
            farbe = zufallsfarbe(rng)
            farbe = dunkler(farbe, 0.45) if nacht else farbe
            d.rectangle([hx + 6, top, hx + B / 4 - 6, 1250], fill=farbe, outline=dunkler(farbe), width=5)
            for fy in range(int(top) + 40, 1200, 110):
                for fx in range(int(hx) + 35, int(hx + B / 4) - 60, 80):
                    an = rng.random() < (0.55 if nacht else 0)
                    d.rectangle([fx, fy, fx + 45, fy + 60], fill=(255, 220, 110) if an else (150, 200, 235))
        d.rectangle([0, 1250, B, 1430], fill=(70, 70, 78))
        for sx in range(0, B, 180):
            d.rectangle([sx + 20, 1335, sx + 110, 1345], fill=(240, 210, 60))
        d.rectangle([0, 1430, B, 1450], fill=(200, 200, 205))
        d.rectangle([0, 1450, B, H], fill=(150, 150, 160) if not nacht else (80, 80, 95))
        for sx in range(0, B, 135):
            d.line([sx, 1450, sx, H], fill=(120, 120, 130) if not nacht else (60, 60, 75), width=3)
        if nacht:
            for lx in (135, 675):
                d.rectangle([lx - 8, 1000, lx + 8, 1450], fill=(50, 50, 60))
                d.ellipse([lx - 30, 970, lx + 30, 1020], fill=(255, 240, 160))
        return bild

    if ort == "buehne":
        bild = himmel((40, 10, 60), (90, 30, 110))
        d = ImageDraw.Draw(bild)
        licht = Image.new("RGB", (B, H), (0, 0, 0))
        ld = ImageDraw.Draw(licht)
        for lx in (240, 540, 840):
            ld.polygon([(lx - 30, 380), (lx + 30, 380), (lx + 260, 1500), (lx - 260, 1500)], fill=(255, 240, 180))
        bild = Image.blend(bild, licht, 0.18)
        d = ImageDraw.Draw(bild)
        d.rectangle([0, 1450, B, H], fill=(130, 80, 40))
        for py in range(1450, H, 60):
            d.line([0, py, B, py], fill=(105, 62, 30), width=3)
        for seite in (0, B - 150):
            d.rectangle([seite, 380, seite + 150, 1450], fill=(180, 20, 40))
            for fx in range(seite + 20, seite + 150, 40):
                d.line([fx, 380, fx, 1450], fill=(140, 10, 30), width=6)
        return bild

    # Innenräume: Haus, Autohaus
    wand = (245, 245, 250) if ort == "autohaus" else (240, 200, 150)
    bild = Image.new("RGB", (B, H), wand)
    d = ImageDraw.Draw(bild)
    if ort == "autohaus":
        d.rectangle([60, 450, B - 60, 1250], fill=(170, 215, 245), outline=(120, 120, 130), width=10)
        for fx in range(60, B - 60, 240):
            d.line([fx, 450, fx, 1250], fill=(120, 120, 130), width=8)
        d.rectangle([0, 1350, B, H], fill=(210, 210, 220))
        for fx in range(0, B, 180):
            d.line([fx, 1350, fx, H], fill=(180, 180, 195), width=3)
    else:
        d.rectangle([0, 1380, B, H], fill=(160, 105, 55))
        for py in range(1380, H, 70):
            d.line([0, py, B, py], fill=(130, 85, 45), width=4)
        d.rectangle([90, 600, 400, 950], fill=(150, 210, 250), outline=(255, 255, 255), width=14)
        d.line([245, 600, 245, 950], fill=WEISS, width=10)
        d.rectangle([720, 640, 960, 820], fill=(255, 250, 240), outline=(120, 80, 40), width=10)
        d.ellipse([790, 690, 890, 770], fill=(255, 190, 60))
        d.rectangle([820, 1000, 1000, 1380], fill=(150, 95, 50), outline=(110, 70, 35), width=6)
        d.ellipse([960, 1180, 978, 1198], fill=GOLD)
    return bild


# ---------------- Szene + Film ----------------
class Szene:
    def __init__(self, beschreibung, rng):
        teile = [t.strip().lower() for t in beschreibung.split("|")] + ["", ""]
        self.ort = teile[0] or "strasse"
        self.aktion = teile[1] or "steht"
        self.extras = {e.strip() for e in teile[2].split(",") if e.strip()}
        self.bild = hintergrund(self.ort, rng)
        self.kann_scrollen = self.ort in ("strasse", "nacht", "park")
        self.autos = [(rng.uniform(0, B + 700), rng.uniform(250, 450), zufallsfarbe(rng), spur)
                      for spur in (0, 1) for _ in range(2)]
        self.stau = [zufallsfarbe(rng) for _ in range(5)]
        self.leute = [((rng.choice(["hell", "mittel", "dunkel"])), zufallsfarbe(rng), zufallsfarbe(rng))
                      for _ in range(3)]
        self.leute_hut = [(rng.choice(["cap", "haare", "keiner"]), zufallsfarbe(rng)) for _ in range(3)]
        self.tierfarben = {"hund": rng.choice([(150, 95, 50), (230, 200, 150), (60, 50, 45)]),
                           "katze": rng.choice([(240, 150, 60), (150, 150, 160), (250, 250, 250)]),
                           "pferd": rng.choice([(130, 80, 40), (90, 60, 40), (235, 230, 220)])}
        self.phase = rng.uniform(0, 6.28)


class BlockFilm:
    def __init__(self, kopf, szenen_zeiten, dauer, huss_zeiten, rng, fonts, booms=(), satz_starts=(),
                 sprecher_zeiten=()):
        """szenen_zeiten = Liste (nummer, startzeit). Szenenbeschreibung kommt aus 'szene N' im Kopf."""
        self.fonts = fonts
        werte = [w.strip() for w in kopf.get("figur", "hell, rot, blau").split(",")]
        f = [FARBEN.get(w, FARBEN["gelb"]) for w in werte[:3]]
        self.ich = (f + [FARBEN["hell"], FARBEN["rot"], FARBEN["blau"]])[:3]
        self.ich_hut = werte[3] if len(werte) > 3 else "keiner"          # cap / haare / keiner
        self.ich_hutfarbe = FARBEN.get(werte[4], (245, 245, 245)) if len(werte) > 4 else (245, 245, 245)
        self.szenen = []
        for i, (nr, start) in enumerate(szenen_zeiten):
            ende = szenen_zeiten[i + 1][1] if i + 1 < len(szenen_zeiten) else dauer
            beschr = kopf.get(f"szene {nr}", kopf.get(f"szene{nr}", "strasse | steht"))
            self.szenen.append((Szene(beschr, rng), start, ende))
        self.huss = huss_zeiten
        self.booms = list(booms)
        self.satz_starts = list(satz_starts)
        self.sprecher_zeiten = list(sprecher_zeiten)
        self.wackel = random.Random(7)
        self.konfetti = [(rng.uniform(0, B), rng.uniform(-1500, -20), rng.uniform(350, 750), rng.uniform(0, 6.28),
                          zufallsfarbe(rng)) for _ in range(140)]
        self.regen = [(rng.uniform(0, B), rng.uniform(0, H), rng.uniform(1300, 1800)) for _ in range(120)]

    def _huss_seit(self, zeit):
        """Sekunden seit dem letzten 'Huss' (oder None) + welches Huss es war."""
        for k, t in enumerate(reversed(self.huss)):
            if t <= zeit:
                return zeit - t, len(self.huss) - 1 - k
        return None, 0

    def sound(self, n_samples, sr):
        spur = np.zeros(n_samples, dtype=np.float32)
        rausch = np.random.default_rng(3)
        for t0 in self.huss:
            t = np.arange(int(sr * 0.35)) / sr
            wumms = np.sin(2 * np.pi * (90 - 50 * t) * t) * np.exp(-t * 12)
            zisch = np.convolve(rausch.normal(size=len(t)), np.ones(4) / 4, mode="same") * np.exp(-t * 18) * 0.4
            i = int(t0 * sr)
            stueck = (wumms + zisch)[: max(0, min(len(t), n_samples - i))]
            spur[i:i + len(stueck)] += stueck * 0.45
        for t0 in self.booms:                   # tiefer "BOOM" bei Beleidigungen
            t = np.arange(int(sr * 1.4)) / sr
            boom = np.tanh(2.5 * (np.sin(2 * np.pi * 55 * t) + 0.5 * np.sin(2 * np.pi * 110 * t))) * np.exp(-t * 2.8)
            i = int(t0 * sr)
            stueck = boom[: max(0, min(len(t), n_samples - i))]
            spur[i:i + len(stueck)] += stueck * 0.55
        for _, start, _ in self.szenen[1:]:     # leiser "Wusch" bei Szenenwechsel
            t = np.arange(int(sr * 0.25)) / sr
            wusch = np.convolve(rausch.normal(size=len(t)), np.ones(12) / 12, mode="same") * np.sin(np.pi * t / 0.25)
            i = int(start * sr)
            stueck = wusch[: max(0, min(len(t), n_samples - i))]
            spur[i:i + len(stueck)] += stueck * 0.25
        return spur

    def bild(self, zeit):
        i = 0
        while i + 1 < len(self.szenen) and self.szenen[i + 1][1] <= zeit:
            i += 1
        sz, start, ende = self.szenen[i]
        t = zeit - start
        self._zeit = zeit
        huss_dt, huss_nr = self._huss_seit(zeit)
        boom_dt = next((zeit - b for b in reversed(self.booms) if b <= zeit), None)
        boom_aktiv = boom_dt is not None and boom_dt < 0.9
        huss_aktiv = huss_dt is not None and huss_dt < 0.45

        # Hintergrund (beim Rennen scrollt die Welt nach links)
        tempo = {"rennt": 700, "traegt": 180}.get(sz.aktion, 0) if sz.kann_scrollen else 0
        if tempo:
            off = int(t * tempo) % B
            bild = Image.new("RGB", (B, H))
            bild.paste(sz.bild.crop((off, 0, B, H)), (0, 0))
            bild.paste(sz.bild.crop((0, 0, off, H)), (B - off, 0))
        else:
            bild = sz.bild.copy()
        d = ImageDraw.Draw(bild)
        if sz.ort == "nacht":
            d.ellipse([820, 420, 960, 560], fill=(250, 245, 210))

        # Autos auf der Straße (hinter der Figur)
        if "autos" in sz.extras and sz.ort != "autohaus":
            for x0, v, fb, spur in sz.autos:
                richtung = -1 if spur == 0 else 1
                x = (x0 + richtung * v * t - tempo * t) % (B + 700) - 350
                auto(d, x, 1330 if spur == 0 else 1425, 0.7 if spur == 0 else 0.85, fb, richtung)
        if "autos" in sz.extras and sz.ort == "autohaus":
            for k, ax in enumerate((210, 870)):
                auto(d, ax, 1480, 0.95, sz.stau[k], 1 if k else -1, sport=k == 1)
        if "stau" in sz.extras:
            for k, fb in enumerate(sz.stau):
                wackel = math.sin(t * 20 + k) * 2
                auto(d, 110 + k * 230 + wackel, 1425, 0.7, fb)
                if (int(t * 2) + k) % 4 == 0:
                    d.text((110 + k * 230, 1210), "HUP!", font=self.fonts["klein"], fill=GOLD, anchor="mm",
                           stroke_width=4, stroke_fill=SCHWARZ)

        # Möbel / Gegenstände im Hintergrund
        if "tisch" in sz.extras:
            d.rectangle([150, 1330, 520, 1360], fill=(120, 75, 35))
            for tx in (175, 480):
                d.rectangle([tx, 1360, tx + 18, 1560], fill=(100, 62, 28))
        if "jury" in sz.extras:
            for k in range(3):
                figur(d, 700 + k * 120, 1480, 0.38, self._leute(sz, k),
                      mimik=self._mund("jury", "lachen" if t > 1.5 else "neutral"), **self._hut(sz, k))
            d.rectangle([620, 1400, 1060, 1500], fill=(50, 50, 60), outline=GOLD, width=5)

        # Nebenfiguren
        if "mama" in sz.extras:
            figur(d, 850, FUSS_Y, 0.85, (FARBEN["mittel"], FARBEN["lila"], FARBEN["schwarz"]),
                  arme=(-35, 35), mimik=self._mund("mama", "boese"), hut="haare", hutfarbe=(110, 60, 30))
        if "typ" in sz.extras:                      # random Typ, der aus dem Nichts beleidigt
            redet = self._redet("typ")
            wackel = math.sin(t * 30) * 6 if redet else 0
            figur(d, 870 + wackel, FUSS_Y, 0.85, (FARBEN["dunkel"], FARBEN["rot"], FARBEN["schwarz"]),
                  arme=(150 if redet else 10, -10), mimik=self._mund("typ", "boese" if redet else "froh"),
                  hut="cap", hutfarbe=FARBEN["schwarz"])
        if "lacher" in sz.extras:
            wackel = math.sin(t * 25) * 8
            figur(d, 860 + wackel, FUSS_Y, 0.8, (FARBEN["hell"], FARBEN["schwarz"], FARBEN["grau"]),
                  arme=(150, -20), mimik=self._mund("lacher", "lachen"), hut="cap", hutfarbe=FARBEN["rot"])
            if int(t * 3) % 2 == 0:
                d.text((860, 980), "HAHAHA", font=self.fonts["klein"], fill=WEISS, anchor="mm",
                       stroke_width=5, stroke_fill=SCHWARZ)
        for k, art in enumerate(("leute", "leute_lachen")):
            if art in sz.extras:
                for j, (x, s) in enumerate(((110, 0.6), (970, 0.6))):
                    lacht = art == "leute_lachen"
                    wackel = math.sin(t * 22 + j) * 6 if lacht else math.sin(t * 2 + j) * 3
                    figur(d, x, FUSS_Y + wackel, s, self._leute(sz, j), mimik="lachen" if lacht else "froh",
                          arme=(150 if lacht else 8, -8), **self._hut(sz, j))
                    if lacht and (int(t * 3) + j) % 2 == 0:
                        d.text((x, FUSS_Y - 470), "HAHA", font=self.fonts["klein"], fill=WEISS, anchor="mm",
                               stroke_width=5, stroke_fill=SCHWARZ)
        for k, art in enumerate(("hund", "katze", "pferd")):
            if art in sz.extras:
                tier(d, art, (150, 930, 870)[k] if art != "pferd" else 820, FUSS_Y + 10, t + k, sz.tierfarben[art],
                     redet=self._redet(art))

        # Hauptfigur
        self._hauptfigur(d, sz, t, huss_aktiv)

        # Wetter und Effekte
        if "regen" in sz.extras:
            for rx, ry, v in self.regen:
                yy = (ry + v * t) % H
                d.line([rx, yy, rx - 8, yy + 40], fill=(170, 200, 255), width=3)
        if "konfetti" in sz.extras:
            for kx, ky, v, ph, fb in self.konfetti:
                yy = ky + v * t
                if -30 < yy < H:
                    xx = kx + math.sin(t * 3 + ph) * 40
                    d.rectangle([xx, yy, xx + 14, yy + 22], fill=fb)
        if huss_aktiv:
            self._huss_text(d, huss_dt, huss_nr)
        if t < 0.12 and i > 0:                     # kurzer Blitz beim Szenenwechsel
            bild = Image.blend(bild, Image.new("RGB", (B, H), WEISS), 0.6 * (1 - t / 0.12))
        if boom_aktiv:                              # Beleidigung: Totenkopf + roter Blitz
            r = 95 * (1 + 0.6 * max(0, 1 - boom_dt / 0.12))
            totenkopf(d, 870, 860, r)
            if boom_dt < 0.35:
                bild = Image.blend(bild, Image.new("RGB", (B, H), (200, 0, 0)), 0.35 * (1 - boom_dt / 0.35))

        # Kamera: kleiner Zoom bei jedem neuen Satz, stärker bei Huss und Boom, Wackeln bei Boom
        z, dx, dy = 1.0, 0, 0
        satz_dt = next((zeit - s0 for s0 in reversed(self.satz_starts) if s0 <= zeit), 9)
        if satz_dt < 0.25:
            z = max(z, 1 + 0.045 * (1 - satz_dt / 0.25))
        if huss_aktiv and huss_dt < 0.3:
            z = max(z, 1 + 0.09 * (1 - huss_dt / 0.3))
        if boom_aktiv and boom_dt < 0.5:
            z = max(z, 1 + 0.15 * (1 - boom_dt / 0.5))
            staerke = 28 * (1 - boom_dt / 0.5)
            dx, dy = self.wackel.uniform(-staerke, staerke), self.wackel.uniform(-staerke, staerke)
        if z > 1.001:
            w, h = int(B / z), int(H / z)
            cx, cy = B // 2 + dx, int(FUSS_Y - 420 + dy)
            links, oben = int(max(0, min(B - w, cx - w // 2))), int(max(0, min(H - h, cy - h // 2)))
            bild = bild.crop((links, oben, links + w, oben + h)).resize((B, H))
        return bild

    def _redet(self, name):
        """Spricht diese Figur gerade (laut {name} im Skript)?"""
        return any(w == name and a <= self._zeit < e for w, a, e in self.sprecher_zeiten)

    def _mund(self, name, mimik):
        """Beim Sprechen geht der Mund auf und zu."""
        if self._redet(name) and int(self._zeit * 8) % 2 == 0:
            return "offen"
        return mimik

    def _hut(self, sz, j):
        hut, farbe = sz.leute_hut[j % 3]
        return {"hut": hut, "hutfarbe": farbe}

    def _leute(self, sz, j):
        haut, shirt, hose = sz.leute[j % 3]
        return FARBEN[haut], shirt, hose

    def _hauptfigur(self, d, sz, t, huss):
        a, x, fy = sz.aktion, B / 2, FUSS_Y
        mimik = {"rennt": "entschlossen", "traurig": "traurig", "jubelt": "froh", "traegt": "offen",
                 "steht": "neutral", "springt": "froh", "faehrt": "froh"}.get(a, "neutral")
        if huss:
            mimik = "offen"
        elif any(0 <= self._zeit - b < 0.9 for b in self.booms):
            mimik = "traurig"                       # getroffen von der Beleidigung
        arme, beine, kopf_dreh = (6, -6), (0, 0), 0
        if a == "rennt":
            w = math.sin(t * 16) * 40
            arme, beine = (w, w), (-w * 0.8, w * 0.8)
            fy -= abs(math.sin(t * 16)) * 25
        elif a == "traegt":
            w = math.sin(t * 6) * 15
            arme, beine = (165, -165), (-w, w)
            fy -= abs(math.sin(t * 6)) * 8
        elif a == "jubelt":
            w = math.sin(t * 10) * 15
            arme = (150 + w, -150 - w)
            fy -= abs(math.sin(t * 8)) * 70
        elif a == "springt":
            fy -= abs(math.sin(t * 7)) * 160
            arme = (60, -60)
        elif a == "traurig":
            fy += 6
            arme, kopf_dreh = (3, -3), 0
        else:
            fy -= math.sin(t * 2.5 + sz.phase) * 4      # leichtes Atmen

        if a == "faehrt":
            info = figur(d, x + 30, fy - 120, 0.8, self.ich, arme=(160, -160) if t > 2 else (40, -40), mimik=mimik,
                         hut=self.ich_hut, hutfarbe=self.ich_hutfarbe)
            auto(d, x, FUSS_Y + 40, 1.6, (220, 30, 40), 1, sport=True)
            return
        info = figur(d, x, fy, GROESSE, self.ich, arme, beine, mimik, kopf_dreh,
                     hut=self.ich_hut, hutfarbe=self.ich_hutfarbe)
        if a == "traegt" or "stein" in sz.extras:
            if a == "traegt":
                hx = (info["hand_l"][0] + info["hand_r"][0]) / 2
                stein(d, hx, min(info["hand_l"][1], info["hand_r"][1]) + 30, 1.1)
                for k in range(3):                       # Schweißtropfen
                    sy = (t * 300 + k * 60) % 120
                    d.ellipse([x + 110 + k * 15, info["kopf"][1] - 40 + sy, x + 124 + k * 15,
                               info["kopf"][1] - 18 + sy], fill=(120, 190, 255))
            elif "tisch" in sz.extras:
                stein(d, 335, 1330, 0.9)
            else:
                stein(d, 240, FUSS_Y, 0.8)
        if "pokal" in sz.extras:
            if a == "jubelt":
                hx = (info["hand_l"][0] + info["hand_r"][0]) / 2
                pokal(d, hx, min(info["hand_l"][1], info["hand_r"][1]) + 40, 1.0)
            else:
                pokal(d, 220, FUSS_Y, 1.0)
        if "sportwagen" in sz.extras:
            auto(d, 820, FUSS_Y + 10, 1.0, (220, 30, 40), -1, sport=True)

    def _huss_text(self, d, dt, nr):
        groesse = int(135 * (1 + 0.5 * max(0, 1 - dt / 0.12)))
        font = self.fonts["huss"].font_variant(size=groesse)
        seite = -1 if nr % 2 else 1
        breite = font.getlength("HUSS!") + 30          # nie über den Bildrand
        x = min(max(B / 2 + seite * 180, breite / 2), B - breite / 2)
        y = FUSS_Y - 840 - dt * 120
        d.text((x, y), "HUSS!", font=font, fill=(255, 60, 40), anchor="mm", stroke_width=10, stroke_fill=WEISS)
        for k in range(3):                               # Atemwolken
            r = 25 + dt * 120 + k * 12
            px = B / 2 + seite * (110 + dt * 400 + k * 40)
            py = FUSS_Y - 600 - k * 20
            d.ellipse([px - r, py - r * 0.6, px + r, py + r * 0.6], fill=(235, 240, 255))
