# Firefox to Anki

Extract words from Firefox bookmarks/history and turn them into **Anki flashcards** for language learning.

## Features

- Read bookmarks (title + tags) from `places.sqlite`
- Filter unknown words
- Fetch meanings from tureng.com
- Export to **Anki-ready TSV** (import via Anki → File → Import)

## Quick start

```bash
conda create -n tureng-anki python=3.11 -y
conda activate tureng-anki
pip install -U pip
pip install -r requirements.txt

set PYTHONPATH=%CD%\src
python -m tureng_anki --tag anki --top-n 5 --headless

conda install -c conda-forge firefox geckodriver
```

## Note
Use responsibly, respect site ToS and add delays.