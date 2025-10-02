import os, re, numpy as np, pandas as pd

def _clean_txt(s):
    if pd.isna(s): return ''
    s = str(s)
    # drop trailing "More Sentences" (and TR variant)
    s = re.sub(r'(?:<br>\s*)?(more\s+sentences|daha\s+fazla\s+c[üu]mle(?:ler)?)\s*$', '', s, flags=re.I)
    s = s.replace(' <br> ', '<br>').replace(' <br>', '<br>').replace('<br> ', '<br>')
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def build_cards_df(df: pd.DataFrame, max_per_card=5):
    df = df.loc[:, ~df.columns.duplicated()].copy()
    for col in ('source_term','target_term','example'):
        if col in df.columns:
            df[col] = df[col].map(_clean_txt)

    df = df.reset_index(drop=True)
    df['row_order'] = np.arange(len(df))

    def uniq_preserve(seq):
        seen=set(); out=[]
        for x in seq:
            if x and x not in seen: seen.add(x); out.append(x)
        return out

    cards = []
    group_cols = ['url','from_lang','to_lang','source_term']
    for key, g in df.groupby(group_cols, sort=False):
        g = g.sort_values('row_order')
        top = g.head(max_per_card)

        trans = uniq_preserve(top['target_term'].tolist())
        back = " • ".join(trans)

        ex_parts = []
        for _, r in top.iterrows():
            ex = _clean_txt(r.get('example',''))
            if ex:
                ex_parts.append(f"<b>{r['target_term']}</b>: {ex}")
        examples = "<br><br>".join(uniq_preserve(ex_parts))

        cards.append({"Front": key[-1], "Back": back, "Examples": examples})

    return pd.DataFrame(cards).drop_duplicates()

def save_tsv(cards_df: pd.DataFrame, path="anki_tureng_multi_with_examples.tsv"):
    cards_df.to_csv(path, sep='\t', index=False, header=False, encoding='utf-8')
    print(f"Wrote {len(cards_df)} cards -> {path}")
    return path