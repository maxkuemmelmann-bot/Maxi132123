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
| `.github/workflows/videos.yml` | Rendert alle Videos automatisch auf GitHub (mit guter KI-Stimme) |
| `BUSINESSPLAN.md` | Geld verdienen, Rechnung, Posting-Plan, Regeln |

## Videos bekommen (ohne eigenen PC-Aufwand)
1. Auf GitHub ins Repo → Tab **Actions** → **Videos erstellen**
2. Neuesten Lauf anklicken (oder **Run workflow** drücken)
3. Unten bei **Artifacts** herunterladen (ZIP): `videos-skripte` oder `videos-skripte_obst`
4. Darin: `01_toaster.mp4` + `01_toaster_beschreibung.txt` (Text zum Reinkopieren bei TikTok)

**Neues Video?** Neue Datei in `skripte/` oder `skripte_obst/` anlegen → speichern/committen → GitHub rendert automatisch nur die neuen Skripte.

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
