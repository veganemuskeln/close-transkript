#!/usr/bin/env python3
"""Transkribiert Close-Anrufe ab 20 Sekunden kostenlos (faster-whisper)
und legt das Transkript als Notiz beim Lead ab: "TRANSKRIPT acti_...".
Läuft stündlich über GitHub Actions. Braucht das Secret CLOSE_API_KEY.
"""
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone

import requests
from faster_whisper import WhisperModel

API = "https://api.close.com/api/v1"
AUTH = (os.environ["CLOSE_API_KEY"].strip(), "")
MIN_SEC = 20
LOOKBACK_H = int(os.environ.get("LOOKBACK_H", "3"))
MODEL = os.environ.get("WHISPER_MODEL", "small")


def get(path, **params):
    r = requests.get(f"{API}/{path}", auth=AUTH, params=params, timeout=60)
    r.raise_for_status()
    return r.json()


def all_pages(path, **params):
    skip = 0
    while True:
        data = get(path, _skip=skip, _limit=100, **params)
        yield from data["data"]
        if not data.get("has_more"):
            return
        skip += 100


def already_done(lead_id, cid, cache):
    if lead_id not in cache:
        cache[lead_id] = " ".join(
            (n.get("note") or "")[:40] for n in all_pages("activity/note/", lead_id=lead_id)
        )
    return f"TRANSKRIPT {cid}" in cache[lead_id]


def fmt(sec):
    return f"{int(sec // 60):02d}:{int(sec % 60):02d}"


def main():
    since = (datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_H)).isoformat()
    todo, notes_cache = [], {}
    for call in all_pages("activity/call/", date_created__gte=since):
        if (call.get("duration") or 0) < MIN_SEC or not call.get("recording_url"):
            continue
        if already_done(call["lead_id"], call["id"], notes_cache):
            continue
        todo.append(call)

    print(f"{len(todo)} neue Anrufe zum Transkribieren")
    if not todo:
        return

    model = WhisperModel(MODEL, device="cpu", compute_type="int8")
    fails = 0
    for call in todo:
        cid = call["id"]
        try:
            audio = requests.get(call["recording_url"], auth=AUTH, timeout=300)
            audio.raise_for_status()
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                f.write(audio.content)
                path = f.name
            segments, _ = model.transcribe(path, language="de", vad_filter=True)
            text = "\n".join(f"[{fmt(s.start)}] {s.text.strip()}" for s in segments)
            os.unlink(path)
            note = (
                f"TRANSKRIPT {cid}\n"
                f"Verkäufer: {call.get('user_name', '')} · Dauer: {call.get('duration')} Sek. · "
                f"{call.get('date_created', '')}\n\n{text or '(kein Text erkannt)'}"
            )
            r = requests.post(f"{API}/activity/note/", auth=AUTH,
                              json={"lead_id": call["lead_id"], "note": note}, timeout=60)
            r.raise_for_status()
            print(f"{cid}: ok ({call.get('duration')} Sek.)")
        except Exception as e:  # einzelne Fehler sollen den Lauf nicht stoppen
            fails += 1
            print(f"{cid}: Fehler {type(e).__name__}")
    if fails == len(todo):
        sys.exit(1)


if __name__ == "__main__":
    main()
