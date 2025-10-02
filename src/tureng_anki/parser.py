import time, re
from bs4 import BeautifulSoup, NavigableString
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FFOptions
from selenium.webdriver.firefox.service import Service as FFService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def make_ff_driver(headless: bool = False):
    opts = FFOptions()
    if headless: opts.add_argument("-headless")
    # lighter & stable
    opts.set_preference("permissions.default.image", 2)
    opts.set_preference("dom.ipc.processCount", 1)
    opts.set_preference("network.http.max-persistent-connections-per-server", 4)
    opts.set_preference("intl.accept_languages", "en-US,tr-TR,en")
    return webdriver.Firefox(service=FFService(), options=opts)

def _langs(u: str):
    ul = u.lower()
    if "/english-turkish/" in ul or "/ingilizce-turkce/" in ul: return ("English","Turkish")
    if "/turkish-english/" in ul or "/turkce-ingilizce/" in ul: return ("Turkish","English")
    return ("?","?")

def _strip_pos(s: str):
    s = re.sub(r"\s+", " ", s).strip()
    return re.sub(r"\b(adj|adv|n|v|prep|conj|pron|abbr)\.\b$", "", s, flags=re.I).strip()

def _term_from_cell(td):
    for a in td.select("a"):
        t = a.get_text(" ", strip=True)
        if t and "more sentences" not in t.lower():
            return _strip_pos(t)
    for sel in ("strong","b","span"):
        el = td.select_one(sel)
        if el: return _strip_pos(el.get_text(" ", strip=True))
    return _strip_pos(td.get_text(" ", strip=True))

def _examples_from_row(ex_tr):
    td = ex_tr.select_one("td.example-sentences")
    if not td: return ""
    SEP = "<br>"
    en_chunks, tr_chunks, cur = [], [], 0
    for node in td.children:
        if getattr(node, "name", None) == "br":
            cur = 1; continue
        txt = str(node) if isinstance(node, NavigableString) else node.get_text(" ", strip=True)
        txt = re.sub(r"\s+", " ", txt).strip()
        if not txt: continue
        (en_chunks if cur == 0 else tr_chunks).append(txt)
    en = " ".join(en_chunks).strip()
    tr = " ".join(tr_chunks).strip()
    return (en + (SEP + tr if tr else "")).strip()

def parse_tureng_ff(driver, url: str, top_n: int = 5, wait_s: int = 20, verbose: bool = False):
    if verbose: print(f"[{time.strftime('%H:%M:%S')}] GET {url}")
    driver.get(url)

    # cookie banners (best-effort)
    for sel in ["#onetrust-accept-btn-handler","button[id*='accept']","button.cookie-accept","button[aria-label*='Accept']"]:
        try:
            WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CSS_SELECTOR, sel))).click(); break
        except Exception:
            pass

    WebDriverWait(driver, wait_s).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    try:
        WebDriverWait(driver, 10).until(EC.any_of(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#englishResultsTable")),
            EC.presence_of_element_located((By.CSS_SELECTOR, "#turkishResultsTable")),
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.searchResultsTable")),
        ))
    except TimeoutException:
        pass

    soup = BeautifulSoup(driver.page_source, "lxml")
    page_title = soup.title.text.strip() if soup.title else ""
    frm, to = _langs(url)

    pairs, rows = [], []
    tbl = soup.select_one("#englishResultsTable, #turkishResultsTable, table.searchResultsTable")
    if tbl:
        trs = tbl.select("tbody > tr")
        i = 0
        while i < len(trs) and len(pairs) < top_n:
            tr = trs[i]
            en_td = tr.select_one('td.en, td[class^="en"], td[class*=" en "]')
            tr_td = tr.select_one('td.tr, td[class^="tr"], td[class*=" tr "]')
            if en_td and tr_td:
                en = _term_from_cell(en_td)
                tr_word = _term_from_cell(tr_td)
                example = ""
                if i + 1 < len(trs):
                    nxt = trs[i+1]
                    if "example-sentences-row" in (nxt.get("class", []) or []):
                        example = _examples_from_row(nxt)
                        i += 1  # skip example row

                if en.lower() in {"common usage","general","electric","medicine","computers","slang"}:
                    tds = tr.find_all("td", recursive=False)
                    if len(tds) >= 4:
                        en      = _term_from_cell(tds[2])
                        tr_word = _term_from_cell(tds[3])

                if en and tr_word:
                    pairs.append((en, tr_word))
                    rows.append({"en": en, "tr": tr_word, "example": example})
            i += 1

    if verbose: print(f"[{time.strftime('%H:%M:%S')}] OK pairs={len(pairs)}")
    return {"page_title": page_title, "from_lang": frm, "to_lang": to, "pairs": pairs, "rows": rows}