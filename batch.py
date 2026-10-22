"""batch.py - run the message detector over a whole CSV (adds score, level, language, signs)."""
import pandas as pd
from detector import analyze


def analyze_dataframe(df: pd.DataFrame, text_column: str) -> pd.DataFrame:
    rows = []
    for _, row in df.iterrows():
        res = analyze(str(row[text_column]))
        rows.append({
            "risk_score": res["score"],
            "risk_level": res["level"],
            "language": res["language"],
            "signs": ", ".join(f["rule"] for f in res["findings"]),
        })
    return pd.concat([df.reset_index(drop=True), pd.DataFrame(rows)], axis=1)
