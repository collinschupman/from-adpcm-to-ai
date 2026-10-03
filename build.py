#!/usr/bin/env python3
"""Rebuild index.html and speaker-notes.md from the files in source/.

Usage:  python3 build.py              # deck with speaker notes
        python3 build.py --no-notes   # deck only: notes left out of index.html

source/deck.json lists the slide order; each slide is one file in
source/slides/<id>.html holding a single 1920x1080 <section>. Speaker
notes live in the <aside> at the end of each slide.
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "source"

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
@font-face { font-family: "Libre Franklin"; font-weight: 100 900; font-display: swap;
  src: url(assets/fonts/LibreFranklin-Variable.ttf) format("truetype"); }
@font-face { font-family: "IBM Plex Mono"; font-weight: 400; font-display: swap;
  src: url(assets/fonts/IBMPlexMono-Regular.ttf) format("truetype"); }
@font-face { font-family: "IBM Plex Mono"; font-weight: 500; font-display: swap;
  src: url(assets/fonts/IBMPlexMono-Medium.ttf) format("truetype"); }

* { box-sizing: border-box; }
html, body { margin: 0; height: 100%; background: #0e0e0e; overflow: hidden; }

/* The deck is a fixed 1920x1080 stage, scaled to fit the window. */
#stage { position: absolute; left: 50%; top: 50%; width: 1920px; height: 1080px; }
#stage > section { position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; overflow: hidden; }
#stage > section:not(.on) { display: none !important; }

h1, h2, h3, p, ul, ol { margin: 0; }
p { font-size: 32px; line-height: 1.4; }
ul, ol { padding-left: 1.1em; }
img, svg { display: block; }
aside { display: none; }

table { width: 100%; border-collapse: collapse; }
th, td { padding: 0.45em 0.8em 0.45em 0; line-height: 1.4; vertical-align: top;
  border-bottom: 1px solid #cfcbc2; }
th { font-weight: 700; border-bottom: 2px solid #161616; }

x-shape { display: block; flex: none; }
x-shape[kind="arrow-right"] {
  clip-path: polygon(0 30%, 60% 30%, 60% 0, 100% 50%, 60% 100%, 60% 70%, 0 70%); }

#hud { position: fixed; right: 12px; bottom: 8px; font: 13px/1 system-ui, sans-serif;
  color: #fff; opacity: 0.45; user-select: none; }
#notes { position: fixed; left: 0; right: 0; bottom: 0; max-height: 34vh; overflow: auto;
  padding: 16px 24px 28px; background: rgba(14, 14, 14, 0.92); color: #f7f6f2;
  font: 18px/1.5 system-ui, sans-serif; display: none; }
#notes.on { display: block; }

@page { size: 1920px 1080px; margin: 0; }
@media print {
  html, body { height: auto; overflow: visible; background: none; }
  #stage { position: static; width: auto; height: auto; transform: none !important; }
  #stage > section, #stage > section:not(.on) { position: relative; display: flex !important;
    break-after: page; }
  #hud, #notes { display: none !important; }
}
</style>
</head>
<body>
<div id="stage">
__SLIDES__
</div>
<div id="notes"></div>
<div id="hud"></div>
<script>
const stage = document.getElementById('stage');
const hud = document.getElementById('hud');
const notes = document.getElementById('notes');
const slides = [...stage.children];
let current = 0;

function fit() {
  const s = Math.min(innerWidth / 1920, innerHeight / 1080);
  stage.style.transform = `translate(-50%, -50%) scale(${s})`;
}

function go(n) {
  current = Math.max(0, Math.min(slides.length - 1, n));
  slides.forEach((s, k) => s.classList.toggle('on', k === current));
  const aside = slides[current].querySelector('aside');
  notes.textContent = aside ? aside.textContent : '';
  hud.textContent = `${current + 1} / ${slides.length}   ←/→ move · N notes · F fullscreen`;
  history.replaceState(null, '', '#' + (current + 1));
}

addEventListener('resize', fit);
addEventListener('hashchange', () => go((parseInt(location.hash.slice(1), 10) || 1) - 1));
addEventListener('keydown', (e) => {
  if (['ArrowRight', 'ArrowDown', 'PageDown', ' '].includes(e.key)) { go(current + 1); e.preventDefault(); }
  else if (['ArrowLeft', 'ArrowUp', 'PageUp'].includes(e.key)) { go(current - 1); e.preventDefault(); }
  else if (e.key === 'Home') go(0);
  else if (e.key === 'End') go(slides.length - 1);
  else if (e.key === 'n' || e.key === 'N') notes.classList.toggle('on');
  else if (e.key === 'f' || e.key === 'F') {
    if (document.fullscreenElement) document.exitFullscreen();
    else document.documentElement.requestFullscreen();
  }
});
stage.addEventListener('click', (e) => go(current + (e.clientX < innerWidth / 3 ? -1 : 1)));
let touchX = null;
addEventListener('touchstart', (e) => { touchX = e.touches[0].clientX; }, { passive: true });
addEventListener('touchend', (e) => {
  if (touchX === null) return;
  const dx = e.changedTouches[0].clientX - touchX;
  if (Math.abs(dx) > 40) go(current + (dx < 0 ? 1 : -1));
  touchX = null;
});

fit();
go((parseInt(location.hash.slice(1), 10) || 1) - 1);
</script>
</body>
</html>
"""


def plain(markup):
    return html.unescape(re.sub(r"<[^>]+>", "", markup)).strip()


def main():
    with_notes = "--no-notes" not in sys.argv[1:]
    deck = json.loads((SRC / "deck.json").read_text(encoding="utf-8"))
    slides, notes = [], ["# Speaker notes", "", deck["title"], ""]
    for number, slide_id in enumerate(deck["order"], 1):
        text = (SRC / "slides" / f"{slide_id}.html").read_text(encoding="utf-8").strip()
        title = re.search(r"<h[12][^>]*>(.*?)</h[12]>", text, re.S)
        aside = re.search(r"<aside>(.*?)</aside>", text, re.S)
        notes += [f"## {number}. {plain(title.group(1)) if title else slide_id}", "",
                  plain(aside.group(1)) if aside else "(no notes)", ""]
        if not with_notes:
            text = re.sub(r"\s*<aside>.*?</aside>", "", text, flags=re.S)
        slides.append(text)

    page = TEMPLATE.replace("__TITLE__", html.escape(deck["title"])).replace("__SLIDES__", "\n".join(slides))
    (ROOT / "index.html").write_text(page, encoding="utf-8")
    if with_notes:
        (ROOT / "speaker-notes.md").write_text("\n".join(notes), encoding="utf-8")
        print(f"Built index.html and speaker-notes.md from {len(slides)} slides.")
    else:
        print(f"Built index.html from {len(slides)} slides, without speaker notes.")


if __name__ == "__main__":
    main()
