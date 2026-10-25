# Close-Transkription über GitHub (kostenlos)

1. Auf github.com einloggen, oben rechts „+“ → „New repository“. Name: close-transkript. Sichtbarkeit: **Public** (dann sind die Server-Minuten unbegrenzt gratis; im Projekt stehen keine Kundendaten, die Transkripte landen nur in Close). „Create repository“.
2. Auf der neuen Seite „uploading an existing file“ anklicken und den kompletten Inhalt dieses Ordners hineinziehen (auch den Ordner .github). „Commit changes“.
3. In Close: Settings → Developer → API Keys → neuen Schlüssel erstellen und kopieren.
4. In GitHub im Projekt: Settings → Secrets and variables → Actions → „New repository secret“. Name: CLOSE_API_KEY, Wert: den Schlüssel einfügen. Speichern.
5. Test: Reiter „Actions“ → „Close-Anrufe transkribieren“ → „Run workflow“. Nach ein paar Minuten liegen bei den Anrufen der letzten 3 Stunden Notizen „TRANSKRIPT …“ in Close.

Danach läuft es von allein stündlich von ca. 8:40 bis 21:40 Uhr deutscher Zeit. Der Claude-Agent „Anwahl-Analyse Close“ liest die Notizen und schickt dir stündlich den Report.
