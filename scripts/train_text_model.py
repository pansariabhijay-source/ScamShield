"""Train the ScamShield text classifier on the real labeled corpus.

Pipeline = TF-IDF (word 1-2grams  ⊕  char_wb 2-5grams)  →  Logistic Regression.
Char n-grams catch obfuscation / URLs / odd spacing that word tokens miss; the
linear head keeps the model tiny, fast (sub-ms inference) and fully interpretable
(per-token weights → explainable signals at serve time).

Outputs:
  app/detectors/models/text_clf.joblib   the fitted sklearn Pipeline
  app/detectors/models/text_clf.meta.json metrics + provenance

Run:  python -m scripts.train_text_model   (after scripts.fetch_datasets)
"""
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import FeatureUnion, Pipeline

from app.detectors.text_normalize import normalize

CORPUS = Path("data/processed/corpus.csv")
MODEL_DIR = Path("app/detectors/models")
MODEL_PATH = MODEL_DIR / "text_clf.joblib"
META_PATH = MODEL_DIR / "text_clf.meta.json"
VERSION = "text-clf-2.1.0"
# How many extra copies of the curated India seed to add to the TRAIN split so a
# few dozen domain examples actually move a 34k-row model (without leaking into test).
SEED_UPSAMPLE = 20


def build_pipeline() -> Pipeline:
    # preprocessor=normalize bakes URL/amount/phone/code placeholder substitution
    # into the model, so train & serve preprocessing can never drift apart.
    word = TfidfVectorizer(
        preprocessor=normalize, sublinear_tf=True, ngram_range=(1, 2), min_df=2,
        max_features=40000, strip_accents=None, lowercase=False,
    )
    char = TfidfVectorizer(
        preprocessor=normalize, sublinear_tf=True, analyzer="char_wb",
        ngram_range=(2, 5), min_df=3, max_features=40000, lowercase=False,
    )
    features = FeatureUnion([("word", word), ("char", char)])
    clf = LogisticRegression(
        C=4.0, class_weight="balanced", max_iter=2000, n_jobs=-1, solver="liblinear",
    )
    return Pipeline([("features", features), ("clf", clf)])


def top_tokens(pipe: Pipeline, k: int = 20) -> dict[str, list[str]]:
    names = pipe.named_steps["features"].get_feature_names_out()
    coef = pipe.named_steps["clf"].coef_[0]
    order = np.argsort(coef)
    scam = [names[i].split("__", 1)[-1] for i in order[::-1][:k]]
    safe = [names[i].split("__", 1)[-1] for i in order[:k]]
    return {"scam_indicative": scam, "ham_indicative": safe}


def main() -> None:
    if not CORPUS.exists():
        raise SystemExit("Run `python -m scripts.fetch_datasets` first.")
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(CORPUS).dropna(subset=["text"])
    df["text"] = df["text"].astype(str)
    df["label"] = df["label"].astype(int)
    if "source" not in df:
        df["source"] = "unknown"
    print(f"corpus: {len(df):,} rows  ({int(df.label.sum()):,} scam / {int((df.label == 0).sum()):,} ham)")

    train_df, test_df = train_test_split(
        df, test_size=0.2, random_state=42, stratify=df["label"]
    )

    def upsample(frame: pd.DataFrame) -> pd.DataFrame:
        seed = frame[frame["source"] == "india_seed"]
        if len(seed):
            frame = pd.concat([frame] + [seed] * SEED_UPSAMPLE, ignore_index=True)
        return frame.sample(frac=1.0, random_state=42)  # shuffle

    train_up = upsample(train_df)
    X_tr, y_tr = train_up["text"].values, train_up["label"].values
    X_te, y_te = test_df["text"].values, test_df["label"].values
    print(f"train rows after India-seed upsample (x{SEED_UPSAMPLE}): {len(train_up):,}")

    pipe = build_pipeline()
    print("training…")
    pipe.fit(X_tr, y_tr)

    proba = pipe.predict_proba(X_te)[:, 1]
    pred = (proba >= 0.5).astype(int)
    auc = roc_auc_score(y_te, proba)
    ap = average_precision_score(y_te, proba)
    cm = confusion_matrix(y_te, pred)
    report = classification_report(y_te, pred, target_names=["ham", "scam"], digits=4)

    print("\n=== held-out test (20%) ===")
    print(report)
    print(f"ROC-AUC={auc:.4f}   PR-AUC={ap:.4f}")
    print(f"confusion [[TN FP],[FN TP]] =\n{cm}")

    # Probability calibration: make predict_proba reflect the TRUE likelihood of
    # scam (so "0.70" means ~70% of such messages really are scams), measured by
    # the Brier score (lower = better calibrated). Isotonic fit via internal CV.
    print("\ncalibrating probabilities (isotonic)…")
    calibrated = CalibratedClassifierCV(build_pipeline(), method="isotonic", cv=3)
    calibrated.fit(X_tr, y_tr)
    proba_cal = calibrated.predict_proba(X_te)[:, 1]
    brier_raw = brier_score_loss(y_te, proba)
    brier_cal = brier_score_loss(y_te, proba_cal)
    auc_cal = roc_auc_score(y_te, proba_cal)
    print(f"  Brier (lower=better): raw={brier_raw:.4f}  ->  calibrated={brier_cal:.4f}")
    print(f"  ROC-AUC after calibration={auc_cal:.4f} (ranking preserved)")

    print("\n5-fold CV F1 (shuffled, no upsampling — honest generalization)…")
    cv = cross_val_score(
        build_pipeline(), df["text"].values, df["label"].values,
        cv=StratifiedKFold(5, shuffle=True, random_state=42), scoring="f1", n_jobs=-1,
    )
    print(f"  f1 per fold = {np.round(cv, 4)}   mean={cv.mean():.4f} ± {cv.std():.4f}")

    toks = top_tokens(pipe)
    print("\nTop scam tokens:", ", ".join(toks["scam_indicative"][:15]))

    # Ship the CALIBRATED model refit on ALL data (seed upsampled). The detector
    # only calls predict_proba, which CalibratedClassifierCV provides — no serving
    # changes needed; scores are now calibrated probabilities.
    print("\nrefitting calibrated model on full corpus for deployment…")
    full_up = upsample(df)
    final = CalibratedClassifierCV(build_pipeline(), method="isotonic", cv=3)
    final.fit(full_up["text"].values, full_up["label"].values)
    joblib.dump(final, MODEL_PATH, compress=3)
    rpt = classification_report(y_te, pred, target_names=["ham", "scam"], output_dict=True)
    meta = {
        "version": VERSION,
        "trained_at": datetime.now(UTC).isoformat(),
        "n_samples": int(len(df)),
        "sources": df["source"].value_counts().to_dict() if "source" in df else {},
        "test_metrics": {
            "roc_auc": round(float(auc), 4),
            "pr_auc": round(float(ap), 4),
            "precision_scam": round(rpt["scam"]["precision"], 4),
            "recall_scam": round(rpt["scam"]["recall"], 4),
            "f1_scam": round(rpt["scam"]["f1-score"], 4),
            "accuracy": round(rpt["accuracy"], 4),
        },
        "cv_f1_mean": round(float(cv.mean()), 4),
        "calibration": {
            "method": "isotonic",
            "brier_raw": round(float(brier_raw), 4),
            "brier_calibrated": round(float(brier_cal), 4),
        },
        "top_tokens": toks,
    }
    META_PATH.write_text(json.dumps(meta, indent=2))
    size_mb = MODEL_PATH.stat().st_size / 1e6
    print(f"\nsaved {MODEL_PATH} ({size_mb:.1f} MB)  +  {META_PATH}")


if __name__ == "__main__":
    main()
