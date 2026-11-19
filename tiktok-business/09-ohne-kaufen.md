# 09 – Ohne Produkte kaufen: Videos aus Produktbildern

**So läuft es jetzt:**
1. Du schickst mir die Produktbilder.
2. Ich rendere daraus fertige Videos (MP4, 9:16, mit Zoom, Texten und Kennzeichnung).
3. Du fügst in TikTok einen Sound hinzu, verlinkst das Produkt und postest.

Das Tool liegt in `video-tool/`, die 21 Videos der Woche 1 stehen in `video-tool/woche1.json`.

---

## 🔴 Das brauche ich von dir

### 1. Bilder für die 5 Startprodukte
Für jedes Produkt **3 Bilder** aus dem TikTok-Shop-Eintrag (oder von der Händler-Website):

| Datei | Was drauf sein soll |
|---|---|
| `1.jpg` | **Hauptbild**: Produkt gut erkennbar |
| `2.jpg` | **Anwendung**: Produkt im Einsatz |
| `3.jpg` | **Ergebnis/Detail**: z. B. Vorher/Nachher vom Hersteller oder Detailbild |
| `problem.jpg` *(optional)* | KI-Bild vom Problem (z. B. dreckiger Ofen). Machst du mit ChatGPT-Bilder o. Ä., Prompts in `06-ki-workflow.md`. Ohne dieses Bild wird die Folie einfach weggelassen. |

**Produkte und Ordnernamen:**

| Produkt | Ordner |
|---|---|
| Backofen-Reinigungsgel | `produkte/backofengel/` |
| Fugenreiniger-Stift | `produkte/fugenstift/` |
| Fusselrasierer | `produkte/fusselrasierer/` |
| Abfluss-Haarfänger | `produkte/haarfaenger/` |
| Mini-Akku-Handstaubsauger | `produkte/minisauger/` |

**So bekommst du die Bilder:**
- Im Shop-Eintrag auf das Produktbild tippen (Vollbild) → Screenshot. Möglichst wenig App-Oberfläche mit drauf.
- Oder auf der Website des Händlers „Bild speichern“.

**So schickst du sie mir (eine Möglichkeit reicht):**
- **A)** Hier im Chat hochladen und dazuschreiben, welches Bild welches ist (z. B. „Backofengel 1“).
- **B)** In der GitHub-App/Website in diesem Repo in den passenden Ordner unter `tiktok-business/produkte/` hochladen („Add file → Upload files“) und mir Bescheid sagen.

### 2. Erlaubnis vom Händler (wichtig!)
Produktbilder sind **urheberrechtlich geschützt**. Hol dir vorher eine kurze Erlaubnis. Das ist in 2 Minuten erledigt. Antwort als Screenshot speichern.

> **Nachricht an den Händler** (im TikTok-Shop-Affiliate-Chat):
>
> Hallo! Ich betreibe einen TikTok-Kanal zu Haushalts-Gadgets und möchte euer Produkt „[PRODUKTNAME]“ als Affiliate bewerben. Darf ich dafür eure Produktbilder und -videos in meinen TikTok-Videos verwenden? Die Videos sind als Werbung gekennzeichnet, und eure Bilder werden als „Herstellerbild“ markiert. Falls ihr zusätzliches Video-Material habt, nehme ich das gerne. Vielen Dank!

**Bonus-Nachricht** (sobald du Verkäufe hast):
> Hallo! Mit meinen Videos zu „[PRODUKT]“ habe ich in den letzten 7 Tagen [X] Verkäufe gemacht. Ich würde gerne mehr Videos dazu machen. Wäre eine höhere Provision (z. B. [Y] %) oder eine gezielte Kooperation möglich?

---

## Was sich durch „ohne kaufen“ ändert (ehrlich)

| Punkt | Was das heißt |
|---|---|
| **Keine Test-Aussagen** | Du hast das Produkt nicht benutzt. Also nie „ich habe getestet“ oder „bei mir funktioniert es“. Die Texte in `woche1.json` sind schon so formuliert. |
| **Herstellerbilder kennzeichnen** | Jede Folie zeigt oben „Werbung \| Herstellerbild“. Ergebnis-Bilder heißen „Ergebnis laut Hersteller“. |
| **Niedrigere Kaufquote** | Reine Bild-Videos verkaufen vermutlich schlechter als echte Vorführungen. Rechne eher mit 0,05 % statt 0,1 % (geschätzt). Gegenmittel: viele Videos, gute Hooks, Gewinner schnell erkennen. |
| **Reichweiten-Risiko** | Viele Accounts posten dieselben Herstellerbilder. TikTok kann solche Inhalte als „nicht originell“ einstufen und weniger ausspielen. Gegenmittel: eigene Texte, eigene KI-Problem-Szenen, Formate abwechseln. |
| **Später upgraden** | Sobald ein Produkt verkauft, lohnt es sich, es als **Gratis-Muster** anzufragen und 5 echte Clips zu filmen. Das kostet dich nichts und erhöht die Kaufquote. |

**Neue Rechnung für 1.000 €/Tag** bei 0,05 % Kaufquote und 3 € pro Verkauf: 334 Verkäufe ÷ 0,05 % = **ca. 670.000 Aufrufe pro Tag**. Deshalb lohnt sich der Wechsel auf echte Clips (Muster), sobald ein Produkt Verkäufe bringt.

---

## Ablauf, sobald die Bilder da sind
1. Ich lege die Bilder in die Ordner und rendere alle 21 Videos (ca. 2 Minuten).
2. Ich schicke dir die MP4s hier im Chat.
3. Du postest jeden Tag nach Plan. Pro Video:
   - [ ] Video hochladen
   - [ ] **Sound hinzufügen** (TikTok-Bibliothek, für Business-Konten die „Commercial Music Library“)
   - [ ] **Caption** aus `woche1.json` (Feld `caption`) einfügen
   - [ ] **Produkt verlinken** (sobald der Shop freigeschaltet ist)
   - [ ] **KI-Label** aktivieren, wenn eine KI-Szene (`problem.jpg`) im Video ist
4. Zahlen in `tracker.xlsx` eintragen und mir nach einer Woche schicken.

**Optional KI-Stimme:** In CapCut „Text-to-Speech“ auf die Texte der Folien anwenden. Mit Stimme verkaufen Videos meist besser als nur mit Musik, das ist aber kein Muss.
