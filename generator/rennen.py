"""
Hintergrund "Rennen": Früchte mit Gesichtern treten gegeneinander an.
Der Underdog liegt lange hinten, holt ab [WENDE] auf und gewinnt bei [ZIEL].
"""
import math
import random

import numpy as np

B = 1080                     # Videobreite
FPS = 30
START_X, ZIEL_X = 130, 890   # Start- und Ziellinie (rechts Platz für TikTok-Knöpfe)
BAHN_OBEN = 770              # y-Position der ersten Bahn

# Name -> (Form, Farbe). Neue Früchte einfach hier eintragen.
FRUECHTE = {
    "apfel": ("rund", (220, 40, 40)),
    "orange": ("rund", (255, 140, 0)),
    "mandarine": ("rund", (255, 160, 30)),
    "pflaume": ("rund", (110, 40, 140)),
    "kiwi": ("rund", (130, 95, 50)),
    "kokosnuss": ("rund", (110, 70, 40)),
    "tomate": ("rund", (235, 50, 30)),
    "zitrone": ("oval", (250, 225, 40)),
    "mango": ("oval", (255, 175, 40)),
    "wassermelone": ("melone", (40, 150, 60)),
    "melone": ("melone", (40, 150, 60)),
    "erdbeere": ("erdbeere", (230, 30, 60)),
    "banane": ("banane", (250, 215, 50)),
    "traube": ("traube", (130, 60, 170)),
    "weintraube": ("traube", (130, 60, 170)),
    "kirsche": ("kirsche", (200, 0, 30)),
    "rosine": ("rosine", (90, 55, 35)),
    "birne": ("birne", (190, 210, 70)),
    "ananas": ("ananas", (240, 190, 40)),
}

BAHNEN = {   # Bahnfarbe, zweite Farbe (abwechselnd), Linienfarbe
    "laufbahn": ((190, 75, 55), (175, 66, 48), (255, 255, 255)),
    "wasser": ((30, 120, 210), (25, 108, 195), (255, 80, 80)),
    "rasen": ((60, 150, 60), (52, 138, 52), (255, 255, 255)),
}

SCHWARZ, WEISS, GOLD = (0, 0, 0), (255, 255, 255), (255, 210, 0)


def dunkler(farbe, f=0.65):
    return tuple(int(c * f) for c in farbe)


# ---------------- Wer ist wann wo? ----------------
def berechne_positionen(n, underdog, wende, ziel, n_frames, rng):
    """Gibt ein Array [Teilnehmer, Bild] mit dem Fortschritt 0..1 zurück."""
    t = np.arange(n_frames) / FPS
    pos = np.zeros((n, n_frames))
    favorit = 0 if underdog != 0 else 1
    for i in range(n):
        if i == underdog:
            # langsam, kurz fast stehen bleiben, dann Aufholjagd bis ins Ziel
            punkte = [(0, 0), (wende * 0.45, 0.14), (wende * 0.8, 0.17), (wende, 0.22),
                      (ziel, 1.0), (ziel + 99, 1.0)]
        else:
            k = 1.0 if i == favorit else rng.uniform(0.78, 0.92)
            punkte = [(0, 0), (wende * 0.5, 0.45 * k), (wende, 0.72 * k),
                      (ziel, 0.96 * k - (0 if i == favorit else 0.03)),
                      (ziel + rng.uniform(0.8, 2.5), 1.0), (ziel + 99, 1.0)]
        zeiten, werte = zip(*punkte)
        roh = np.interp(t, zeiten, werte)
        # glätten -> sanftes Beschleunigen statt ruckartiger Tempowechsel
        fenster = int(FPS * 0.8)
        gepolstert = np.pad(roh, fenster, mode="edge")
        glatt = np.convolve(gepolstert, np.ones(fenster) / fenster, mode="same")[fenster:-fenster]
        pos[i] = np.clip(glatt, 0, 1)
    pos[underdog][t >= ziel] = 1.0        # Underdog ist pünktlich im Ziel
    return pos


# ---------------- Früchte zeichnen ----------------
def zeichne_gesicht(d, x, y, r, gluecklich, entschlossen):
    """Augen schauen nach rechts (Laufrichtung), Mund je nach Stimmung."""
    for ax in (x - r * 0.32, x + r * 0.32):
        d.ellipse([ax - r * 0.24, y - r * 0.39, ax + r * 0.24, y + r * 0.09], fill=WEISS,
                  outline=SCHWARZ, width=max(2, int(r * 0.05)))
        px = ax + r * 0.08
        d.ellipse([px - r * 0.11, y - r * 0.26, px + r * 0.11, y - r * 0.04], fill=SCHWARZ)
        if entschlossen:   # schräge Augenbrauen
            d.line([ax - r * 0.25, y - r * 0.55, ax + r * 0.22, y - r * 0.42], fill=SCHWARZ,
                   width=max(3, int(r * 0.09)))
    breite = max(3, int(r * 0.08))
    if gluecklich:
        d.chord([x - r * 0.35, y - r * 0.05, x + r * 0.35, y + r * 0.5], 0, 180, fill=SCHWARZ)
    elif entschlossen:
        d.line([x - r * 0.22, y + r * 0.28, x + r * 0.22, y + r * 0.24], fill=SCHWARZ, width=breite)
    else:
        d.arc([x - r * 0.3, y, x + r * 0.3, y + r * 0.35], 20, 160, fill=SCHWARZ, width=breite)


def zeichne_frucht(d, art, x, y, r, gluecklich=False, entschlossen=False):
    form, farbe = FRUECHTE.get(art, ("rund", (200, 200, 200)))
    dunkel = dunkler(farbe)
    gruen, braun = (60, 170, 60), (100, 60, 30)
    gesicht_y, gesicht_r = y, r           # wo das Gesicht sitzt

    if form in ("rund", "oval"):
        rx = r * (1.2 if form == "oval" else 1.0)
        ry = r * (0.88 if form == "oval" else 1.0)
        d.ellipse([x - rx, y - ry, x + rx, y + ry], fill=farbe, outline=dunkel, width=3)
        d.line([x, y - ry, x + r * 0.15, y - ry - r * 0.35], fill=braun, width=max(3, int(r * 0.12)))
        d.ellipse([x + r * 0.15, y - ry - r * 0.4, x + r * 0.6, y - ry - r * 0.15], fill=gruen)
    elif form == "melone":
        d.ellipse([x - r * 1.1, y - r, x + r * 1.1, y + r], fill=farbe)
        for k in (0.35, 0.75):
            d.ellipse([x - r * 1.1 * k, y - r, x + r * 1.1 * k, y + r], outline=dunkler(farbe, 0.6),
                      width=max(3, int(r * 0.1)))
    elif form == "erdbeere":
        d.polygon([(x - r, y - r * 0.35), (x + r, y - r * 0.35), (x, y + r * 1.15)], fill=farbe)
        d.ellipse([x - r, y - r * 0.9, x + r, y + r * 0.2], fill=farbe)
        for sx, sy in ((-0.6, 0.1), (0.6, 0.1), (-0.3, 0.55), (0.3, 0.55), (0, 0.85), (-0.7, -0.4), (0.7, -0.4)):
            d.ellipse([x + sx * r - 3, y + sy * r - 4, x + sx * r + 3, y + sy * r + 4], fill=(255, 230, 120))
        zacken = [(x + dx * r, y - r * (0.85 if i % 2 == 0 else 1.25))
                  for i, dx in enumerate((-0.7, -0.45, -0.2, 0, 0.2, 0.45, 0.7))]
        d.polygon(zacken + [(x + 0.7 * r, y - r * 0.75), (x - 0.7 * r, y - r * 0.75)], fill=gruen)
        gesicht_y = y - r * 0.1
    elif form == "banane":
        d.arc([x - r * 1.4, y - r * 1.9, x + r * 1.4, y + r * 0.9], 25, 155, fill=farbe,
              width=int(r * 0.95))
        for wx in (-1, 1):   # braune Enden
            ex = x + wx * r * 1.22
            d.ellipse([ex - r * 0.12, y - r * 0.15, ex + r * 0.12, y + r * 0.1], fill=braun)
        gesicht_y, gesicht_r = y + r * 0.45, r * 0.8
    elif form == "traube":
        kr = r * 0.42
        for zeile, anzahl in enumerate((3, 2, 1)):
            for i in range(anzahl):
                kx = x + (i - (anzahl - 1) / 2) * kr * 1.8
                ky = y - r * 0.55 + zeile * kr * 1.6
                d.ellipse([kx - kr, ky - kr, kx + kr, ky + kr], fill=farbe, outline=dunkel, width=2)
        d.line([x, y - r * 0.95, x + r * 0.2, y - r * 1.35], fill=braun, width=max(3, int(r * 0.1)))
        gesicht_y, gesicht_r = y - r * 0.2, r * 0.85
    elif form == "kirsche":
        for kx, ky in ((x - r * 0.5, y + r * 0.35), (x + r * 0.45, y + r * 0.3)):
            d.line([kx, ky - r * 0.5, x + r * 0.1, y - r * 1.1], fill=(70, 120, 40), width=max(3, int(r * 0.08)))
            d.ellipse([kx - r * 0.62, ky - r * 0.62, kx + r * 0.62, ky + r * 0.62], fill=farbe,
                      outline=dunkel, width=2)
        x, gesicht_y, gesicht_r = x + r * 0.45, y + r * 0.35, r * 0.6
    elif form == "rosine":
        d.ellipse([x - r * 0.9, y - r * 0.72, x + r * 0.9, y + r * 0.72], fill=farbe,
                  outline=dunkel, width=3)
        for wy in (-0.45, 0.35, 0.55):   # Falten
            d.arc([x - r * 0.7, y + wy * r - r * 0.2, x + r * 0.3, y + wy * r + r * 0.2], 200, 330,
                  fill=dunkel, width=3)
        gesicht_r = r * 0.85
    elif form == "birne":
        d.ellipse([x - r, y - r * 0.6, x + r, y + r * 1.0], fill=farbe)
        d.ellipse([x - r * 0.6, y - r * 1.2, x + r * 0.6, y], fill=farbe)
        d.line([x, y - r * 1.2, x + r * 0.15, y - r * 1.5], fill=braun, width=max(3, int(r * 0.12)))
        gesicht_y = y + r * 0.15
    elif form == "ananas":
        for i in range(-3, 4):   # Blätter
            d.polygon([(x + i * r * 0.15, y - r * 0.9), (x + i * r * 0.35, y - r * 1.75),
                       (x + i * r * 0.15 + r * 0.15, y - r * 0.9)], fill=gruen)
        d.ellipse([x - r * 0.85, y - r * 1.05, x + r * 0.85, y + r * 1.05], fill=farbe, outline=dunkel, width=3)
        for i in range(-2, 3):
            d.line([x + i * r * 0.4 - r * 0.4, y - r * 0.8, x + i * r * 0.4 + r * 0.4, y + r * 0.8],
                   fill=dunkel, width=2)

    zeichne_gesicht(d, x, gesicht_y, gesicht_r, gluecklich, entschlossen)


def zeichne_krone(d, x, y, r):
    s = r * 0.7
    d.polygon([(x - s, y), (x - s, y - s * 0.9), (x - s * 0.5, y - s * 0.4), (x, y - s * 1.1),
               (x + s * 0.5, y - s * 0.4), (x + s, y - s * 0.9), (x + s, y)], fill=GOLD,
              outline=(180, 130, 0), width=3)
    d.ellipse([x - 7, y - s * 0.5 - 7, x + 7, y - s * 0.5 + 7], fill=(230, 30, 60))


# ---------------- Das ganze Rennen ----------------
class Rennen:
    def __init__(self, teilnehmer_text, bahn, wettkampf, wende, ziel, n_frames, rng):
        # "Apfel Anton, Rosine Ronny*" -> Stern = Underdog
        eintraege = [t.strip() for t in (teilnehmer_text or "Apfel, Banane, Wassermelone, Rosine*").split(",")]
        self.namen = [e.rstrip("*").strip() for e in eintraege]
        self.arten = [n.split()[0].lower() for n in self.namen]
        sterne = [i for i, e in enumerate(eintraege) if e.endswith("*")]
        self.underdog = sterne[0] if sterne else len(eintraege) - 1
        self.bahn = BAHNEN.get((bahn or "laufbahn").lower(), BAHNEN["laufbahn"])
        self.wasser = (bahn or "").lower() == "wasser"
        self.wettkampf = wettkampf or "Das große Obstrennen"
        self.ziel = ziel
        n = len(self.namen)
        self.bahn_h = min(200, 800 // n)
        self.pos = berechne_positionen(n, self.underdog, wende, ziel, n_frames, rng)
        self.phase = [rng.uniform(0, 6.28) for _ in range(n)]
        self.konfetti = [(rng.uniform(0, B), rng.uniform(-1400, -20), rng.uniform(350, 750),
                          rng.uniform(0, 6.28), rng.choice([(255, 60, 60), (255, 210, 0), (60, 200, 255),
                                                            (120, 255, 120), (255, 120, 220)]))
                         for _ in range(160)]

    def zeichne(self, d, f, zeit, font_klein, font_name):
        n = len(self.namen)
        # Überschrift über den Bahnen
        d.text((B / 2, BAHN_OBEN - 45), self.wettkampf.upper(), font=font_klein, fill=GOLD,
               anchor="mm", stroke_width=5, stroke_fill=SCHWARZ)
        # Bahnen
        for i in range(n):
            y0 = BAHN_OBEN + i * self.bahn_h
            d.rectangle([0, y0, B, y0 + self.bahn_h], fill=self.bahn[i % 2])
            if self.wasser:   # Leinen aus roten/weißen Kugeln
                for lx in range(0, B, 28):
                    d.ellipse([lx, y0 - 6, lx + 12, y0 + 6], fill=self.bahn[2] if lx // 28 % 2 else WEISS)
            else:
                d.line([0, y0, B, y0], fill=self.bahn[2], width=4)
        unten = BAHN_OBEN + n * self.bahn_h
        d.line([0, unten, B, unten], fill=WEISS, width=4)
        d.line([START_X - 70, BAHN_OBEN, START_X - 70, unten], fill=WEISS, width=6)
        # Ziellinie im Schachbrettmuster
        q = 18
        for row, yy in enumerate(range(BAHN_OBEN, unten, q)):
            for col in range(2):
                fb = WEISS if (row + col) % 2 == 0 else SCHWARZ
                d.rectangle([ZIEL_X + 50 + col * q, yy, ZIEL_X + 50 + (col + 1) * q, min(yy + q, unten)], fill=fb)

        gewonnen = zeit >= self.ziel
        # Teilnehmer (hinterste zuerst zeichnen)
        for i in range(n):
            y0 = BAHN_OBEN + i * self.bahn_h
            p = self.pos[i][f]
            tempo = (p - self.pos[i][max(f - 1, 0)]) * FPS     # Fortschritt pro Sekunde
            x = START_X + p * (ZIEL_X - START_X)
            r = self.bahn_h * 0.36 * (0.9 if i == self.underdog else 1.0)
            # Hüpfen beim Laufen / Schaukeln im Wasser
            if self.wasser:
                hub = math.sin(zeit * 5 + self.phase[i]) * 6
            else:
                hub = -abs(math.sin(zeit * 13 + self.phase[i])) * self.bahn_h * 0.12 * min(1, tempo * 40)
            y = y0 + self.bahn_h * 0.58 + hub
            # Tempo-Striche hinter schnellen Früchten
            if tempo > 0.03:
                for k in range(3):
                    ly = y - r * 0.5 + k * r * 0.5
                    d.line([x - r * 1.4 - 60, ly, x - r * 1.4, ly], fill=WEISS, width=4)
            ist_underdog = i == self.underdog
            zeichne_frucht(d, self.arten[i], x, y, r,
                           gluecklich=(ist_underdog and gewonnen) or (not ist_underdog and not gewonnen),
                           entschlossen=ist_underdog and not gewonnen)
            # Name links in der Bahn
            d.text((14, y0 + 8), self.namen[i], font=font_name, fill=WEISS,
                   stroke_width=3, stroke_fill=SCHWARZ)
            if ist_underdog and gewonnen:
                zeichne_krone(d, x, y - r * 1.2, r * 1.4)
                d.text((x - r * 1.6, y), "SIEGER!", font=font_klein, fill=GOLD, anchor="rm",
                       stroke_width=5, stroke_fill=SCHWARZ)

        # Konfetti nach dem Sieg
        if gewonnen:
            dt = zeit - self.ziel
            for kx, ky, v, ph, fb in self.konfetti:
                yy = ky + v * dt
                if -30 < yy < 1950:
                    xx = kx + math.sin(dt * 3 + ph) * 40
                    d.rectangle([xx, yy, xx + 14, yy + 22], fill=fb)

    def sound(self, n_samples, sr):
        """Startpfiff, Jubel und Siegerfanfare."""
        spur = np.zeros(n_samples, dtype=np.float32)

        def lege(ton, sek, laut):
            i = int(sek * sr)
            stueck = ton[: max(0, min(len(ton), n_samples - i))] * laut
            spur[i:i + len(stueck)] += stueck

        t = np.arange(int(sr * 0.5)) / sr          # Pfiff mit Triller
        lege(np.sin(2 * np.pi * (2300 + 120 * np.sin(2 * np.pi * 30 * t)) * t) * np.exp(-t * 4), 0.2, 0.12)
        for k, freq in enumerate((523, 659, 784, 1047)):   # Fanfare C-E-G-C
            dauer = 0.45 if k == 3 else 0.14
            t = np.arange(int(sr * dauer)) / sr
            ton = (np.sin(2 * np.pi * freq * t) + 0.4 * np.sin(4 * np.pi * freq * t)) * np.exp(-t * 3)
            lege(ton, self.ziel + k * 0.14, 0.12)
        t = np.arange(int(sr * 2.0)) / sr          # Jubel (gefiltertes Rauschen)
        rauschen = np.convolve(np.random.default_rng(1).normal(size=len(t)), np.ones(6) / 6, mode="same")
        lege(rauschen * np.minimum(t * 4, 1) * np.exp(-t * 1.2), self.ziel, 0.05)
        return spur
