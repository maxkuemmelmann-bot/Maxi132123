# Faceless Brainrot-TikTok-Fabrik 🧠💀

Automatische Erstellung von TikTok-Videos (über 1 Minute, 9:16) aus Textskripten.
Den kompletten Plan findest du in **[BUSINESSPLAN.md](BUSINESSPLAN.md)**.

## Was ist drin?
| Ordner/Datei | Inhalt |
|---|---|
| `skripte/` | 10 fertige, selbst geschriebene Geschichten (Teil 1), Hintergrund: Ball-Animation |
| `skripte_obst/` | 6 Obst-Wettkämpfe, bei denen der Underdog gewinnt (Rennen-Animation) |
| `generator/make_video.py` | Macht aus einem Skript ein fertiges Video |
| `generator/rennen.py` | Zeichnet das Obst-Rennen (Früchte mit Gesichtern, Krone, Konfetti) |
| `skripte_block/` | Klötzchen-Storytime im „In dieser Stadt … außer mir. Huss. Huss. Huss.“-Stil, komplett automatisch |
| `generator/block.py` | Zeichnet Klötzchen-Figuren, Städte, Autos, Tiere + HUSS!-Effekt |
| `ki_videos/` | KI-Frucht-Storys: Skript + Ordner für deine Clips |
| `skripte_info/` | Info-Videos zu aktuellen Themen (Infokarten, Frauenstimme, ruhige Musik) |
| `generator/info.py` | Zeichnet die Infokarten: Zahlen, Balken, Listen, Fragen |
| `generator/clips.py` | Schneidet deine Clips passend zur Erzählung zusammen |
| `.github/workflows/videos.yml` | Rendert alle Videos automatisch auf GitHub (mit guter KI-Stimme) |
| `BUSINESSPLAN.md` | Geld verdienen, Rechnung, Posting-Plan, Regeln |

## Videos bekommen (ohne eigenen PC-Aufwand)
**Am einfachsten:** Auf GitHub in den Ordner **`fertige_videos/`** gehen, Video antippen, **Download** (↓) drücken.
GitHub legt jedes fertige Video dort automatisch ab (ca. 5–15 Minuten nach einer Änderung).

**Alternativ als ZIP:**
1. Auf GitHub ins Repo → Tab **Actions** → **Videos erstellen**
2. Neuesten Lauf anklicken (oder **Run workflow** drücken)
3. Unten bei **Artifacts** herunterladen (ZIP): `videos-skripte`, `videos-skripte_obst`, `videos-skripte_block` oder `videos-ki_videos`
4. Darin: `01_toaster.mp4` + `01_toaster_beschreibung.txt` (Text zum Reinkopieren bei TikTok)

**Neues Video?** Neue Datei in `skripte/` oder `skripte_obst/` anlegen → speichern/committen → GitHub rendert automatisch nur die neuen Skripte.

## Klötzchen-Storytime: Vorlage (komplett automatisch)
```
TITEL: In dieser Stadt hat jeder ein Auto, außer mir (Teil 1)
BESCHREIBUNG: Huss. Huss. Huss. #inthistown #huss #fyp
STIL: block
FIGUR: hell, rot, blau                 <- Haut, Shirt, Hose
SZENE 1: strasse | traurig | autos     <- Ort | was du machst | was sonst da ist
SZENE 2: strasse | rennt | autos
---
[1] In dieser Stadt hat jeder ein Auto. Außer mir. Huss. Huss. Huss.
[2] Jeden Morgen renne ich zur Schule ...
```
- **Orte:** strasse, nacht, park, haus, autohaus, buehne
- **Aktionen:** steht, rennt, traurig, jubelt, springt, traegt (Stein), faehrt (Sportwagen)
- **Extras:** autos, stau, sportwagen, leute, leute_lachen, lacher, mama, hund, katze, pferd, stein, tisch, pokal, jury, regen, konfetti
- **Farben:** gelb, rot, blau, gruen, schwarz, weiss, orange, lila, pink, braun, grau, tuerkis, Haut: hell, mittel, dunkel
- Jedes gesprochene **„Huss“** bekommt automatisch einen Effekt: großes HUSS!, Zoom, Wumms-Sound, Atemwolke.

## KI-Frucht-Videos (mit deinen Clips)
Jede Story besteht aus einem Skript und einem Ordner mit gleichem Namen:
```
ki_videos/frucht_01_kiwi.txt          <- Erzähltext mit Szenen [1], [2], ...
ki_videos/frucht_01_kiwi/PROMPTS.md   <- fertige Prompts für jede Szene
ki_videos/frucht_01_kiwi/01.mp4       <- deine Clips (legst du rein)
```
1. **Clips machen:** `PROMPTS.md` in die KI-Video-App kopieren.
2. **Hochladen:** Auf GitHub in den Ordner gehen → **Add file → Upload files** → Clips reinziehen → **Commit changes**. (Max. 25 MB pro Datei.)
3. **Warten:** GitHub baut das Video automatisch, ca. 5 Minuten. Download wie oben (`videos-ki_videos`).

**Gut zu wissen:**
- Fehlt ein Clip, zeigt das Video an der Stelle „SZENE X, Clip fehlt“ und **wie viele Sekunden** der Clip lang sein sollte. So kannst du das Timing vorher testen.
- Zu kurze Clips werden etwas verlangsamt, zu lange gekürzt. Querformat wird hochkant zugeschnitten, deshalb **Wichtiges in die Bildmitte**.
- Clip-Namen: `01.mp4`, `1.mp4` oder `01_kampf.mp4` funktionieren alle (auch `.mov`, `.webm`).

## Obst-Rennen: Vorlage
```
TITEL: Die kleinste Rosine gegen den Weltmeister (Teil 1)
BESCHREIBUNG: Niemand hat an Ronny geglaubt 🍇 #brainrot #obst #underdog #fyp
STIL: rennen
WETTKAMPF: 100 Meter Obst-Sprint
BAHN: laufbahn
TEILNEHMER: Wassermelone Walter, Banane Bianca, Apfel Anton, Rosine Ronny*
---
Text ... [WENDE] Aufholjagd ... [ZIEL] Und Ronny gewinnt. Teil zwei ...
```
- **TEILNEHMER:** 2–5 Früchte. Das erste Wort ist die Frucht, der Rest der Name. Der **Erste ist der Favorit**, der mit **`*`** ist der **Underdog**.
- **Früchte:** Apfel, Orange, Mandarine, Pflaume, Kiwi, Kokosnuss, Tomate, Zitrone, Mango, Wassermelone, Melone, Erdbeere, Banane, Traube, Kirsche, Rosine, Birne, Ananas
- **BAHN:** `laufbahn`, `wasser` oder `rasen`
- **`[WENDE]`** im Text: Hier startet die Aufholjagd des Underdogs. **`[ZIEL]`**: Hier überquert er die Ziellinie (Krone und Konfetti). Die Marker werden nicht vorgelesen.
- Setz `[ZIEL]` kurz vor das Ende, sodass danach noch ein Satz kommt (z. B. „Was danach passiert ist, siehst du in Teil zwei.“).

## Auf dem eigenen PC (optional)
Du brauchst Python 3 und [ffmpeg](https://ffmpeg.org/download.html).
```bash
pip install -r generator/requirements.txt
python generator/make_video.py skripte            # alle Videos
python generator/make_video.py skripte/02_taube.txt --stil chaos
python generator/make_video.py skripte_obst      # alle Obst-Rennen
```
Die Videos landen im Ordner `videos/`.

**Typische Anfängerfehler:**
- `ffmpeg not found` → ffmpeg ist nicht installiert oder nicht im PATH.
- „Kein Text gefunden“ → im Skript fehlt die Zeile `---` vor dem Text.
- „Schreib ca. X Wörter mehr“ → das Skript ist zu kurz für über 1 Minute.
- „Edge-TTS nicht erreichbar“ → die gute Stimme braucht Internet. Notlösung: `--stimme espeak` (Roboterstimme, nicht zum Posten geeignet).
