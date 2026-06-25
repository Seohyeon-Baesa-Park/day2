import pandas as pd
from pathlib import Path
import sys

BASE = Path(__file__).parent
A_FILE = BASE / "store_a.xlsx"
B_FILE = BASE / "store_b.xlsx"
OUT_FILE = BASE / "merged_sales.xlsx"

if not A_FILE.exists() or not B_FILE.exists():
    print(f"Missing input files: {A_FILE.exists()=}, {B_FILE.exists()=}")
    sys.exit(1)


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    col_map = {}
    for col in df.columns:
        c = col.strip()
        if c in ("품목", "상품명"):
            col_map[col] = "상품"
        elif c in ("매출(원)", "금액"):
            col_map[col] = "금액"
        elif c in ("거래일", "날짜"):
            col_map[col] = "날짜"
        else:
            col_map[col] = col
    return df.rename(columns=col_map)


def clean_df(df: pd.DataFrame, branch_label: str) -> pd.DataFrame:
    df = normalize_columns(df)

    # Ensure required columns exist
    required = ["날짜", "상품", "금액"]
    for r in required:
        if r not in df.columns:
            raise KeyError(f"Required column '{r}' not found after mapping. Available: {list(df.columns)}")

    # 날짜 -> YYYY-MM-DD
    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")
    if df["날짜"].isna().any():
        raise ValueError("Some 날짜 values could not be parsed as dates.")
    df["날짜"] = df["날짜"].dt.strftime("%Y-%m-%d")

    # 금액 -> 숫자 (정수)
    df["금액"] = (
        df["금액"].astype(str).str.replace(r"[^0-9.-]", "", regex=True)
    )
    if df["금액"].eq("").any():
        raise ValueError("Some 금액 values are empty after cleaning.")
    df["금액"] = pd.to_numeric(df["금액"], errors="coerce").fillna(0).astype(int)

    df["지점"] = branch_label

    return df[["날짜", "지점", "상품", "금액"]]


def main():
    a = pd.read_excel(A_FILE)
    b = pd.read_excel(B_FILE)

    a_clean = clean_df(a, "A")
    b_clean = clean_df(b, "B")

    merged = pd.concat([a_clean, b_clean], ignore_index=True)

    merged.to_excel(OUT_FILE, index=False)
    print(f"Saved merged file to: {OUT_FILE}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Error:", e)
        sys.exit(1)
