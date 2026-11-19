# Faceless Brainrot-TikTok-Fabrik 🧠💀

Automatische Erstellung von TikTok-Videos (über 1 Minute, 9:16) aus Textskripten.
Den kompletten Plan findest du in **[BUSINESSPLAN.md](BUSINESSPLAN.md)**.

## Was ist drin?
| Ordner/Datei | Inhalt |
|---|---|
| `skripte/` | 10 fertige, selbst geschriebene Geschichten (Teil 1) |
| `generator/make_video.py` | Macht aus einem Skript ein fertiges Video |
| `.github/workflows/videos.yml` | Rendert alle Videos automatisch auf GitHub (mit guter KI-Stimme) |
| `BUSINESSPLAN.md` | Geld verdienen, Rechnung, Posting-Plan, Regeln |

## Videos bekommen (ohne eigenen PC-Aufwand)
1. Auf GitHub ins Repo → Tab **Actions** → **Videos erstellen**
2. Neuesten Lauf anklicken (oder **Run workflow** drücken)
3. Unten bei **Artifacts** → `tiktok-videos` herunterladen (ZIP)
4. Darin: `01_toaster.mp4` + `01_toaster_beschreibung.txt` (Text zum Reinkopieren bei TikTok)

**Neues Video?** Neue Datei in `skripte/` anlegen (Vorlage im Businessplan) → speichern/committen → GitHub rendert automatisch.

## Auf dem eigenen PC (optional)
Du brauchst Python 3 und [ffmpeg](https://ffmpeg.org/download.html).
```bash
pip install -r generator/requirements.txt
python generator/make_video.py skripte            # alle Videos
python generator/make_video.py skripte/02_taube.txt --stil chaos
```
Die Videos landen im Ordner `videos/`.

**Typische Anfängerfehler:**
- `ffmpeg not found` → ffmpeg ist nicht installiert oder nicht im PATH.
- „Kein Text gefunden“ → im Skript fehlt die Zeile `---` vor dem Text.
- „Schreib ca. X Wörter mehr“ → das Skript ist zu kurz für über 1 Minute.
- Roboterstimme → Edge-TTS braucht Internet; ohne Internet nimmt das Programm espeak-ng.
