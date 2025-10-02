# Firefox to Anki (TSV)

Pull Firefox bookmarks tagged like `anki`, scrape **Tureng** meanings + example sentences with Selenium/Firefox and export **Anki-ready TSV** (Front, Back, Examples).

## Quick start

```bash
conda create -n tureng-anki python=3.11 -y
conda activate tureng-anki
pip install -U pip
pip install -r requirements.txt

set PYTHONPATH=%CD%\src
python -m tureng_anki --tag anki --top-n 5 --headless

conda install -c conda-forge firefox geckodriver
