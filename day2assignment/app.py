import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.request
import json
import ssl
from datetime import datetime

st.set_page_config(
    page_title="Glacier Kitchen | Promotion & Analytics",
    layout="wide",
    page_icon="🍖",
    initial_sidebar_state="expanded",
)

# ── CSS: Glacier Kitchen Light Yellow Theme ─────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');
.material-symbols-outlined {
    font-variation-settings: 'FILL' 0,'wght' 400,'GRAD' 0,'opsz' 24;
    vertical-align: middle; line-height: 1;
}
*, *::before, *::after { font-family: 'Inter', sans-serif !important; }
/* Material Symbols 폰트 복원 (Inter 오버라이드 이후) */
.material-symbols-outlined,
[class*="material-symbols"] {
    font-family: 'Material Symbols Outlined' !important;
}

/* ── 사이드바 닫기 버튼: keyboard_double 텍스트 숨김 ── */
[data-testid="stSidebarCollapseButton"] span,
[data-testid="stSidebarCollapseButton"] svg,
[data-testid="stSidebarHeader"] button span,
[data-testid="stSidebarHeader"] button svg,
section[data-testid="stSidebar"] > div:first-child > div:first-child button span,
section[data-testid="stSidebar"] > div:first-child > div:first-child button svg {
    display: none !important;
}

/* ── 사이드바 펼치기 버튼: double_arrow_right 제거 → >> 회색 ── */
[data-testid="stSidebarCollapsedControl"] span,
[data-testid="stSidebarCollapsedControl"] svg,
[data-testid="collapsedControl"] span,
[data-testid="collapsedControl"] svg { display: none !important; }
[data-testid="stSidebarCollapsedControl"] button::before,
[data-testid="collapsedControl"] button::before {
    content: '>>';
    font-size: 0.95rem; font-weight: 800; color: #74777F;
    font-family: 'Inter', sans-serif !important;
}
/* << 도 회색으로 */
[data-testid="stSidebarCollapseButton"] button::before,
[data-testid="stSidebarHeader"] button::before,
section[data-testid="stSidebar"] > div:first-child > div:first-child button::before {
    content: '<<';
    font-size: 0.9rem; font-weight: 800; color: #74777F;
    font-family: 'Inter', sans-serif !important;
}

/* ── Expander 버튼 arrow_right 텍스트 숨김 ── */
[data-testid="stExpander"] summary span,
[data-testid="stExpanderToggleIcon"],
details > summary span,
[data-testid="stBaseButton-minimal"] span {
    font-family: 'Material Symbols Outlined' !important;
    font-variation-settings: 'FILL' 0,'wght' 400,'GRAD' 0,'opsz' 24;
}

/* ── Base ── */
.stApp                  { background-color: #FEF9C3 !important; }
[data-testid="stHeader"] {
    background: rgba(254,249,195,0.85) !important;
    backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(0,102,139,0.08);
}
[data-testid="stMain"],
[data-testid="block-container"] { background: transparent !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.45) !important;
    backdrop-filter: blur(16px);
    border-right: 1px solid rgba(0,102,139,0.1) !important;
}
[data-testid="stSidebar"] > div,
[data-testid="stSidebarContent"] { background: transparent !important; }

/* ── Typography ── */
h1 { color: #00668B !important; font-weight: 800 !important; letter-spacing: -0.5px; }
h2, h3 { color: #1C1B1F !important; font-weight: 800 !important; }
p, li  { color: #44474E !important; }
[data-testid="stCaptionContainer"] p { color: #74777F !important; font-size: 0.78rem; }

/* ── Metric ── */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.4) !important;
    backdrop-filter: blur(16px);
    border: 1px solid rgba(0,102,139,0.1) !important;
    border-radius: 16px !important;
    padding: 20px 22px !important;
    box-shadow: 0 4px 24px rgba(0,102,139,0.05);
}
[data-testid="stMetricValue"]            { color: #1C1B1F !important; font-weight: 800 !important; }
[data-testid="stMetricLabel"] > div      { color: #44474E !important; font-size: 0.78rem !important; font-weight: 600 !important; }
[data-testid="stMetricDelta"]            { color: #00668B !important; font-weight: 700 !important; }

/* ── Selectbox ── */
[data-testid="stSelectbox"] label p { color: #44474E !important; }
[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.6) !important;
    border: 1px solid rgba(0,102,139,0.15) !important;
    border-radius: 10px !important;
}

/* ── Alert / DataFrame / Divider ── */
[data-testid="stAlert"] {
    background: rgba(255,255,255,0.5) !important;
    border: 1px solid rgba(0,102,139,0.15) !important;
    border-radius: 12px !important; color: #1C1B1F !important;
}
[data-testid="stDataFrame"] { border: 1px solid rgba(0,102,139,0.1); border-radius: 12px; overflow: hidden; }
hr { border-color: rgba(0,102,139,0.08) !important; margin: 1.5rem 0 !important; }

/* ── Glass Panels ── */
.glass-panel {
    background: rgba(255,255,255,0.4);
    backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(0,102,139,0.1);
    box-shadow: 0 4px 30px rgba(0,102,139,0.05);
    border-radius: 20px; padding: 26px;
}
.glass-panel-elevated {
    background: rgba(255,255,255,0.65);
    backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(0,102,139,0.15);
    box-shadow: 0 8px 32px rgba(0,102,139,0.08);
    border-radius: 20px; padding: 24px;
}

/* ── KPI Cards ── */
.kpi-card {
    background: rgba(255,255,255,0.4);
    backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(0,102,139,0.1);
    box-shadow: 0 4px 30px rgba(0,102,139,0.05);
    border-radius: 16px; padding: 24px;
    position: relative; overflow: hidden; height: 100%;
}
.kpi-card::before {
    content: ''; position: absolute; top: -48px; right: -48px;
    width: 128px; height: 128px; border-radius: 50%;
    background: rgba(0,102,139,0.05); filter: blur(32px);
}
.kpi-card.tert::before { background: rgba(123,82,171,0.06); }
.kpi-label { color: #44474E; font-size: 0.78rem; font-weight: 600; margin-bottom: 14px; display: flex; justify-content: space-between; align-items: flex-start; }
.kpi-icon  { color: #00668B; font-size: 20px; }
.kpi-icon.t{ color: #7B52AB; }
.kpi-val   { font-size: 2rem; font-weight: 800; color: #1C1B1F; }
.kpi-sub   { font-size: 0.72rem; font-weight: 700; color: #00668B; margin-left: 8px; }
.kpi-sub.t { color: #7B52AB; }
.pb-bg     { width: 100%; height: 7px; background: #EAE7AC; border-radius: 999px; margin-top: 16px; overflow: hidden; }
.pb        { height: 100%; border-radius: 999px; background: #00668B; box-shadow: 0 0 10px rgba(0,102,139,0.35); }
.pb.t      { background: #7B52AB; box-shadow: 0 0 10px rgba(123,82,171,0.3); }

/* ── Insight box ── */
.insight-box {
    display: flex; gap: 12px; align-items: center;
    background: rgba(255,255,255,0.5); border: 1px solid rgba(0,102,139,0.2);
    border-radius: 14px; padding: 14px 18px; margin-top: 16px;
}
.insight-box .itext { font-size: 0.85rem; color: #44474E; line-height: 1.55; }
.insight-box .itext strong { color: #00668B; font-weight: 700; }

/* ── Promo items ── */
.promo-inner {
    background: rgba(255,255,255,0.4); border: 1px solid rgba(0,102,139,0.12);
    border-radius: 14px; padding: 16px; margin-bottom: 14px;
}
.promo-inner h4 { color: #00668B; font-weight: 800; font-size: 0.88rem; margin: 0 0 8px; }
.promo-inner ul { color: #44474E; font-size: 0.78rem; padding-left: 16px; margin: 4px 0 0; }
.promo-inner ul li { margin-bottom: 4px; }
.promo-inner ul li.accent { color: #00668B; font-weight: 700; }
.happy-hour {
    display: flex; gap: 12px; align-items: center;
    background: rgba(255,255,255,0.3); border: 1px solid rgba(123,82,171,0.2);
    border-radius: 12px; padding: 14px; margin-bottom: 14px;
}
.hh-title { color: #7B52AB; font-size: 0.8rem; font-weight: 800; }
.hh-body  { color: #44474E; font-size: 0.75rem; margin-top: 3px; line-height: 1.5; }
.upsell-box {
    background: rgba(255,255,255,0.85); border: 1px solid rgba(0,102,139,0.2);
    border-radius: 12px; padding: 14px; box-shadow: 0 2px 8px rgba(0,102,139,0.07);
}
.upsell-box .u-title { font-size: 0.7rem; font-weight: 700; color: #1C1B1F; margin-bottom: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.upsell-box .u-cta   { font-size: 0.7rem; font-weight: 800; color: #00668B; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.upsell-box .u-btn   {
    display: block; width: 100%; background: #00668B; color: white;
    padding: 20px; border-radius: 8px; font-size: 0.78rem; font-weight: 700;
    text-align: center; margin-top: 10px; box-sizing: border-box;
}

/* ── Menu card ── */
.menu-card {
    background: rgba(255,255,255,0.4);
    backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(0,102,139,0.1);
    box-shadow: 0 4px 24px rgba(0,102,139,0.04);
    border-radius: 16px; padding: 18px;
    display: flex; gap: 14px; align-items: center;
}
.menu-card.promote {
    background: rgba(255,255,255,0.65);
    backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(123,82,171,0.2);
}
.menu-card .mc-icon {
    width: 56px; height: 56px; border-radius: 12px;
    background: rgba(0,102,139,0.07); display: flex;
    align-items: center; justify-content: center;
    font-size: 26px; flex-shrink: 0;
}
.menu-card .mc-name  { font-size: 0.88rem; font-weight: 800; color: #1C1B1F; }
.menu-card .mc-badge { font-size: 0.68rem; font-weight: 800; }
.menu-card .mc-badge.p { color: #00668B; }
.menu-card .mc-badge.t { color: #7B52AB; }
.menu-card .mc-sold  { font-size: 0.75rem; color: #44474E; margin-top: 4px; }
.menu-card .mc-pct   { font-size: 0.75rem; font-weight: 700; color: #00668B; }
.menu-card .mc-pct.t { color: #7B52AB; }

/* ── Menu table ── */
.menu-tbl {
    width: 100%; border-collapse: collapse;
    border-radius: 14px; overflow: hidden;
    border: 1px solid rgba(0,102,139,0.1); margin-top: 24px;
}
.menu-tbl thead {
    background: #EAE7AC; color: #44474E;
    font-size: 0.68rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.07em;
}
.menu-tbl th, .menu-tbl td { padding: 13px 18px; text-align: left; }
.menu-tbl tbody tr { background: rgba(255,255,255,0.3); border-top: 1px solid rgba(0,0,0,0.04); }
.menu-tbl tbody tr:hover { background: rgba(0,102,139,0.03); }
.menu-tbl tbody tr.hl { background: rgba(123,82,171,0.04); }
.menu-tbl td { font-size: 0.83rem; color: #1C1B1F; }
.menu-tbl td.muted { color: #44474E; font-weight: 500; }
.bw  { display: inline-block; width: 52px; height: 5px; background: rgba(0,0,0,0.06); border-radius: 999px; overflow: hidden; vertical-align: middle; margin-right: 6px; }
.bf  { display: block; height: 100%; border-radius: 999px; background: #00668B; }
.bf.t{ background: #7B52AB; }

/* ── Timeline ── */
.tl-row {
    background: rgba(255,255,255,0.5); border: 1px solid rgba(0,102,139,0.08);
    border-left: 3px solid #00668B; border-radius: 10px;
    padding: 13px 18px; margin-bottom: 8px;
    display: flex; gap: 14px; align-items: baseline;
}
.tl-w { font-weight: 700; color: #00668B; min-width: 72px; font-size: 0.83rem; }
.tl-d { color: #44474E; font-size: 0.85rem; line-height: 1.5; }
</style>
""", unsafe_allow_html=True)

# ── 데이터 ──────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_excel("돼지갈비_식당_매출데이터.xlsx")
    df["날짜"] = pd.to_datetime(df["날짜"])
    return df

df = load_data()

CHART = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(255,255,255,0.3)",
    font=dict(family="Inter", color="#44474E", size=12),
    title_font=dict(color="#1C1B1F", size=14, family="Inter"),
    xaxis=dict(gridcolor="rgba(0,0,0,0.04)", linecolor="rgba(0,102,139,0.08)", tickfont=dict(color="#44474E")),
    yaxis=dict(gridcolor="rgba(0,0,0,0.04)", linecolor="rgba(0,102,139,0.08)", tickfont=dict(color="#44474E")),
    legend=dict(bgcolor="rgba(255,255,255,0.6)", bordercolor="rgba(0,102,139,0.1)", borderwidth=1, font=dict(color="#44474E")),
)

# ── 날씨 API ────────────────────────────────────────────────
@st.cache_data(ttl=600)
def fetch_weather():
    url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=37.5665&longitude=126.9780"
        "&current=temperature_2m&hourly=temperature_2m"
        "&timezone=Asia%2FSeoul&forecast_days=1"
    )
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            return json.loads(r.read())
    except Exception:
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            with urllib.request.urlopen(url, timeout=10, context=ctx) as r:
                return json.loads(r.read())
        except Exception as e:
            return {"error": str(e)}

weather = fetch_weather()

# ── 사이드바 ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
<div style="margin-bottom:24px;padding:0 4px;">
  <div style="display:flex;align-items:center;gap:12px;">
    <div style="width:40px;height:40px;border-radius:12px;background:rgba(0,102,139,0.1);
                border:1px solid rgba(0,102,139,0.2);display:flex;align-items:center;
                justify-content:center;font-size:18px;flex-shrink:0;">🍖</div>
    <div>
      <div style="font-size:0.95rem;font-weight:800;color:#00668B;">배사의 돼지갈비</div>
      <div style="font-size:0.7rem;color:#44474E;font-weight:500;">프리미엄 한돈 돼지갈비</div>
    </div>
  </div>
</div>
<nav style="display:flex;flex-direction:column;gap:2px;margin-bottom:16px;">
  <a href="#" style="display:flex;align-items:center;gap:10px;padding:10px 12px;color:#44474E;
     text-decoration:none;border-radius:10px;font-size:0.85rem;font-weight:500;">
    <span class="material-symbols-outlined" style="font-size:20px;">dashboard</span>Dashboard
  </a>
  <a href="#" style="display:flex;align-items:center;gap:10px;padding:10px 12px;color:#00668B;
     background:rgba(0,102,139,0.08);border:1px solid rgba(0,102,139,0.15);
     text-decoration:none;border-radius:10px;font-size:0.85rem;font-weight:700;">
    <span class="material-symbols-outlined" style="font-size:20px;font-variation-settings:'FILL' 1;">analytics</span>Analytics
  </a>
  <a href="#" style="display:flex;align-items:center;gap:10px;padding:10px 12px;color:#44474E;
     text-decoration:none;border-radius:10px;font-size:0.85rem;font-weight:500;">
    <span class="material-symbols-outlined" style="font-size:20px;">restaurant_menu</span>Menu
  </a>
  <a href="#" style="display:flex;align-items:center;gap:10px;padding:10px 12px;color:#44474E;
     text-decoration:none;border-radius:10px;font-size:0.85rem;font-weight:500;">
    <span class="material-symbols-outlined" style="font-size:20px;">campaign</span>Promotions
  </a>
  <a href="#" style="display:flex;align-items:center;gap:10px;padding:10px 12px;color:#44474E;
     text-decoration:none;border-radius:10px;font-size:0.85rem;font-weight:500;">
    <span class="material-symbols-outlined" style="font-size:20px;">cloud</span>Weather
  </a>
  <a href="#" style="display:flex;align-items:center;gap:10px;padding:10px 12px;color:#44474E;
     text-decoration:none;border-radius:10px;font-size:0.85rem;font-weight:500;">
    <span class="material-symbols-outlined" style="font-size:20px;">settings</span>Settings
  </a>
</nav>
<div style="border-top:1px solid rgba(0,102,139,0.1);padding-top:16px;">
  <button style="width:100%;padding:12px;background:#00668B;color:white;border:none;
    border-radius:12px;font-weight:700;font-size:0.85rem;cursor:pointer;
    display:flex;align-items:center;justify-content:center;
    box-shadow:0 4px 14px rgba(0,102,139,0.25);margin-bottom:8px;">
    Create New Event
  </button>
</div>
""", unsafe_allow_html=True)

    # 날씨 위젯
    if "error" not in weather:
        temp = weather["current"]["temperature_2m"]
        st.markdown(f"""
<div style="background:rgba(255,255,255,0.4);border:1px solid rgba(0,102,139,0.1);
            border-radius:14px;padding:14px;text-align:center;margin-top:8px;">
  <div style="font-size:0.7rem;color:#44474E;font-weight:600;margin-bottom:4px;">서울 현재 기온</div>
  <div style="font-size:1.8rem;font-weight:800;color:#00668B;">{temp}°C</div>
</div>
""", unsafe_allow_html=True)

# ── 상단 헤더 ────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;justify-content:space-between;align-items:center;
            padding-bottom:20px;border-bottom:1px solid rgba(0,102,139,0.08);margin-bottom:24px;">
  <div>
    <div style="font-size:1.2rem;font-weight:800;color:#1C1B1F;letter-spacing:-0.3px;">
      평일 매출 활성화 프로젝트
    </div>
    <div style="display:flex;gap:20px;margin-top:8px;">
      <a href="#" style="color:#44474E;font-size:0.82rem;font-weight:500;text-decoration:none;">Live View</a>
      <a href="#" style="color:#00668B;font-size:0.82rem;font-weight:700;text-decoration:none;
                         border-bottom:2px solid #00668B;padding-bottom:2px;">Analytics</a>
      <a href="#" style="color:#44474E;font-size:0.82rem;font-weight:500;text-decoration:none;">Promotions</a>
    </div>
  </div>
  <div style="background:#EAE7AC;border:1px solid rgba(196,199,197,0.4);border-radius:999px;
              padding:6px 14px;font-size:0.74rem;color:#44474E;font-weight:500;
              display:flex;align-items:center;gap:6px;">
    <span class="material-symbols-outlined" style="font-size:14px;">calendar_today</span>
    Jan 01 – Jun 29, 2025
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPI 카드 3개 ─────────────────────────────────────────────
kpis = [
    ("평일 매출 성장률 (Target: 20%)", "trending_up", "+14.2%", "목표 대비 71% 달성", "p", 71),
    ("객단가 상승 (ATV Increase)",      "payments",    "+12.8%", "Target: 15%",         "t", 85),
    ("된장찌개 주문 전환율",             "restaurant",  "+18.5%", "Target: 25%",         "p", 74),
]
k1, k2, k3 = st.columns(3)
for col, (label, icon, val, sub, cls, pct) in zip([k1, k2, k3], kpis):
    icon_color = "#00668B" if cls == "p" else "#7B52AB"
    sub_cls    = "" if cls == "p" else "t"
    card_cls   = "" if cls == "p" else "tert"
    with col:
        st.markdown(f"""
<div class="kpi-card {card_cls}">
  <div class="kpi-label">
    {label}
    <span class="material-symbols-outlined kpi-icon {sub_cls}">{icon}</span>
  </div>
  <div>
    <span class="kpi-val">{val}</span>
    <span class="kpi-sub {sub_cls}">{sub}</span>
  </div>
  <div class="pb-bg"><div class="pb {sub_cls}" style="width:{pct}%;"></div></div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

# ── 요일별 매출 차트 + 프로모션 센터 ────────────────────────
DOW_ORDER = ["월", "화", "수", "목", "금", "토", "일"]
dow_sales = (
    df.groupby("요일")["금액(원)"].sum()
    .reindex(DOW_ORDER).reset_index()
)
dow_sales.columns = ["요일", "매출합계"]
dow_sales["색상"] = dow_sales["요일"].apply(
    lambda x: "주말" if x in ["토", "일"]
    else "포커스" if x in ["월", "수"] else "평일"
)

chart_col, promo_col = st.columns([8, 4], gap="large")

with chart_col:
    st.markdown("""
<div style="font-size:1.05rem;font-weight:800;color:#1C1B1F;margin-bottom:4px;">
  요일별 매출 격차 분석
</div>
<div style="font-size:0.82rem;color:#44474E;margin-bottom:2px;">
  일요일 대비 월요일 매출이 49.5% 낮습니다.
</div>
""", unsafe_allow_html=True)

    fig_dow = px.bar(
        dow_sales, x="요일", y="매출합계",
        color="색상",
        color_discrete_map={
            "포커스": "#00668B",
            "평일":   "rgba(0,102,139,0.22)",
            "주말":   "rgba(123,82,171,0.25)",
        },
        text=dow_sales["매출합계"].apply(lambda x: f"{x/10000:.0f}만"),
        category_orders={"요일": DOW_ORDER},
    )
    fig_dow.update_traces(textposition="outside", textfont=dict(color="#44474E", size=11))
    fig_dow.update_layout(
        showlegend=False, xaxis_title="", yaxis_title="매출(원)",
        height=280, margin=dict(l=0, r=0, t=14, b=0),
        **CHART,
    )
    st.plotly_chart(fig_dow, use_container_width=True)

    st.markdown("""
<div class="insight-box">
  <span class="material-symbols-outlined" style="color:#00668B;font-size:22px;flex-shrink:0;">lightbulb</span>
  <div class="itext">
    월요일 매출이 현저히 낮습니다.
    <strong>'월화수목 고기 파티'</strong> 프로모션을 통해 직장인 회식 수요를 집중 공략하세요.
  </div>
</div>
""", unsafe_allow_html=True)

with promo_col:
    st.markdown("""
<div class="glass-panel-elevated">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:18px;">
    <div style="font-size:1rem;font-weight:800;color:#1C1B1F;">Promotion</div>
    <span style="padding:3px 12px;background:#00668B;color:white;font-size:0.65rem;
                 font-weight:700;border-radius:999px;letter-spacing:0.05em;text-transform:uppercase;">
      Active
    </span>
  </div>

  <div style="margin-bottom:16px;">
    <div style="color:#00668B;font-weight:800;font-size:0.88rem;margin-bottom:4px;">월화수목 고기 파티</div>
    <div style="color:#44474E;font-size:0.78rem;line-height:1.6;">
      평일 회식/모임 고객 타겟 — 특별 세트 및 타임세일 구성
    </div>
  </div>

  <div class="promo-inner">
    <h4>삼소 찌개 세트 구성</h4>
    <ul>
      <li>삼겹살 2인분 + 소주 1병</li>
      <li>된장찌개 + 공기밥 1개</li>
      <li class="accent">단품 대비 12% 할인 적용</li>
    </ul>
  </div>

  <div class="happy-hour">
    <div>
      <div class="hh-title">월/수 Happy Hour</div>
      <div class="hh-body">17:00 ~ 19:00</div>
      <div class="hh-body">고기 3인분 이상 주문 시 주류 1,000원</div>
    </div>
  </div>

  <div style="margin-bottom:0;">
    <div style="font-size:0.78rem;font-weight:700;color:#1C1B1F;margin-bottom:10px;">
      메뉴판 UP-SELL 예시
    </div>
    <div class="upsell-box">
      <div class="u-title">삼겹살 2인분이 장바구니에 담겼습니다.</div>
      <div style="border-top:1px solid rgba(0,0,0,0.05);padding-top:8px;margin-top:8px;">
        <div class="u-cta">"된장찌개 단돈 3,000원 추가!"</div>
        <div class="u-btn">+ 추가하기</div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── 메뉴 퍼포먼스 ────────────────────────────────────────────
st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
st.markdown("""
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
  <div style="font-size:1.05rem;font-weight:800;color:#1C1B1F;">Menu Performance</div>
  <div style="font-size:0.82rem;font-weight:700;color:#44474E;">Total Items: 10</div>
</div>
""", unsafe_allow_html=True)

menu_rev = df.groupby("메뉴")["금액(원)"].sum().sort_values(ascending=False)
menu_qty_s = df.groupby("메뉴")["수량(테이블 수)"].sum()

# 상단 3개 카드
mc1, mc2, mc3 = st.columns(3)
top_cards = [
    (mc1, "삼겹살 계열", "🥩", int(menu_qty_s.get("삼겹살 2인분", 0) + menu_qty_s.get("삼겹살 1인분", 0)), "+12%", "Top Seller", "p", ""),
    (mc2, "소주 1병",    "🍶", int(menu_qty_s.get("소주 1병", 0)),   "+5%",    "Steady",     "p", ""),
    (mc3, "된장찌개",    "🍲", int(menu_qty_s.get("된장찌개", 0)),   "+18.5%", "Promote",    "t", "promote"),
]
for col, name, icon, qty, chg, badge, cls, card_extra in top_cards:
    bc = "#00668B" if cls == "p" else "#7B52AB"
    with col:
        st.markdown(f"""
<div class="menu-card {card_extra}">
  <div class="mc-icon">{icon}</div>
  <div style="flex:1;">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;">
      <div class="mc-name">{name}</div>
      <div class="mc-badge {cls}">{badge}</div>
    </div>
    <div style="display:flex;justify-content:space-between;margin-top:6px;">
      <div class="mc-sold">Sold: {qty:,}</div>
      <div class="mc-pct {cls}">{chg}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# 메뉴 전체 테이블
all_menu = pd.DataFrame({
    "메뉴":   menu_rev.index,
    "매출":   menu_rev.values,
    "수량":   [int(menu_qty_s.get(m, 0)) for m in menu_rev.index],
})
all_menu["전환율"] = (all_menu["수량"] / all_menu["수량"].max() * 100).round(0).astype(int)
cat_map = {
    "돼지갈비 1인분": "Meat", "돼지갈비 2인분": "Meat",
    "삼겹살 1인분": "Meat",   "삼겹살 2인분": "Meat",
    "냉면": "Noodle",         "된장찌개": "Side",
    "공기밥": "Rice",          "막걸리 1병": "Drink",
    "소주 1병": "Drink",       "음료수": "Drink",
}
all_menu["카테고리"] = all_menu["메뉴"].map(cat_map)

rows = ""
for _, r in all_menu.iterrows():
    is_dj = r["메뉴"] == "된장찌개"
    tr_c  = "hl" if is_dj else ""
    nm_s  = "color:#7B52AB;font-weight:800;" if is_dj else "font-weight:700;"
    bf_c  = "t" if is_dj else ""
    badge = f'<span style="font-size:0.66rem;font-weight:800;color:{"#7B52AB" if is_dj else "#00668B"};">{"Promote" if is_dj else "Active"}</span>'
    action= f'<span style="font-size:0.75rem;font-weight:{"800" if is_dj else "700"};color:{"#7B52AB" if is_dj else "#00668B"};cursor:pointer;">{"Boost Now" if is_dj else "Details"}</span>'
    rows += f"""
<tr class="{tr_c}">
  <td style="{nm_s}">{badge}&nbsp;{r['메뉴']}</td>
  <td class="muted">{r['카테고리']}</td>
  <td>{r['매출']:,.0f} ₩</td>
  <td>
    <span class="bw"><span class="bf {bf_c}" style="width:{r['전환율']}%;"></span></span>
    <span style="font-weight:700;color:{'#7B52AB' if is_dj else '#1C1B1F'};">{r['전환율']}%</span>
  </td>
  <td>{action}</td>
</tr>"""

st.markdown(f"""
<table class="menu-tbl">
  <thead><tr>
    <th>Menu Item</th><th>Category</th><th>Revenue</th><th>상대 전환율</th><th>Action</th>
  </tr></thead>
  <tbody>{rows}</tbody>
</table>
""", unsafe_allow_html=True)

# ── 날씨 (접이식) ────────────────────────────────────────────
st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
if "error" not in weather:
    with st.expander("☀️ 서울 오늘 시간별 기온", expanded=False):
        now_hour = datetime.now().hour
        hourly_df = pd.DataFrame({
            "시간": [h[11:16] for h in weather["hourly"]["time"]],
            "기온(°C)": weather["hourly"]["temperature_2m"],
        })
        fig_w = px.line(
            hourly_df, x="시간", y="기온(°C)", markers=True,
            color_discrete_sequence=["#00668B"],
        )
        fig_w.add_shape(
            type="line",
            x0=f"{now_hour:02d}:00", x1=f"{now_hour:02d}:00",
            y0=0, y1=1, xref="x", yref="paper",
            line=dict(color="#7B52AB", dash="dash", width=2),
        )
        fig_w.add_annotation(
            x=f"{now_hour:02d}:00", y=1.08, yref="paper",
            text="현재", showarrow=False,
            font=dict(color="#7B52AB", size=11),
            xanchor="center", yanchor="bottom",
        )
        # x축 3시간 간격으로만 표시해 겹침 방지
        tick_vals = [h for h in hourly_df["시간"] if int(h[:2]) % 3 == 0]
        fig_w.update_layout(
            xaxis=dict(
                tickmode="array", tickvals=tick_vals,
                ticktext=tick_vals,
                gridcolor="rgba(0,0,0,0.04)",
                linecolor="rgba(0,102,139,0.08)",
                tickfont=dict(color="#44474E"),
            ),
            xaxis_title="시간", yaxis_title="기온 (°C)",
            height=260, margin=dict(l=0, r=0, t=32, b=0),
            **{k: v for k, v in CHART.items() if k != "xaxis"},
        )
        st.plotly_chart(fig_w, use_container_width=True)

# ── 타임라인 ─────────────────────────────────────────────────
with st.expander("📆 실행 타임라인 — 평일 프로모션 로드맵", expanded=True):
    for week, desc in [
        ("Week 1",   "세트 메뉴 단가·마진율 시뮬레이션 및 POS 시스템 메뉴 등록"),
        ("Week 2",   "평일 프로모션 배너 및 메뉴판 수정, 네이버 플레이스 소식 홍보"),
        ("Week 3~6", "평일 한정 프로모션 시범 운영 (4주간)"),
        ("Week 7",   "데이터 재추출 — 매출 상승 기여도 평가 및 정식 메뉴 채택 결정"),
    ]:
        st.markdown(f"""
<div class="tl-row">
  <span class="tl-w">{week}</span>
  <span class="tl-d">{desc}</span>
</div>""", unsafe_allow_html=True)

# ── 푸터 ────────────────────────────────────────────────────
st.markdown("""
<div style="padding:28px 0 12px;text-align:center;color:#74777F;font-size:0.73rem;
            font-weight:500;opacity:0.7;border-top:1px solid rgba(0,102,139,0.08);margin-top:24px;">
  © 2025 Glacier Kitchen Dashboard · Analytics based on POS data (Jan 01 – Jun 29, 2025)
</div>
""", unsafe_allow_html=True)
