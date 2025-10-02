import time, random, pandas as pd
from datetime import datetime
from .parser import make_ff_driver, parse_tureng_ff

def crawl_urls(items, top_n=5, headless=False, jitter=(0.4, 1.0)):
    """
    items: [{'url','tag','bookmark_title'}, ...]
    Returns DataFrame with url, source_term, target_term, example, etc.
    """
    driver = make_ff_driver(headless=headless)
    records = []
    try:
        for i, item in enumerate(items, 1):
            u = item["url"]; tag = item.get("tag",""); ttl = item.get("bookmark_title","")
            out = parse_tureng_ff(driver, u, top_n=top_n, verbose=False)
            rowlist = out.get("rows") or [{"en": en, "tr": tr, "example": ""} for en, tr in out.get("pairs", [])]
            print(f"[{i}/{len(items)}] {u} -> {len(rowlist)} rows")
            for r in rowlist:
                records.append({
                    "url": u, "bookmark_title": ttl, "tag": tag,
                    "page_title": out.get("page_title",""),
                    "from_lang": out.get("from_lang",""),
                    "to_lang": out.get("to_lang",""),
                    "source_term": r["en"], "target_term": r["tr"],
                    "example": r.get("example",""),
                })
            time.sleep(random.uniform(*jitter))
    finally:
        try: driver.quit()
        except Exception: pass
    return pd.DataFrame(records)

def save_csv(df: pd.DataFrame, path_prefix="tureng_pairs"):
    out_csv = f"{path_prefix}_{datetime.now().strftime('%Y%m%d-%H%M%S')}.csv"
    df.to_csv(out_csv, index=False, encoding="utf-8-sig")
    print(f"Saved {len(df)} rows → {out_csv}")
    return out_csv