"""Fetch & unify public scam/spam corpora for training the text classifier.

Pulls real, publicly-licensed labeled datasets, normalises them into a single
`(text, label, source)` table (label: 1 = scam/spam, 0 = legitimate) and writes
`data/processed/corpus.csv`. Idempotent: raw downloads are cached under
`data/raw/` and skipped on re-run.

Sources
-------
* UCI SMS Spam Collection  — ~5.5k hand-labelled SMS (lottery/prize/premium-rate
  scams + ham).  Almeida & Gómez Hidalgo, 2011.
* Enron-Spam (Metsis et al.) — ~33k labelled emails (subject + body).

Run:  python -m scripts.fetch_datasets
"""
from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

RAW = Path("data/raw")
OUT = Path("data/processed/corpus.csv")
RAW.mkdir(parents=True, exist_ok=True)
OUT.parent.mkdir(parents=True, exist_ok=True)

SMS_URL = "https://raw.githubusercontent.com/justmarkham/pycon-2016-tutorial/master/data/sms.tsv"
ENRON_URL = "https://raw.githubusercontent.com/MWiechmann/enron_spam_data/master/enron_spam_data.zip"


def _download(url: str, dest: Path) -> Path:
    if dest.exists() and dest.stat().st_size > 0:
        print(f"  cached  {dest}")
        return dest
    print(f"  GET     {url}")
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    dest.write_bytes(r.content)
    print(f"  saved   {dest} ({dest.stat().st_size:,} bytes)")
    return dest


def load_sms() -> pd.DataFrame:
    path = _download(SMS_URL, RAW / "sms.tsv")
    df = pd.read_csv(path, sep="\t", header=None, names=["label", "text"])
    df["label"] = (df["label"].str.strip().str.lower() == "spam").astype(int)
    df["source"] = "uci_sms"
    return df[["text", "label", "source"]]


def load_enron() -> pd.DataFrame:
    path = _download(ENRON_URL, RAW / "enron_spam_data.zip")
    with zipfile.ZipFile(path) as z:
        name = next(n for n in z.namelist() if n.endswith(".csv"))
        df = pd.read_csv(io.BytesIO(z.read(name)))
    subj = df["Subject"].fillna("").astype(str)
    body = df["Message"].fillna("").astype(str)
    text = (subj + ". " + body).str.strip(". ").str.strip()
    out = pd.DataFrame({"text": text})
    out["label"] = (df["Spam/Ham"].str.strip().str.lower() == "spam").astype(int)
    out["source"] = "enron"
    return out[["text", "label", "source"]]


def load_india_seed() -> pd.DataFrame:
    """Curated India-specific scam/ham (see scripts/gen_india_seed.py)."""
    path = Path("data/curated/india_seed.csv")
    if not path.exists():
        raise FileNotFoundError("run `python -m scripts.gen_india_seed` first")
    df = pd.read_csv(path)
    return df[["text", "label", "source"]]


LOADERS = {"uci_sms": load_sms, "enron": load_enron, "india_seed": load_india_seed}


def main() -> None:
    frames: list[pd.DataFrame] = []
    for name, loader in LOADERS.items():
        print(f"[{name}]")
        try:
            df = loader()
            print(f"  rows={len(df):,}  scam={int(df.label.sum()):,}  ham={int((df.label == 0).sum()):,}")
            frames.append(df)
        except Exception as exc:  # one dead mirror must not kill the build
            print(f"  SKIPPED ({exc})")

    if not frames:
        raise SystemExit("No datasets could be fetched.")

    corpus = pd.concat(frames, ignore_index=True)
    # Clean: drop empties, collapse whitespace, cap absurdly long emails, dedup.
    corpus["text"] = corpus["text"].astype(str).str.replace(r"\s+", " ", regex=True).str.strip()
    corpus = corpus[corpus["text"].str.len().between(3, 5000)]
    corpus = corpus.drop_duplicates(subset="text").reset_index(drop=True)

    corpus.to_csv(OUT, index=False)
    n, pos = len(corpus), int(corpus.label.sum())
    print(f"\nWrote {OUT}: {n:,} rows  ({pos:,} scam / {n - pos:,} ham, {pos / n:.1%} positive)")
    print(corpus.groupby("source").size().to_dict())


if __name__ == "__main__":
    main()
