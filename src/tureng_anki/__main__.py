import argparse, pandas as pd
from .bookmarks import get_tagged_tureng
from .crawl import crawl_urls, save_csv
from .export import build_cards_df, save_tsv

def main():
    ap = argparse.ArgumentParser(description="Firefox bookmarks (Tureng) → Anki TSV")
    ap.add_argument("--tag", default="anki", help="Bookmark tag LIKE filter (default: anki)")
    ap.add_argument("--top-n", type=int, default=5, help="Top N meanings per word")
    ap.add_argument("--headless", action="store_true", help="Run Firefox headless")
    ap.add_argument("--out-csv", default=None, help="CSV output path prefix")
    ap.add_argument("--out-tsv", default="anki_tureng_multi_with_examples.tsv", help="TSV output file")
    args = ap.parse_args()

    items = get_tagged_tureng(args.tag)
    print(f"Found {len(items)} tureng.com URLs with tag like '%{args.tag}%'.")
    df = crawl_urls(items, top_n=args.top_n, headless=args.headless)
    csv_path = save_csv(df, args.out_csv or "tureng_pairs")
    cards_df = build_cards_df(df, max_per_card=args.top_n)
    save_tsv(cards_df, args.out_tsv)
    print("Done.")

if __name__ == "__main__":
    main()