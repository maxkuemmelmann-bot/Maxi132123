"""
Hintergrund "info": ruhige Erklärvideos mit Infokarten.
Jede Szene wird im Skript-Kopf beschrieben:

    SZENE 1: zahl | 231 Min. | pro Tag am Smartphone
    SZENE 2: balken | Mädchen: 233; Jungen: 229 | Minuten pro Tag
    SZENE 3: liste | Punkt eins; Punkt zwei; Punkt drei
    SZENE 4: titel | Große Überschrift | kleine Zeile darunter
    SZENE 5: frage | Wie lange warst du heute am Handy?

Kopfzeilen: KATEGORIE (z. B. NEWS, WISSEN, TECH), QUELLEN (wird am Ende eingeblendet).
Zahlen werden deutsch geschrieben: 18.100 (Tausender-Punkt), 0,9 (Komma).
"""
import math
import re

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

B, H, FPS = 1080, 1920, 30
KARTE = (70, 540, B - 70, 1290)            # Bereich der Infokarte
KARTEN_FARBE = (22, 28, 58)
AKZENTE = [(0, 200, 255), (255, 90, 160), (255, 205, 60), (120, 230, 140)]
WEISS, GRAU = (255, 255, 255), (170, 180, 210)


def weich(x):
    """Sanftes Abbremsen (0..1 -> 0..1)."""
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def zerlege_zahl(text):
    """'knapp 4 Std.' -> ('knapp ', 4.0, ' Std.', 0 Nachkommastellen)."""
    m = re.match(r"^(.*?)(\d[\d.]*(?:,\d+)?)(.*)$", text.strip())
    if not m:
        return text, None, "", 0
    vor, zahl, nach = m.groups()
    nachkomma = len(zahl.split(",")[1]) if "," in zahl else 0
    wert = float(zahl.replace(".", "").replace(",", "."))
    return vor, wert, nach, nachkomma


def schreibe_zahl(wert, nachkomma):
    text = f"{wert:,.{nachkomma}f}"                       # 18,100.0 (englisch)
    return text.replace(",", "X").replace(".", ",").replace("X", ".")   # -> 18.100,0


def umbrechen(text, font, breite):
    """Bricht Text in Zeilen um. Zu lange Wörter mit Bindestrich werden am Bindestrich getrennt."""
    woerter = []
    for w in text.split():
        if font.getlength(w) > breite and "-" in w:
            teile = w.split("-")
            woerter += [t + "-" for t in teile[:-1]] + [teile[-1]]
        else:
            woerter.append(w)
    zeilen, zeile = [], ""
    for w in woerter:
        test = (zeile + " " + w).strip()
        if font.getlength(test) > breite and zeile:
            zeilen.append(zeile)
            zeile = w
        else:
            zeile = test if not zeile.endswith("-") else zeile + w
    return zeilen + [zeile] if zeile else zeilen


def passend(font, zeilen, breite):
    """Macht die Schrift kleiner, falls eine Zeile trotzdem zu breit ist."""
    breiteste = max((font.getlength(z) for z in zeilen), default=0)
    return font if breiteste <= breite else font.font_variant(size=int(font.size * breite / breiteste))


def hintergrund():
    """Dunkelblauer Verlauf mit weichen Farbflächen (wird langsam verschoben)."""
    kb, kh = 340, 600                                     # klein malen, dann weichzeichnen
    klein = Image.new("RGB", (kb, kh), (10, 12, 35))
    d = ImageDraw.Draw(klein)
    for (x, y, r), farbe in zip([(60, 120, 110), (280, 260, 130), (90, 470, 120), (300, 560, 90)],
                                [(30, 60, 160), (110, 30, 120), (0, 90, 130), (60, 30, 140)]):
        d.ellipse([x - r, y - r, x + r, y + r], fill=farbe)
    klein = klein.filter(ImageFilter.GaussianBlur(45))
    return klein.resize((B + 240, H + 300), Image.BICUBIC)


class InfoFilm:
    def __init__(self, kopf, szenen_zeiten, dauer, lade_font):
        self.kategorie = kopf.get("kategorie", "WISSEN").upper()
        self.quellen = kopf.get("quellen", "")
        self.szenen = []
        for i, (nr, start) in enumerate(szenen_zeiten):
            ende = szenen_zeiten[i + 1][1] if i + 1 < len(szenen_zeiten) else dauer
            teile = [t.strip() for t in kopf.get(f"szene {nr}", "titel | ").split("|")] + ["", ""]
            self.szenen.append({"art": teile[0].lower(), "a": teile[1], "b": teile[2],
                                "start": start, "ende": ende, "akzent": AKZENTE[i % len(AKZENTE)]})
        self.hg = hintergrund()
        self.f = {"riesig": lade_font(190), "gross": lade_font(96), "mittel": lade_font(62),
                  "klein": lade_font(46), "mini": lade_font(34)}
        self.dauer = dauer

    # ---------------- Ton ----------------
    def sound(self, n_samples, sr):
        """Leise Hintergrundmusik (weiche Akkorde) + kleine Effekte."""
        t = np.arange(n_samples) / sr
        spur = np.zeros(n_samples, dtype=np.float32)
        akkorde = [(261.6, 329.6, 392.0, 493.9), (220.0, 261.6, 329.6, 392.0),
                   (174.6, 220.0, 261.6, 329.6), (196.0, 246.9, 293.7, 349.2)]   # Cmaj7 Am7 Fmaj7 G7
        laenge = 2.6
        for k in range(int(n_samples / sr / laenge) + 1):
            a, e = int(k * laenge * sr), min(n_samples, int((k + 1) * laenge * sr + 0.6 * sr))
            if a >= n_samples:
                break
            tt = t[a:e] - k * laenge
            huelle = np.minimum(tt / 0.8, 1) * np.exp(-np.maximum(tt - laenge, 0) * 6)
            for f in akkorde[k % 4]:
                spur[a:e] += (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * f * 2.003 * tt)) * huelle
        spur *= 0.012
        for sz in self.szenen[1:]:                  # weiches "Wusch" beim Kartenwechsel
            n = int(sr * 0.3)
            rausch = np.convolve(np.random.default_rng(int(sz["start"] * 10)).normal(size=n),
                                 np.ones(20) / 20, mode="same") * np.sin(np.pi * np.arange(n) / n)
            i = int(sz["start"] * sr)
            stueck = rausch[: max(0, min(n, n_samples - i))]
            spur[i:i + len(stueck)] += stueck * 0.18
        for zeit in self._pop_zeiten():             # "Plopp" wenn etwas erscheint
            n = int(sr * 0.08)
            tt = np.arange(n) / sr
            plopp = np.sin(2 * np.pi * (900 - 3000 * tt) * tt) * np.exp(-tt * 50)
            i = int(zeit * sr)
            stueck = plopp[: max(0, min(n, n_samples - i))]
            spur[i:i + len(stueck)] += stueck * 0.15
        return spur

    def _pop_zeiten(self):
        zeiten = []
        for sz in self.szenen:
            if sz["art"] == "liste":
                punkte = [p for p in sz["a"].split(";") if p.strip()]
                for k in range(len(punkte)):
                    zeiten.append(sz["start"] + self._listen_zeit(sz, k, len(punkte)))
            elif sz["art"] == "zahl":
                zeiten.append(sz["start"] + 0.9)
        return zeiten

    def _listen_zeit(self, sz, k, n):
        return 0.3 + k * (sz["ende"] - sz["start"]) * 0.65 / max(n, 1)

    # ---------------- Bild ----------------
    def bild(self, zeit):
        ox = int(120 + 110 * math.sin(zeit * 0.11))
        oy = int(150 + 140 * math.cos(zeit * 0.07))
        bild = self.hg.crop((ox, oy, ox + B, oy + H))
        d = ImageDraw.Draw(bild)
        # Kategorie-Schild ganz oben
        breite = self.f["mini"].getlength(self.kategorie) + 50
        d.rounded_rectangle([(B - breite) / 2, 110, (B + breite) / 2, 162], radius=26, fill=(255, 60, 90))
        d.text((B / 2, 136), self.kategorie, font=self.f["mini"], fill=WEISS, anchor="mm")

        sz = next((s for s in reversed(self.szenen) if s["start"] <= zeit), self.szenen[0])
        t = zeit - sz["start"]
        dx = int((1 - weich(t / 0.35)) * B * 0.7)        # Karte gleitet von rechts rein
        x0, y0, x1, y1 = KARTE
        d.rounded_rectangle([x0 + dx, y0, x1 + dx, y1], radius=44, fill=KARTEN_FARBE,
                            outline=sz["akzent"], width=5)
        getattr(self, "_" + sz["art"], self._titel)(d, sz, t, dx)
        # Quellen am Ende
        if self.quellen and zeit > self.dauer - 6:
            for k, zeile in enumerate(umbrechen("Quellen: " + self.quellen, self.f["mini"], 900)[:3]):
                d.text((B / 2, 1330 + k * 42), zeile, font=self.f["mini"], fill=GRAU, anchor="mm")
        return bild

    def _titel(self, d, sz, t, dx):
        zeilen = umbrechen(sz["a"], self.f["gross"], 820)[:4]
        font = passend(self.f["gross"], zeilen, 840)
        y = 915 - (len(zeilen) - 1) * 55 - (40 if sz["b"] else 0)
        for k, z in enumerate(zeilen):
            d.text((B / 2 + dx, y + k * 110), z, font=font, fill=WEISS, anchor="mm")
        strich = 260 * weich((t - 0.3) / 0.5)
        unten = y + (len(zeilen) - 1) * 110 + 75
        d.rounded_rectangle([B / 2 - strich + dx, unten, B / 2 + strich + dx, unten + 10], radius=5,
                            fill=sz["akzent"])
        for k, z in enumerate(umbrechen(sz["b"], self.f["klein"], 820)[:2]):
            d.text((B / 2 + dx, unten + 70 + k * 56), z, font=self.f["klein"], fill=GRAU, anchor="mm")

    def _zahl(self, d, sz, t, dx):
        vor, wert, nach, nk = zerlege_zahl(sz["a"])
        if wert is None:
            return self._titel(d, sz, t, dx)
        aktuell = wert * weich(t / 0.9)
        text = vor + schreibe_zahl(aktuell, nk) + nach
        font = self.f["riesig"]
        if font.getlength(text) > 880:
            font = font.font_variant(size=int(190 * 880 / font.getlength(text)))
        puls = 1 + 0.04 * math.sin(max(0, t - 0.9) * 4) if t > 0.9 else 1
        if puls != 1:
            font = font.font_variant(size=int(font.size * puls))
        d.text((B / 2 + dx, 840), text, font=font, fill=sz["akzent"], anchor="mm")
        for k, z in enumerate(umbrechen(sz["b"], self.f["mittel"], 840)[:3]):
            d.text((B / 2 + dx, 1010 + k * 72), z, font=self.f["mittel"], fill=WEISS, anchor="mm")

    def _balken(self, d, sz, t, dx):
        eintraege = []
        for teil in sz["a"].split(";"):
            if ":" in teil:
                name, wert = teil.rsplit(":", 1)
                vor, w, nach, nk = zerlege_zahl(wert)
                if w is not None:
                    eintraege.append((name.strip(), w, nk))
        if not eintraege:
            return self._titel(d, sz, t, dx)
        groesst = max(w for _, w, _ in eintraege) or 1
        abstand = min(170, 560 / len(eintraege))
        y = 900 - abstand * (len(eintraege) - 1) / 2 - 40
        for k, (name, w, nk) in enumerate(eintraege):
            anteil = weich((t - 0.25 - k * 0.18) / 0.8)
            laenge = 700 * w / groesst * anteil
            farbe = AKZENTE[k % len(AKZENTE)]
            yy = y + k * abstand
            d.text((130 + dx, yy - 45), name, font=self.f["klein"], fill=WEISS, anchor="ls")
            d.rounded_rectangle([130 + dx, yy - 25, 130 + dx + max(laenge, 20), yy + 35], radius=18, fill=farbe)
            d.text((150 + dx + max(laenge, 20), yy + 5), schreibe_zahl(w * anteil, nk), font=self.f["mittel"],
                   fill=WEISS, anchor="lm")
        unter = umbrechen(sz["b"], self.f["klein"], 840)[:2]
        for k, z in enumerate(unter):
            d.text((B / 2 + dx, 1225 - (len(unter) - 1 - k) * 50), z, font=self.f["klein"], fill=GRAU, anchor="mm")

    def _liste(self, d, sz, t, dx):
        punkte = [p.strip() for p in sz["a"].split(";") if p.strip()]
        n = len(punkte)
        hoehe = min(190, 640 / max(n, 1))
        y = 915 - hoehe * (n - 1) / 2
        for k, p in enumerate(punkte):
            seit = t - self._listen_zeit(sz, k, n)
            if seit < 0:
                continue
            ex = int((1 - weich(seit / 0.3)) * 120)
            farbe = AKZENTE[k % len(AKZENTE)]
            yy = y + k * hoehe
            d.ellipse([125 + dx + ex, yy - 34, 193 + dx + ex, yy + 34], fill=farbe)
            d.text((159 + dx + ex, yy), str(k + 1), font=self.f["klein"], fill=(10, 12, 35), anchor="mm")
            zeilen = umbrechen(p, self.f["mittel"], 720)[:2]
            for z_nr, z in enumerate(zeilen):
                d.text((225 + dx + ex, yy + (z_nr - (len(zeilen) - 1) / 2) * 68), z, font=self.f["mittel"],
                       fill=WEISS, anchor="lm")

    def _frage(self, d, sz, t, dx):
        r = 110 * (1 + 0.08 * math.sin(t * 3))
        d.ellipse([B / 2 - r + dx, 720 - r, B / 2 + r + dx, 720 + r], fill=sz["akzent"])
        d.text((B / 2 + dx, 722), "?", font=self.f["riesig"], fill=KARTEN_FARBE, anchor="mm")
        for k, z in enumerate(umbrechen(sz["a"], self.f["mittel"], 820)[:3]):
            d.text((B / 2 + dx, 920 + k * 74), z, font=self.f["mittel"], fill=WEISS, anchor="mm")
        if sz["b"]:
            d.text((B / 2 + dx, 1180), sz["b"], font=self.f["klein"], fill=GRAU, anchor="mm")
