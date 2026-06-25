import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import altair as alt
import urllib.request
import json
from datetime import datetime

st.set_page_config(page_title="매출 대시보드", layout="wide")

# 데이터 로드: merged_sales.xlsx 우선, 없으면 업로드로 대체
DATA_PATH = Path("merged_sales.xlsx")
uploaded_file = st.sidebar.file_uploader("merged_sales.xlsx 업로드 (옵션)", type=["xlsx"])

if DATA_PATH.exists():
    df = pd.read_excel(DATA_PATH)
elif uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
else:
    st.warning("'merged_sales.xlsx' 파일을 찾을 수 없습니다. 프로젝트 폴더에 파일을 두거나 아래에서 파일을 업로드하세요.")
    st.info("터미널에서 'python3 merge_sales.py'를 실행하여 파일을 생성할 수 있습니다.")
    st.stop()

# 컬럼명 통일(가능한 경우)
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
df = df.rename(columns=col_map)

# 필수 컬럼 존재 확인
required = ["날짜", "지점", "상품", "금액"]
missing = [r for r in required if r not in df.columns]
if missing:
    st.error(f"필수 컬럼이 누락되었습니다: {missing}")
    st.stop()

# 데이터 타입 정리
df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")
if df["날짜"].isna().any():
    st.error("일부 '날짜' 값을 날짜로 파싱할 수 없습니다. 데이터 형식을 확인하세요.")
    st.stop()
df["금액"] = (
    df["금액"].astype(str).str.replace(r"[^0-9.-]", "", regex=True)
)
df["금액"] = pd.to_numeric(df["금액"], errors="coerce").fillna(0).astype(int)

# 제목
st.title("매출 대시보드")

# 지점 필터 (데이터에서 가능한 값으로 생성)
branches = sorted(df["지점"].dropna().unique().tolist())
branch = st.selectbox("지점 선택", ["전체"] + branches)
filtered = df if branch == "전체" else df[df["지점"] == branch]

# 왼쪽 사이드바에 날짜 범위 필터 추가
min_date = df["날짜"].min().date()
max_date = df["날짜"].max().date()
date_range = st.sidebar.date_input("기간 선택", value=(min_date, max_date))
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date, end_date = date_range[0], date_range[1]
else:
    start_date = date_range
    end_date = date_range

# 필터에 날짜 범위 적용
filtered = filtered[(filtered["날짜"].dt.date >= start_date) & (filtered["날짜"].dt.date <= end_date)]

# 전체 매출 합계
total = filtered["금액"].sum()
st.metric(label="총 매출", value=f"₩{total:,.0f}")

st.divider()

# --- 서울 기상 정보 (Open-Meteo API) ---
@st.cache_data(ttl=600)
def get_seoul_weather():
    """Open-Meteo에서 서울의 현재 기온과 시간별 기온(오늘)을 가져옵니다."""
    # wttr.in provides JSON at ?format=j1 and does not require an API key
    url = "https://wttr.in/Seoul?format=j1"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.load(resp)
    except Exception:
        return None, None

    # current condition
    current_list = data.get("current_condition") or []
    current = current_list[0] if current_list else None

    # hourly data for today is under weather[0]['hourly']
    weather = data.get("weather") or []
    hourly = []
    if weather:
        hourly = weather[0].get("hourly", [])

    if not hourly:
        return current, None

    rows = []
    today = pd.Timestamp.now().date()
    for h in hourly:
        # wttr.time values are strings like '0', '300', '600', '900', etc.
        tstr = h.get("time", "0")
        try:
            tval = int(tstr)
        except Exception:
            tval = 0
        hour = tval if tval < 100 else (tval // 100)
        # build datetime for today at that hour
        now = pd.Timestamp.now()
        dt = pd.Timestamp(year=now.year, month=now.month, day=now.day, hour=int(hour))
        temp_c = h.get("tempC") or h.get("tempC")
        try:
            temp = float(temp_c)
        except Exception:
            temp = None
        rows.append({"시간": dt, "기온": temp})

    hourly_df = pd.DataFrame(rows)
    today_df = hourly_df[hourly_df["시간"].dt.date == today]
    return current, today_df

st.subheader("서울 기상 정보")
current_weather, seoul_today = get_seoul_weather()
if current_weather is None:
    st.info("서울의 기상 정보를 불러올 수 없습니다. (Open-Meteo)")
else:
    cur_temp = current_weather.get("temperature")
    cur_time = current_weather.get("time")
    st.metric(label="서울 현재 기온", value=f"{cur_temp} ℃")
    if cur_time:
        st.caption(f"측정시각: {cur_time}")

    if seoul_today is None or seoul_today.empty:
        st.info("오늘의 시간별 기온 데이터를 가져오지 못했습니다.")
    else:
        chart = (
            alt.Chart(seoul_today)
            .mark_line(point=True)
            .encode(
                x=alt.X("시간:T", title="시간"),
                y=alt.Y("기온:Q", title="기온 (℃)"),
                tooltip=[
                    alt.Tooltip("시간:T", title="시간"),
                    alt.Tooltip("기온:Q", title="기온 (℃)")
                ],
            )
            .properties(height=240)
            .interactive()
        )
        st.altair_chart(chart, use_container_width=True)

        disp = seoul_today.copy()
        disp["시간"] = disp["시간"].dt.strftime("%H:%M")
        disp["기온"] = disp["기온"].map(lambda x: f"{x:.1f} ℃")
        st.dataframe(disp.rename(columns={"시간": "시간", "기온": "기온"}), use_container_width=True, hide_index=True)


col1, col2 = st.columns(2)

# 월별 매출 추이 선그래프
with col1:
    st.subheader("월별 매출 추이")
    # 날짜를 기준으로 월말 기준 월별 합계를 계산
    monthly_sales = (
        filtered.groupby(pd.Grouper(key="날짜", freq="ME"))["금액"]
        .sum()
        .rename("매출")
    )
    monthly_sales.index = monthly_sales.index.to_period("M").to_timestamp()

    # Altair 차트로 표시: 축 포맷과 툴팁에 원화 표시 포함
    monthly_df = monthly_sales.reset_index()
    monthly_df.columns = ["날짜", "매출"]
    monthly_df["매출_표시"] = monthly_df["매출"].apply(lambda x: f"₩{x:,.0f}")

    chart = (
        alt.Chart(monthly_df)
        .mark_line(point=True)
        .encode(
            x=alt.X("날짜:T", title="날짜"),
            y=alt.Y("매출:Q", axis=alt.Axis(format=",.0f", title="매출 (₩)")),
            tooltip=[alt.Tooltip("매출_표시:N", title="매출")],
        )
        .interactive()
    )

    st.altair_chart(chart, use_container_width=True)

# 상품별 매출 표
with col2:
    st.subheader("상품별 매출")
    product_sales = (
        filtered.groupby("상품")["금액"]
        .sum()
        .reset_index()
        .sort_values("금액", ascending=False)
        .rename(columns={"금액": "매출"})
    )
    product_sales["매출"] = product_sales["매출"].apply(lambda x: f"₩{x:,.0f}")
    st.dataframe(product_sales, use_container_width=True, hide_index=True)
