# Beyond the Dropdown: Audio Codecs for Game Audio

Repository: [from-adpcm-to-ai](https://github.com/collinschupman/from-adpcm-to-ai).
The local project directory is `from-adpcm-to-ai`.

Slides for Collin Schupman's talk at GameSoundCon, Wednesday, October 21, 2026.

Audio codecs form the foundation of every audio choice in a game: file size, streaming performance, memory budgets, platform compliance, and, ultimately, what players hear. Yet for many game audio professionals, codec selection remains a black box: a dropdown menu in middleware. This talk aims to change that.

It starts with the basics of audio rendering and how codecs work, covers the problems codecs solve in games (samples, memory, voice chat, streaming, hardware), moves through the formats in use today (Opus, Vorbis, AAC, ATRAC9, XMA) with a decision framework, and ends at the frontier: Apple's APAC and neural audio codecs.

## View the slides

Open `index.html` in a browser. Everything it needs is in this repository, including the fonts, so it works offline.

To host it, turn on GitHub Pages for this repository (Settings → Pages → Deploy from a branch → `main`, `/ (root)`). The deck will be served at the repository's Pages URL.

| Key | Action |
|---|---|
| → / Space / Page Down | Next slide |
| ← / Page Up | Previous slide |
| Home / End | First / last slide |
| N | Show or hide speaker notes |
| F | Fullscreen |

Clicking the right side of a slide goes forward, the left third goes back, and swiping works on touch screens. Add `#12` to the URL to open on slide 12. Printing from the browser gives one slide per page, which is a quick way to make a PDF.

## Outline

1. **Introduction**: about the speaker, why this talk, what a codec setting affects
2. **The basics**: the audio render loop, the path of one voice, the cost of uncompressed audio, three kinds of codec, inside a perceptual codec, terms on the settings panel
3. **The problems codecs solve**: sample-based audio, memory and disk, voice chat, streaming, hardware, a short history
4. **The modern toolbox**: codecs in use today, Vorbis and Opus, platform codecs, codecs you didn't choose, a decision order, what to measure
5. **The frontier**: Apple's APAC, neural codecs, language models in codecs, barriers in games, where neural audio shows up first
6. **Takeaways**

## What's in the repository

```
index.html          The deck, built from source/ (35 slides)
slides.pdf          The same deck as a PDF, one slide per page
speaker-notes.md    Speaker notes for every slide, built from source/
build.py            Rebuilds index.html and speaker-notes.md
source/
  deck.json         Title, slide order and sections
  slides/*.html     One file per slide: a single 1920x1080 <section>
assets/
  qr-*.png          QR codes on the closing slide
  fonts/            Libre Franklin and IBM Plex Mono, with their licenses
```

## Editing

Each slide is one file in `source/slides/`, with inline styles on a fixed 1920×1080 canvas. Speaker notes are the `<aside>` at the end of the file. To reorder, add or remove slides, edit the `order` list in `source/deck.json`. Then rebuild:

```
python3 build.py
```

The script needs only the Python standard library. `python3 build.py --no-notes` builds `index.html` with the speaker notes left out.

## Fonts

Libre Franklin and IBM Plex Mono are distributed under the SIL Open Font License 1.1. The license texts are in `assets/fonts/`.
