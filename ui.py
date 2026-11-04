"""Presentation helpers for the Trace-Gate Streamlit demo frontend."""

from html import escape
import streamlit as st


def safe(value):
    return escape(str(value), quote=True)


def apply_styles():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@500;600;700;800&display=swap');
:root { color-scheme: light; }
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] { background: #F6F8FC !important; color: #19243A; }
html, body, input, button, textarea { font-family: 'DM Sans', sans-serif !important; }
h1,h2,h3,h4 { font-family: 'Manrope', 'DM Sans', sans-serif !important; letter-spacing:-.035em; color:#17243B !important; }
[data-testid="stAppViewContainer"] .block-container { max-width: 1500px; padding-top: 2.15rem; padding-left: 3rem; padding-right: 3rem; padding-bottom: 5rem; }
[data-testid="stSidebar"] { background: #FFFFFF !important; border-right: 1px solid #E6EBF4; }
[data-testid="stSidebar"] > div:first-child { padding-top: 1.25rem; }
[data-testid="stSidebarNav"] a { border-radius: 12px !important; padding: .7rem .85rem !important; font-weight: 600; }
[data-testid="stSidebarNav"] a[aria-current="page"] { background:#EEF0FF !important; color:#4338CA !important; }
[data-testid="stSidebarNav"] a:hover { background:#F5F7FE !important; }
[data-testid="stMetric"] { background:#FFFFFF; border:1px solid #E7ECF5; border-radius:17px; padding: 1rem 1.2rem; box-shadow:0 5px 16px rgba(31,48,91,.025); }
[data-testid="stMetricLabel"] { font-size:.78rem; color:#78859B; font-weight:600; }
[data-testid="stMetricValue"] { font-family:'Manrope', sans-serif; font-weight:800; letter-spacing:-.04em; color:#1C2B46; }
[data-testid="stVerticalBlockBorderWrapper"] > div { border-radius:18px !important; border-color:#E7ECF5 !important; background:#FFFFFF; }
[data-testid="stForm"] { background: #FFFFFF; border:1px solid #E5EAF3; border-radius:18px; padding:1.25rem 1.5rem; }
[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea, [data-baseweb="select"] > div, [data-testid="stNumberInput"] input { background:#FBFCFF !important; border:1px solid #DFE6F2 !important; border-radius:11px !important; min-height:43px; }
[data-testid="stFileUploader"] { border-radius:14px; }
[data-testid="stFileUploaderDropzone"] { background:#F8FAFF !important; border-radius:14px; border:1px dashed #BBC6E3 !important; }
.stButton > button[kind="primary"], [data-testid="stFormSubmitButton"] button[kind="primary"] { background:linear-gradient(115deg,#5146E6,#7064EF) !important; color:white !important; border:0 !important; box-shadow:0 7px 18px rgba(79,70,229,.15); }
.stButton > button, [data-testid="stFormSubmitButton"] button { border-radius:11px; font-weight:700; min-height:41px; }
button:hover { transform:translateY(-1px); transition:transform .14s ease; }
[data-testid="stDataFrame"] { border-radius:14px; overflow:hidden; border:1px solid #E7ECF5; }
[data-testid="stTabs"] [data-baseweb="tab-list"] { gap: 1rem; border-bottom:1px solid #DFE7F3; }
[data-testid="stTabs"] button[role="tab"] { font-weight:700; padding:.7rem .35rem; }
[data-testid="stAlert"] { border-radius:12px; }
hr { border-color:#E8EDF5 !important; }
.tg-brand { display:flex; align-items:center; gap:11px; margin:8px 0 15px; padding: 6px 8px; }
.tg-logo { display:flex; align-items:center; justify-content:center; width:38px; height:38px; background:linear-gradient(145deg,#5E52F0,#9287F9); color:white; border-radius:12px; font-size:22px; box-shadow:0 8px 18px rgba(88,70,230,.18); }
.tg-brand-name { font-family:'Manrope',sans-serif; font-size:1.17rem; font-weight:800; color:#1A2740; letter-spacing:-.04em; }
.tg-brand-small { font-size:.68rem; color:#8C97AB; letter-spacing:.065em; font-weight:800; }
.tg-side-note { color:#8490A4; font-size:.78rem; padding:12px 10px; margin-top:4px; line-height:1.55; }
.tg-eyebrow { font-weight:800; color:#6B61D8; text-transform:uppercase; letter-spacing:.11em; font-size:.71rem; margin-bottom:.55rem; }
.tg-page-title { font-family:'Manrope',sans-serif; font-size:2.05rem; font-weight:800; letter-spacing:-.055em; color:#1D2B46; line-height:1.16; margin-bottom:.55rem; }
.tg-subhead { color:#7A879D; font-size:.95rem; line-height:1.6; margin-bottom:1.5rem; }
.tg-hero { padding: 1.6rem 2rem; border-radius:22px; border:1px solid #E4E7F7; background:linear-gradient(115deg,#FFFFFF 15%,#EEF0FF 72%,#E6F2FF 100%); display:flex; justify-content:space-between; gap:14px; margin-bottom:1.5rem; box-shadow:0 10px 28px rgba(43,54,108,.04); }
.tg-hero h1 { font-size:2rem; margin:0 0 .4rem; font-weight:800; }
.tg-hero p { color:#6D7890; max-width:670px; margin:0; font-size:.94rem; line-height:1.6; }
.tg-hero-symbol { color:#7165E8; font-size:4rem; opacity:.27; align-self:center; }
.tg-section { margin:1.6rem 0 .72rem; font-weight:800; font-size:1.13rem; font-family:'Manrope',sans-serif; letter-spacing:-.03em; color:#1F2B44; }
.tg-card { padding:1.15rem 1.2rem; border:1px solid #E6EBF4; border-radius:16px; background:white; box-shadow:0 5px 15px rgba(20,40,80,.028); margin:.35rem 0; }
.tg-card-title { color:#263550; font-weight:800; font-size:.95rem; margin-bottom:.28rem; }
.tg-muted { color:#7A879B; font-size:.84rem; line-height:1.5; }
.tg-stepper { display:flex; flex-wrap:wrap; gap:9px; margin: 0 0 1.5rem; }
.tg-step { background:#fff; border:1px solid #E7ECF5; border-radius:999px; color:#728097; padding:8px 13px; font-size:.77rem; font-weight:700; }
.tg-step-current { background:#EEF0FF; border-color:#C9CCFF; color:#4F46E5; }
.tg-pill { display:inline-block; padding:5px 10px; border-radius:999px; font-size:.74rem; font-weight:800; }
.tg-pill-approved { background:#E5F8ED; color:#198253; }
.tg-pill-pending { background:#FFF2DB; color:#A66916; }
.tg-pill-rejected { background:#FDE9EB; color:#C04456; }
.tg-pill-draft { background:#EEF1F7; color:#64748B; }
.tg-pill-review { background:#EEF0FF; color:#6255C6; }
.tg-foot { color:#9AA5B6; font-size:.75rem; margin:2rem 0 0; padding:1rem 0; border-top:1px solid #E8EDF5; }
@media (max-width:900px) { [data-testid="stAppViewContainer"] .block-container { padding: 1.1rem 1rem 3rem; } .tg-hero { padding:1.2rem; } .tg-hero-symbol{display:none;} .tg-page-title{font-size:1.65rem;} }
</style>
""", unsafe_allow_html=True)


def hero(kicker, title, subtitle, symbol="✦"):
    st.markdown(
        '<div class="tg-hero"><div>'
        f'<div class="tg-eyebrow">{safe(kicker)}</div>'
        f'<h1>{safe(title)}</h1><p>{safe(subtitle)}</p>'
        '</div>'
        f'<div class="tg-hero-symbol">{safe(symbol)}</div></div>',
        unsafe_allow_html=True,
    )


def section(title):
    st.markdown(f'<div class="tg-section">{safe(title)}</div>', unsafe_allow_html=True)


def pill(value):
    value = str(value or "DRAFT").upper()
    style = "tg-pill-" + ({"APPROVED":"approved", "PENDING":"pending", "REJECTED":"rejected", "DRAFT":"draft", "NOT_CHECKED":"review", "REVIEW_REQUIRED":"review"}.get(value, "draft"))
    return f'<span class="tg-pill {style}">{safe(value)}</span>'


def info_card(title, detail):
    st.markdown(f'<div class="tg-card"><div class="tg-card-title">{safe(title)}</div><div class="tg-muted">{safe(detail)}</div></div>', unsafe_allow_html=True)


def steps(active=1):
    names = ["01  Register vendor", "02  Validate & submit", "03  Upload documents", "04  Procurement review"]
    content = "".join(f'<span class="tg-step {"tg-step-current" if i == active else ""}">{safe(name)}</span>' for i,name in enumerate(names,1))
    st.markdown(f'<div class="tg-stepper">{content}</div>', unsafe_allow_html=True)


def footer():
    st.markdown('<div class="tg-foot">TRACE-GATE · Procurement intelligence workspace · Demo environment using synthetic screening rules. Automated decisions are not government or sanctions verification.</div>', unsafe_allow_html=True)
