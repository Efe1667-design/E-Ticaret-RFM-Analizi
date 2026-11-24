from pathlib import Path
import io
from html import escape
import unicodedata
import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="E-Ticaret | RFM Yönetim Paneli", page_icon="📊", layout="wide", initial_sidebar_state="expanded")
st.markdown('<style>\n:root{color-scheme:dark;--ink:#f5f4fc;--muted:#a5a5bd;--accent:#b49aff;--edge:#37354d}\n.stApp,[data-testid="stAppViewContainer"]{background:radial-gradient(ellipse at 85% 0%,#25203d 0%,#0c0d19 42%);color:var(--ink)}\n[data-testid="stHeader"]{background:transparent}\n[data-testid="stSidebar"]{background:#11121f;border-right:1px solid var(--edge)}\n[data-testid="stSidebar"] [data-testid="stSidebarContent"]{padding-top:1rem}\n.stApp h1,.stApp h2,.stApp h3,.stApp p,.stApp label{color:var(--ink)}\n.stApp h1{letter-spacing:-1.5px;font-weight:750}\n[data-testid="stCaptionContainer"] p{color:var(--muted)}\n[data-testid="stMetric"],.rfm-kpi,[data-testid="stPlotlyChart"],[data-testid="stDataFrame"]{background:linear-gradient(145deg,#1a1b2d,#141523);border:1px solid var(--edge);border-radius:12px;padding:0;transition:border-color .35s ease,box-shadow .35s ease,transform .35s ease}\n[data-testid="stMetric"]:hover,.rfm-kpi:hover,[data-testid="stPlotlyChart"]:hover,[data-testid="stDataFrame"]:hover{border-color:var(--accent);box-shadow:0 0 20px #a385ff40,inset 0 0 12px #a385ff0d;}\n[data-testid="stMetricValue"]>div{font-size:clamp(17px,2vw,28px);white-space:normal;overflow-wrap:anywhere;color:var(--ink)}\n[data-testid="stMetricLabel"] p{color:var(--muted)}\n.rfm-kpi{min-height:116px}.rfm-kpi-top{display:flex;align-items:center;justify-content:space-between;color:var(--muted);font-size:13px;gap:8px}.rfm-kpi-top svg{width:24px;height:24px;flex-shrink:0}.rfm-kpi-value{font-size:clamp(18px,2.2vw,30px);font-weight:750;margin-top:12px;overflow-wrap:anywhere;letter-spacing:-.6px}.rfm-kpi small{color:var(--muted)}\n.rfm-hero{padding:20px 0 16px;position:relative;overflow:hidden}.rfm-hero h1{font-size:clamp(28px,4vw,52px);margin:6px 0}.rfm-hero span{color:var(--accent)}.rfm-hero p{color:var(--muted);max-width:620px}.rfm-eyebrow{letter-spacing:2px;font-size:11px;color:#b5a8db}.rfm-brand{display:flex;gap:10px;align-items:center;font-size:23px;font-weight:750;color:var(--ink)}.rfm-brand svg{width:30px;height:30px}\n[data-testid="stButton"] button,[data-testid="stDownloadButton"] button{background:#211e35;color:var(--ink);border:1px solid #51456d;border-radius:8px;transition:all .25s ease}\n[data-testid="stButton"] button:hover,[data-testid="stDownloadButton"] button:hover{border-color:var(--accent);box-shadow:0 0 12px #a385ff40;color:#fff}\n[data-baseweb="select"]>div,[data-baseweb="input"]>div{background:#191a2b;color:var(--ink);border-color:var(--edge)}\n[data-testid="stMainBlockContainer"]{padding-top:3rem}\n@keyframes rfm-in{from{opacity:.25;transform:translateY(5px)}to{opacity:1;transform:translateY(0)}}\n@media(prefers-reduced-motion:reduce){.stApp *{animation:none!important;transition:none!important;transform:none!important}}\n\n[data-testid="stMetric"],.rfm-kpi{padding:14px}\n[data-testid="stPlotlyChart"]{overflow:visible!important;padding:0!important;min-width:0}\n[data-testid="stCaptionContainer"] p{color:#b7b9d0!important}\n[data-testid="stSidebar"] [data-testid="stButton"] button{width:100%;justify-content:flex-start;text-align:left;background:transparent;border-color:transparent;padding:10px 12px;min-height:42px}\n[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"]{background:#352b53;border-color:#7563a7;color:#fff}\n[data-testid="stSidebar"] [data-testid="stButton"] button:hover{background:#28223e;border-color:#b49aff;box-shadow:0 0 14px #a385ff40}\n[data-testid="stSidebar"] [data-testid="stButton"] button span[data-testid="stIconMaterial"]{color:#c4b5fd}\n.rfm-table-wrap{max-height:480px;overflow:auto;padding-right:16px;padding-bottom:12px;scrollbar-gutter:stable;border:1px solid #414057;border-radius:12px;background:#151b30;transition:box-shadow .35s,border-color .35s}\n.rfm-table-wrap:hover{border-color:#b49aff;box-shadow:0 0 18px #a385ff40}\n.rfm-table{border-collapse:separate;border-spacing:0;width:100%;font-size:14px;color:#f1f2fc;font-variant-numeric:tabular-nums}\n.rfm-table th{position:sticky;top:0;background:#30294b;color:#e0d5ff;text-align:left;z-index:1;white-space:nowrap}\n.rfm-table td,.rfm-table th{padding:12px 16px;border-bottom:1px solid #343b55}\n.rfm-table td{background:#1b2339;min-width:85px}.rfm-table tr:nth-child(even) td{background:#222b43}.rfm-table tr:hover td{background:#34314f}\n.rfm-table td:last-child{min-width:130px;max-width:520px;white-space:normal}.rfm-table td.num{text-align:right;white-space:nowrap}\n.rfm-table-wrap::-webkit-scrollbar{width:9px;height:9px}.rfm-table-wrap::-webkit-scrollbar-thumb{background:#777095;border-radius:8px;border:2px solid #151b30}\n[data-testid="stDownloadButton"] button{width:100%;min-height:48px}\n</style><span class="rfm-style-anchor"></span>', unsafe_allow_html=True)
st.markdown('<style>[data-testid="stPlotlyChart"]{overflow:hidden!important;padding:0!important;box-sizing:border-box;scrollbar-width:none!important;border:1px solid #414057!important;border-radius:12px!important;transform:none!important}\n[data-testid="stPlotlyChart"]:hover{border-color:#b49aff!important}\n[data-testid="stPlotlyChart"] *{scrollbar-width:none!important}\n[data-testid="stPlotlyChart"]::-webkit-scrollbar,[data-testid="stPlotlyChart"] *::-webkit-scrollbar{display:none!important}\n[data-testid="stPlotlyChart"] .modebar{top:8px!important;right:8px!important}\n[data-testid="stPlotlyChart"] .modebar-group{background:transparent!important}\n[data-testid="stPlotlyChart"] .modebar-btn path{fill:#b9b1dc!important}\n[data-testid="stPlotlyChart"] .modebar-btn:hover path{fill:#ffffff!important}\n</style><span class="rfm-style-anchor"></span>', unsafe_allow_html=True)
st.markdown('<style>\n.rfm-table-wrap{padding:0!important;scrollbar-gutter:auto!important;isolation:isolate;background:#1b2339;max-height:480px;overflow:auto;}\n.rfm-table{width:100%!important;margin:0!important;border:0!important;border-collapse:separate!important;border-spacing:0!important;}\n.rfm-table thead{position:sticky;top:0;z-index:10;background:#30294b!important;}\n.rfm-table thead th{position:static!important;background:#30294b!important;opacity:1!important;box-shadow:0 1px 0 #51466c;}\n.rfm-table td:last-child{max-width:none;padding-right:24px;}\n.rfm-table-wrap::-webkit-scrollbar{width:8px;height:8px;}\n[data-testid="stElementContainer"]:has([data-testid="stPlotlyChart"]) [data-testid="stElementToolbar"], [data-testid="stPlotlyChart"] [data-testid="stElementToolbar"],[data-testid="stPlotlyChart"] [data-testid="stElementToolbarButton"]{display:none!important;}\n\n[data-testid="stDialog"] [data-testid="stModal"]{backdrop-filter:blur(7px);}\n[data-testid="stDialog"] [data-testid="stPlotlyChart"]{border:0!important;box-shadow:none!important;}\n</style><span class="rfm-style-anchor"></span>', unsafe_allow_html=True)
st.markdown('<style>\n[data-testid="stDialog"] [data-baseweb="modal"] [role="dialog"], [data-testid="stDialog"] [data-baseweb="modal"] [data-baseweb="modal-body"], [data-testid="stDialog"] [data-baseweb="modal"] [data-baseweb="modal-header"]{background:#191a2b!important;}\n[data-testid="stDialog"] [data-baseweb="modal"] [role="dialog"]{width:min(1050px,90vw)!important;max-width:90vw!important;border:1px solid #7563a7;border-radius:18px;box-shadow:0 20px 80px #0009;}\n[data-testid="stDialog"] [data-testid="stVerticalBlock"]{width:100%!important;max-width:none!important;background:transparent!important;border:0!important;box-shadow:none!important;}\n[data-testid="stDialog"] [data-baseweb="modal"] [role="dialog"] > div{background:#191a2b!important;}\n[data-testid="stDialog"] [aria-label="Close"]{color:#e0d5ff!important;}\n.rfm-table-wrap{max-height:470px;overflow:auto;scrollbar-gutter:auto!important;padding:0!important;background:#1b2339;}\n.rfm-table{width:100%!important;table-layout:auto!important;border-collapse:separate!important;border-spacing:0!important;}\n.rfm-table th,.rfm-table td{padding:9px 12px!important;line-height:1.4!important;font-size:13px!important;min-width:0!important;max-width:none!important;white-space:nowrap!important;border-right:0!important;}\n.rfm-table thead{position:sticky!important;top:0!important;z-index:20!important;background:#30294b!important;}\n.rfm-table thead th{background:#30294b!important;opacity:1!important;}\n.rfm-table td:last-child{padding-right:14px!important;}\n.rfm-table td.rfm-note{min-width:260px!important;max-width:420px!important;}\n.rfm-note span{display:block;max-width:380px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}\n.rfm-table-wrap::-webkit-scrollbar{width:8px;height:8px;}\n</style><span class="rfm-style-anchor"></span>', unsafe_allow_html=True)
px.defaults.color_discrete_sequence = ["#a78bfa", "#60a5fa", "#5cdbb0", "#f4b86a", "#e78bb9", "#818cf8", "#94a3b8"]
st.markdown('<style>\n[data-testid="stMainBlockContainer"]{max-width:none!important;padding-left:1.5rem!important;padding-right:1.5rem!important}\n[data-testid="stSidebar"] [data-testid="stSidebarContent"]{padding-top:0!important}\n[data-testid="stSidebar"] [data-testid="stSidebarUserContent"]{padding: .5rem .65rem!important}\n[data-testid="stSidebar"] [data-testid="stVerticalBlock"]{gap:.2rem!important}\n[data-testid="stSidebar"] [data-testid="stButton"] button{min-height:34px!important;padding:5px 9px!important;justify-content:flex-start!important;text-align:left!important;gap:9px!important}\n[data-testid="stSidebar"] [data-testid="stButton"] button p{text-align:left!important;font-size:13px!important;margin:0!important}\n[data-testid="stSidebar"] [data-testid="stButton"] button [data-testid="stMarkdownContainer"]{flex:1;text-align:left!important}\n[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p{font-size:11px!important;line-height:1.35!important;margin:0!important}\n[data-testid="stSidebar"] hr{margin:8px 0!important}\n.rfm-brand{font-size:20px!important;margin-bottom:4px}\n.rfm-table-wrap{max-height:none!important;overflow:visible!important;width:100%!important;box-sizing:border-box!important}\n.rfm-table{table-layout:fixed!important;width:100%!important;max-width:100%!important}\n.rfm-table th,.rfm-table td{white-space:normal!important;overflow-wrap:anywhere!important;word-break:normal!important;padding:8px 7px!important;font-size:clamp(10px,1vw,13px)!important;line-height:1.35!important;min-width:0!important;max-width:none!important}\n.rfm-table thead{position:static!important}.rfm-table td.num{white-space:normal!important}\n.rfm-table td.rfm-note span{display:block!important;white-space:normal!important;overflow:visible!important;text-overflow:clip!important;max-width:none!important}\n.rfm-table th:first-child{border-top-left-radius:11px}.rfm-table th:last-child{border-top-right-radius:11px}\n.rfm-table tbody tr:last-child td:first-child{border-bottom-left-radius:11px}.rfm-table tbody tr:last-child td:last-child{border-bottom-right-radius:11px}\n@media(max-height:680px){[data-testid="stSidebar"] [data-testid="stButton"] button{min-height:29px!important;padding:3px 8px!important}[data-testid="stSidebar"] [data-testid="stVerticalBlock"]{gap:0!important}}\n</style><span class="rfm-style-anchor"></span>', unsafe_allow_html=True)

st.markdown('<style>\n[data-testid="stMainBlockContainer"], .main .block-container{padding-top:3.6rem!important;padding-bottom:2rem!important;padding-left:1.5rem!important;padding-right:1.5rem!important;max-width:none!important}\n[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"]{gap:0!important}\n[data-testid="stElementContainer"]:has(.rfm-style-anchor),[data-testid="stElementContainer"]:has(iframe[height="0"]){display:none!important}\n.rfm-hero{padding:0 0 12px!important}.rfm-hero h1{padding:0!important;margin:8px 0 10px!important}.rfm-hero p{margin:0!important}\n[data-testid="stSidebar"] [data-testid="stSidebarUserContent"]{padding:1rem .85rem!important}\n[data-testid="stSidebar"] [data-testid="stVerticalBlock"]{gap:6px!important}\n[data-testid="stSidebar"] [data-testid="stButton"] button{display:flex!important;justify-content:flex-start!important;align-items:center!important;text-align:left!important;min-height:38px!important;height:auto!important;padding:7px 12px!important;gap:10px!important}\n[data-testid="stSidebar"] [data-testid="stButton"] button > div{display:flex!important;justify-content:flex-start!important;align-items:center!important;gap:10px!important;width:100%!important}\n[data-testid="stSidebar"] [data-testid="stButton"] button p{margin:0!important;text-align:left!important;line-height:1.3!important;font-size:14px!important}\n[data-testid="stSidebar"] [data-testid="stButton"] button [data-testid="stMarkdownContainer"]{flex:1!important;text-align:left!important}\n.rfm-brand{margin:0 0 5px!important;line-height:1.4!important}.rfm-sidebar-info{font-size:11px;color:#a5a5bd;line-height:1.6;padding:10px 4px 0;border-top:1px solid #37354d;margin-top:9px}.rfm-sidebar-info div{margin:3px 0}.rfm-sidebar-sub{font-size:11px;color:#a5a5bd;line-height:1.5;margin:0 0 9px}\n@media(max-height:750px){[data-testid="stSidebar"] [data-testid="stVerticalBlock"]{gap:3px!important}[data-testid="stSidebar"] [data-testid="stButton"] button{min-height:32px!important;padding:4px 10px!important}.rfm-sidebar-info{padding-top:5px;margin-top:4px}}\n</style><span class="rfm-style-anchor"></span>', unsafe_allow_html=True)

st.markdown('<style>[data-testid="stPlotlyChart"] [data-testid="stElementToolbar"], [data-testid="stElementContainer"]:has([data-testid="stPlotlyChart"]) [data-testid="stElementToolbar"], [data-testid="stPlotlyChart"] button[title*="fullscreen" i], [data-testid="stPlotlyChart"] button[aria-label*="fullscreen" i], [data-testid="stPlotlyChart"] button[title*="full screen" i], [data-testid="stPlotlyChart"] button[aria-label*="full screen" i], [data-testid="stPlotlyChart"] button[data-testid="stFullScreenFrameButton"], [data-testid="stElementContainer"]:has([data-testid="stPlotlyChart"]) [data-testid="stFullScreenFrameButton"]{display:none!important}\n[data-testid="stSidebar"] [data-testid="stVerticalBlock"]{gap:8px!important}\n[data-testid="stSidebar"] [data-testid="stButton"] button{min-height:40px!important;padding:7px 12px!important}\n.rfm-sidebar-sub{margin:4px 0 14px!important;line-height:1.5!important}\n.rfm-sidebar-info{margin-top:14px!important;padding-top:12px!important;line-height:1.6!important}\n.rfm-sidebar-info div{margin:6px 0!important}\n@media(max-height:700px){[data-testid="stSidebar"] [data-testid="stVerticalBlock"]{gap:5px!important}[data-testid="stSidebar"] [data-testid="stButton"] button{min-height:34px!important;padding:5px 12px!important}.rfm-sidebar-sub{margin-bottom:8px!important}.rfm-sidebar-info{margin-top:8px!important;padding-top:8px!important}.rfm-sidebar-info div{margin:4px 0!important}}\n</style><span class="rfm-style-anchor"></span>', unsafe_allow_html=True)
st.markdown('<style>\n[data-testid="stSidebar"] [data-testid="stSidebarUserContent"]{padding-top:0!important}\n[data-testid="stSidebar"] [data-testid="stSidebarHeader"]{padding-top:.35rem!important;padding-bottom:.25rem!important;min-height:2.3rem!important}\n[data-testid="stSidebar"] [data-testid="stSidebarContent"]{padding-top:0!important}\n[data-baseweb="tag"]{background:#45365f!important;color:#f0eaff!important;border:1px solid #7563a7!important}\n[data-baseweb="tag"] svg{fill:#e0d5ff!important}\n[data-baseweb="select"] > div,[data-baseweb="input"] > div{background:#191a2b!important;border-color:#51456d!important;color:#f5f4fc!important}\n[data-baseweb="select"] > div:focus-within,[data-baseweb="input"] > div:focus-within{border-color:#b49aff!important;box-shadow:0 0 0 1px #b49aff55!important}\n[data-baseweb="popover"],[data-baseweb="menu"],[role="listbox"]{background:#191a2b!important;color:#f5f4fc!important}\n[role="option"]:hover,[role="option"][aria-selected="true"]{background:#352b53!important;color:#f5f4fc!important}\n\n\n\n[data-testid="stCheckbox"] input{accent-color:#947bd1!important}\n[data-testid="stCheckbox"] label:has(input:checked) > div:first-of-type{background:#947bd1!important;border-color:#b49aff!important}\n</style><span class="rfm-style-anchor"></span>', unsafe_allow_html=True)
st.markdown('<style>\n[data-testid="stSidebarHeader"]{height:36px!important;min-height:36px!important;padding:4px 12px!important}\n[data-testid="stSidebarContent"]{padding-top:0!important}\n[data-testid="stSidebarUserContent"]{padding-top:0!important;margin-top:0!important}\n[data-testid="stSidebar"] [data-testid="stVerticalBlock"]{gap:7px!important}\n[data-testid="stSidebar"] .rfm-brand{margin-top:0!important;margin-bottom:5px!important}\n[data-testid="stSidebar"] .rfm-sidebar-sub{margin-bottom:12px!important}\n[data-testid="stSidebar"] .rfm-sidebar-info{line-height:1.8!important}\n[data-baseweb="tag"]{background-color:#45365f!important;color:#f0eaff!important}\n[data-baseweb="select"] > div{background-color:#191a2b!important;border-color:#7563a7!important}\n[data-baseweb="select"] > div:focus-within{border-color:#b49aff!important;box-shadow:0 0 0 1px #b49aff!important}\n\n\n\n</style><span class="rfm-style-anchor"></span>', unsafe_allow_html=True)
ROOT = Path(__file__).resolve().parent

def tr_sayi(sayi, basamak=0):
    return f"{sayi:,.{basamak}f}".replace(",", "X").replace(".", ",").replace("X", ".")

def para(sayi):
    return f"{tr_sayi(sayi, 2)} TL"

def norm(metin):
    metin = str(metin).strip().casefold().replace("ı", "i")
    return "".join(x for x in unicodedata.normalize("NFKD", metin) if not unicodedata.combining(x) and x.isalnum())

def temiz_ad(deger, tur):
    eslesme = {
        "kategori": {"elektronik":"Elektronik","spor":"Spor","ofis":"Ofis","kozmetik":"Kozmetik","evveyasam":"Ev ve Yaşam","kitap":"Kitap"},
        "bolge": {"marmara":"Marmara","ege":"Ege","akdeniz":"Akdeniz","icanadolu":"İç Anadolu","karadeniz":"Karadeniz","doguanadolu":"Doğu Anadolu","guneydoguanadolu":"Güneydoğu Anadolu"}
    }
    if pd.isna(deger):
        return "Bilinmiyor"
    return eslesme.get(tur, {}).get(norm(deger), str(deger).strip())

@st.cache_data
def yukle():
    rfm = pd.read_csv(ROOT / "RFM_Musteri_Analizi.csv")
    segment = pd.read_csv(ROOT / "Musteri_Segment_Raporu.csv")
    ozet = pd.read_csv(ROOT / "Proje_Genel_Ozet.csv")
    ham = pd.read_csv(ROOT / "e_ticaret_veri_seti.csv")
    ham = ham.drop_duplicates().copy()
    ham["siparis_tarihi"] = pd.to_datetime(ham["siparis_tarihi"], errors="coerce")
    ham = ham.dropna(subset=["musteri_id", "siparis_id", "siparis_tarihi"])
    ham["toplam_tutar"] = pd.to_numeric(ham["toplam_tutar"], errors="coerce")
    ham["adet"] = pd.to_numeric(ham["adet"], errors="coerce")
    satis = ham[(ham["iade_durumu"].astype(str).str.strip().str.casefold() == "hayır") & (ham["toplam_tutar"] > 0)].copy()
    satis["kategori_analiz"] = satis["kategori"].map(lambda x: temiz_ad(x, "kategori"))
    satis["bolge_analiz"] = satis["bolge"].map(lambda x: temiz_ad(x, "bolge"))
    satis["sehir_analiz"] = satis["sehir"].astype(str).str.strip()
    satis["urun_analiz"] = satis["urun_adi"].astype(str).str.strip()
    satis["odeme_analiz"] = satis["odeme_turu"].map(lambda x: {"kredikarti":"Kredi Kartı","dijitalcuzdan":"Dijital Cüzdan","bankakarti":"Banka Kartı","havaleeft":"Havale/EFT","havale":"Havale/EFT","eft":"Havale/EFT","kapidaodeme":"Kapıda Ödeme","kart":"Kart (Belirtilmemiş)"}.get(norm(x), str(x).strip()) if pd.notna(x) else "Bilinmiyor")
    satis["ay"] = satis["siparis_tarihi"].dt.to_period("M").astype(str)
    satis["yil"] = satis["siparis_tarihi"].dt.year.astype(str)
    return rfm, segment, ozet, satis, ham

def grafik(fig, anahtar):
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#d8d5e8", size=12), title_font=dict(size=17,color="#f5f4fc"), margin=dict(l=20,r=20,t=60,b=35), legend_title_text="", separators=",.", hoverlabel=dict(bgcolor="#242039",font_color="#ffffff"))
    fig.update_xaxes(showgrid=True, gridcolor="#29283d", automargin=True, showticklabels=True)
    fig.update_yaxes(showgrid=True, gridcolor="#29283d", automargin=True, showticklabels=True)
    for trace in fig.data:
        if trace.type == "scatter" and "lines" in (trace.mode or ""):
            trace.update(line=dict(width=2.5,color="#ad95ff"),fill="tozeroy",fillcolor="rgba(167,139,250,0.12)")
        if trace.type == "pie":
            trace.update(textinfo="percent", textposition="inside", insidetextorientation="auto", hovertemplate="%{label}<br>%{value:,.0f}<br>%{percent}<extra></extra>")
    if anahtar in ("ana_aylik", "satis_ay", "ana_yil", "satis_yil"):
        fig.update_yaxes(title="Ciro (TL)",tickformat=",.0f",ticksuffix=" TL")
        fig.update_traces(hovertemplate="%{x}<br>Ciro: %{y:,.2f} TL<extra></extra>")
        fig.update_xaxes(title="Dönem",tickangle=-45 if anahtar.endswith("aylik") or anahtar == "satis_ay" else 0)
    fig.update_layout(title=dict(y=0.89, x=0.04), height=460, margin=dict(l=30,r=30,t=95,b=75), colorway=px.defaults.color_discrete_sequence)
    if any(t.type == "pie" for t in fig.data):
        fig.update_layout(height=510, legend=dict(orientation="h", x=0, y=-0.12, font=dict(size=11)), margin=dict(l=25,r=25,t=95,b=120), uniformtext=dict(minsize=11,mode="hide"))
        fig.update_traces(marker=dict(colors=px.defaults.color_discrete_sequence), selector=dict(type="pie"))
    config = {"displaylogo":False,"responsive":True,"scrollZoom":False,"displayModeBar":True,"doubleClick":"reset+autosize","modeBarButtonsToRemove":["lasso2d","select2d"]}
    if any(t.type == "pie" for t in fig.data):
        fig.update_traces(domain=dict(x=[0.12,0.88],y=[0.08,1]), selector=dict(type="pie"))
        fig.update_layout(legend=dict(orientation="h",x=.5,xanchor="center",y=-.12), margin=dict(l=20,r=20,t=80,b=120))
    with st.container(key=f"chart_group_{anahtar}"):
        if st.button("Grafiği büyüt", icon=":material/open_in_full:", key=f"expand_{anahtar}"):
            grafik_pencere(fig, anahtar, config)
        st.plotly_chart(fig, use_container_width=True, theme=None, key=anahtar, config=config)

@st.dialog("Grafik inceleme", width="large")
def grafik_pencere(fig, anahtar, config):
    import plotly.graph_objects as go
    buyuk = go.Figure(fig)
    buyuk.update_layout(height=480, autosize=True, width=None)
    st.plotly_chart(buyuk, use_container_width=True, theme=None, key=f"modal_{anahtar}", config=config)

def kpi(alan, baslik, deger, ikon, detay=""):
    yollar = ['M3 10l9-7 9 7v11h-7v-7h-4v7H3z', 'M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8M2 21v-3a7 7 0 0 1 14 0v3M17 4a4 4 0 0 1 0 8m2 3a5 5 0 0 1 3 5', 'M11 3a9 9 0 1 0 10 10H11zM14 2v8h8a9 9 0 0 0-8-8z', 'M3 3v18h18M6 15l5-6 4 3 6-8', 'M3 7l9-5 9 5v10l-9 5-9-5zM3 7l9 5 9-5M12 12v10', 'M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20M2 12h20M12 2a16 16 0 0 1 0 20M12 2a16 16 0 0 0 0 20', 'M2 12h5l3-8 4 16 3-8h5', 'M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20M12 7a5 5 0 1 0 0 10 5 5 0 0 0 0-10', 'M5 2h9l5 5v15H5zM14 2v6h5M8 18v-4m4 4v-7m4 7v-5']
    svg = f'<svg viewBox="0 0 24 24" fill="none" stroke="#b49aff" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="{yollar[ikon]}"/></svg>'
    alan.markdown(f'<div class="rfm-kpi"><div class="rfm-kpi-top">{escape(baslik)}{svg}</div><div class="rfm-kpi-value">{escape(str(deger))}</div><small>{escape(detay)}</small></div>', unsafe_allow_html=True)

def tablo(df, anahtar):
    basliklar = {"musteri_id":"Müşteri ID", "Recency":"Son alışveriş (gün)", "Frequency":"Sipariş sayısı", "Monetary":"Harcama (TL)", "R_Score":"R Puanı", "F_Score":"F Puanı", "M_Score":"M Puanı", "RFM_Score":"RFM Puanı", "Pazarlama_Onerisi":"Pazarlama önerisi", "urun_analiz":"Ürün", "bolge_analiz":"Bölge", "Musteri":"Müşteri", "Satis_Kaydi":"Satış kaydı", "Musteri_Basina_Ciro":"Müşteri başına ciro (TL)"}
    toplam = len(df)
    boyut = 12
    if toplam > boyut:
        sayfa_sayisi = (toplam + boyut - 1) // boyut
        sayfa_no = st.selectbox("Tablo sayfası", range(1, sayfa_sayisi + 1), format_func=lambda n: f"{n} / {sayfa_sayisi}", key=f"table_page_{anahtar}")
        baslangic = (sayfa_no - 1) * boyut
        df = df.iloc[baslangic:baslangic + boyut]
        st.caption(f"{baslangic + 1}–{baslangic + len(df)} / {toplam} kayıt")
    agirliklar = {"musteri_id":1.05,"Recency":1.05,"Frequency":.85,"Monetary":1.25,"R_Score":.55,"F_Score":.55,"M_Score":.55,"RFM_Score":.8,"Segment":1.65,"Pazarlama_Onerisi":3.1}
    agirlik = [agirliklar.get(str(c), 1.3) for c in df.columns]
    kolonlar = "<colgroup>" + "".join(f'<col style="width:{100*a/sum(agirlik):.3f}%">' for a in agirlik) + "</colgroup>"
    baslik = "".join(f"<th>{escape(basliklar.get(str(c), str(c).replace('_',' ')))}</th>" for c in df.columns)
    satirlar = []
    for row in df.itertuples(index=False, name=None):
        hucreler = []
        for i, v in enumerate(row):
            sayisal = pd.api.types.is_numeric_dtype(df.dtypes.iloc[i])
            metin = "—" if pd.isna(v) else tr_sayi(v, 2 if pd.api.types.is_float_dtype(df.dtypes.iloc[i]) else 0) if sayisal else str(v)
            if str(df.columns[i]) == "Pazarlama_Onerisi":
                hucreler.append(f'<td class="rfm-note"><span title="{escape(metin, quote=True)}">{escape(metin)}</span></td>')
            else:
                hucreler.append(f'<td class="{"num" if sayisal else ""}">{escape(metin)}</td>')
        satirlar.append("<tr>" + "".join(hucreler) + "</tr>")
    st.markdown(f'<div class="rfm-table-wrap" tabindex="0"><table class="rfm-table">{kolonlar}<thead><tr>{baslik}</tr></thead><tbody>{"".join(satirlar)}</tbody></table></div>', unsafe_allow_html=True)

def csv_indir(df, ad, etiket, anahtar):
    st.download_button(etiket, data=df.to_csv(index=False).encode("utf-8-sig"), file_name=ad, mime="text/csv", key=anahtar, use_container_width=True)

try:
    rfm, segment, ozet, satis, ham = yukle()
except Exception as hata:
    st.error(f"Dosyalar yüklenemedi: {hata}")
    st.info("app.py ve dört CSV dosyasının aynı klasörde olduğundan emin ol.")
    st.stop()

menu = ["Ana Panel", "Müşteri Yönetimi", "RFM Segmentasyonu", "Satış Analizi", "Ürün Analizi", "Bölgesel Analiz", "Müşteri Davranışları", "Pazarlama Stratejileri", "Rapor Merkezi"]
with st.sidebar:
    st.markdown('<div class="rfm-brand">◈ RFM Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="rfm-sidebar-sub">E-Ticaret Analiz ve Yönetim Sistemi</div>', unsafe_allow_html=True)
    ikonlar = ["home", "group", "pie_chart", "monitoring", "inventory_2", "public", "show_chart", "target", "description"]
    if "rfm_page" not in st.session_state:
        st.session_state.rfm_page = menu[0]
        st.session_state.rfm_transition = 0
    def sayfa_degistir(ad):
        if st.session_state.rfm_page != ad:
            st.session_state.rfm_page = ad
            st.session_state.rfm_transition += 1
    for i, ad in enumerate(menu):
        st.button(ad, icon=f":material/{ikonlar[i]}:", key=f"nav_{i}", type="primary" if st.session_state.rfm_page == ad else "secondary", use_container_width=True, on_click=sayfa_degistir, args=(ad,))
    sayfa = st.session_state.rfm_page
    st.markdown(f'<div class="rfm-sidebar-info"><div>Veri dönemi: {satis["siparis_tarihi"].min().date()} — {satis["siparis_tarihi"].max().date()}</div><div>Kaynak: proje CSV dosyaları</div></div>', unsafe_allow_html=True)

animasyon = st.session_state.rfm_transition
if st.session_state.get("rfm_scroll_done") != animasyon:
    st.session_state.rfm_scroll_done = animasyon
    components.html(f"""<script>
    (() => {{
        const doc = window.parent.document;
        const reset = () => {{
            const main = doc.querySelector('[data-testid="stMain"]');
            const view = doc.querySelector('[data-testid="stAppViewContainer"]');
            const block = doc.querySelector('.st-key-rfm_page_{animasyon}');
            if (block) {{
                let node = block.parentElement;
                while (node) {{ node.scrollTop = 0; node = node.parentElement; }}
            }}
            if (main) main.scrollTop = 0;
            if (view) view.scrollTop = 0;
            window.parent.scrollTo(0, 0);
        }};
        reset();
        [80, 220, 450].forEach(ms => setTimeout(reset, ms));
    }})();
    </script>""", height=0, scrolling=False)

st.markdown(f'<style>.st-key-rfm_page_{animasyon}{{animation:rfm-in .4s ease}} @media(prefers-reduced-motion:reduce){{.st-key-rfm_page_{animasyon}{{animation:none!important}}}}</style><span class="rfm-style-anchor"></span>', unsafe_allow_html=True)
with st.container(key=f"rfm_page_{animasyon}"):
    if sayfa == menu[0]:
        st.markdown('<div class="rfm-hero"><div class="rfm-eyebrow">RFM — VERİDEN STRATEJİYE</div><h1>Müşteri <span>Analitiği</span></h1><p>Satış performansını, müşteri segmentlerini ve iş fırsatlarını tek platform üzerinden keşfedin.</p></div>', unsafe_allow_html=True)
    else:
        st.title(sayfa)
        st.caption("Müşteri segmentasyonu, satış performansı ve iş kararları için etkileşimli analiz")

    if sayfa == menu[0]:
        a,b,c,d = st.columns(4)
        kpi(a,"Toplam Müşteri",tr_sayi(rfm["musteri_id"].nunique()),1,"Benzersiz müşteri")
        kpi(b,"Toplam Ciro",f"₺{tr_sayi(rfm['Monetary'].sum()/1e6,2)} Mn",3,para(rfm["Monetary"].sum()))
        kpi(c,"Satış Kaydı",tr_sayi(len(satis)),4,"Geçerli satış kayıtları")
        kpi(d,"Aktif Segment",tr_sayi(rfm["Segment"].nunique()),2,"RFM müşteri grupları")
        st.divider()
        donem = st.radio("Satış performansı dönemi", ["Aylık", "Yıllık"], horizontal=True, key="ana_donem")
        eksen = "ay" if donem == "Aylık" else "yil"
        aylik = satis.groupby(eksen, as_index=False)["toplam_tutar"].sum()
        col1,col2 = st.columns([1.6,1])
        with col1:
            grafik(px.line(aylik,x=eksen,y="toplam_tutar",markers=True,title=f"{donem} Satış Performansı",labels={eksen:"Dönem","toplam_tutar":"Ciro (TL)"}),"ana_aylik")
        with col2:
            adetler = rfm["Segment"].value_counts().reset_index()
            adetler.columns = ["Segment","Müşteri"]
            grafik(px.pie(adetler,names="Segment",values="Müşteri",hole=.55,title="Müşteri Segmentleri"),"ana_pie")
        c1,c2 = st.columns(2)
        with c1:
            ciro = rfm.groupby("Segment",as_index=False)["Monetary"].sum().sort_values("Monetary",ascending=False)
            grafik(px.bar(ciro,x="Segment",y="Monetary",color="Segment",title="Segment Bazında Ciro"),"ana_ciro")
        with c2:
            yillik = satis.groupby("yil",as_index=False)["toplam_tutar"].sum()
            grafik(px.bar(yillik,x="yil",y="toplam_tutar",text_auto=".2s",title="Yıllık Satış Karşılaştırması"),"ana_yil")
        st.subheader("Öne Çıkan Bulgular")
        st.write(f"En fazla müşteri içeren segment: **{rfm['Segment'].value_counts().idxmax()}**")
        st.write(f"En fazla ciro sağlayan segment: **{ciro.iloc[0]['Segment']}** ({para(ciro.iloc[0]['Monetary'])})")
        st.write(f"En yüksek ciro sağlayan ürün: **{satis.groupby('urun_analiz')['toplam_tutar'].sum().idxmax()}**")

    elif sayfa == menu[1]:
        a,b,c = st.columns(3)
        with a:
            arama = st.text_input("Müşteri ID",placeholder="MUS1001")
        with b:
            secim = st.multiselect("Segment",sorted(rfm["Segment"].dropna().unique()))
        with c:
            siralama = st.selectbox("Sıralama",["En yüksek harcama","En sık alışveriş","En son alışveriş","Müşteri ID"])
        filtre = rfm.copy()
        if arama:
            filtre = filtre[filtre["musteri_id"].astype(str).str.contains(arama,case=False,regex=False,na=False)]
        if secim:
            filtre = filtre[filtre["Segment"].isin(secim)]
        kolon,artan = {"En yüksek harcama":("Monetary",False),"En sık alışveriş":("Frequency",False),"En son alışveriş":("Recency",True),"Müşteri ID":("musteri_id",True)}[siralama]
        filtre = filtre.sort_values(kolon,ascending=artan)
        a,b,c = st.columns(3)
        a.metric("Filtrelenen Müşteri",len(filtre))
        b.metric("Toplam Harcama",para(filtre["Monetary"].sum()))
        c.metric("Ortalama Harcama",para(filtre["Monetary"].mean() if len(filtre) else 0))
        tablo(filtre,"musteri_tablosu")
        csv_indir(filtre,"Filtreli_Musteriler.csv","Filtreli Müşterileri İndir","musteri_indir")
        if len(filtre):
            musteri = st.selectbox("Detayını görüntüle",filtre["musteri_id"].astype(str).tolist())
            kayit = filtre.loc[filtre["musteri_id"].astype(str)==musteri].iloc[0]
            st.info(f"**{musteri}** | Segment: {kayit['Segment']} | Son alışverişten beri: {kayit['Recency']} gün | Sipariş: {kayit['Frequency']} | Harcama: {para(kayit['Monetary'])}")
            st.write("**Pazarlama önerisi:**",kayit["Pazarlama_Onerisi"])

    elif sayfa == menu[2]:
        adetler = rfm["Segment"].value_counts().reset_index()
        adetler.columns=["Segment","Müşteri"]
        gelir = rfm.groupby("Segment",as_index=False).agg(Musteri=("musteri_id","nunique"),Ciro=("Monetary","sum"),Ortalama_Harcama=("Monetary","mean"))
        gelir["Ciro_Payi_Yuzde"] = (gelir["Ciro"]/gelir["Ciro"].sum()*100).round(2)
        c1,c2=st.columns(2)
        with c1:
            grafik(px.bar(adetler,x="Segment",y="Müşteri",color="Segment",title="Segmentlerdeki Müşteri Sayısı"),"seg_adet")
        with c2:
            grafik(px.pie(adetler,names="Segment",values="Müşteri",hole=.45,title="Segment Dağılımı"),"seg_pie")
        grafik(px.bar(gelir.sort_values("Ciro",ascending=False),x="Segment",y="Ciro",color="Segment",title="Segmentlerin Toplam Cirosu"),"seg_ciro")
        grafik(px.bar(gelir.sort_values("Ortalama_Harcama",ascending=False),x="Segment",y="Ortalama_Harcama",title="Segment Başına Ortalama Müşteri Harcaması"),"seg_ort")
        tablo(gelir.sort_values("Ciro",ascending=False).round(2),"seg_tablo")
        st.subheader("RFM Puan Dağılımı")
        grafik(px.histogram(rfm,x="RFM_Score",color="Segment",title="RFM Puanları"),"seg_skor")

    elif sayfa == menu[3]:
        c1,c2,c3=st.columns(3)
        c1.metric("Toplam Ciro",para(satis["toplam_tutar"].sum()))
        c2.metric("Satış Kaydı",len(satis))
        c3.metric("Ortalama Kayıt Tutarı",para(satis["toplam_tutar"].mean()))
        yillar=sorted(satis["yil"].unique())
        secilen=st.multiselect("Yıl Filtresi",yillar,default=yillar)
        veri=satis[satis["yil"].isin(secilen)]
        aylik=veri.groupby("ay",as_index=False)["toplam_tutar"].sum()
        grafik(px.line(aylik,x="ay",y="toplam_tutar",markers=True,title="Aylık Ciro",labels={"ay":"Ay","toplam_tutar":"Ciro (TL)"}),"satis_ay")
        c1,c2=st.columns(2)
        with c1:
            yillik=veri.groupby("yil",as_index=False)["toplam_tutar"].sum()
            grafik(px.bar(yillik,x="yil",y="toplam_tutar",text_auto=".2s",title="Yıllık Ciro"),"satis_yil")
        with c2:
            odeme=veri.groupby("odeme_analiz",as_index=False)["toplam_tutar"].sum()
            grafik(px.pie(odeme,names="odeme_analiz",values="toplam_tutar",title="Ödeme Türlerine Göre Ciro"),"satis_odeme")
        st.subheader("Aylık Satış Tablosu")
        tablo(veri.groupby("ay",as_index=False).agg(Satis_Kaydi=("siparis_id","count"),Ciro=("toplam_tutar","sum")).round(2),"satis_tablo")

    elif sayfa == menu[4]:
        kategori=satis.groupby("kategori_analiz",as_index=False).agg(Ciro=("toplam_tutar","sum"),Adet=("adet","sum")).sort_values("Ciro",ascending=False)
        urun=satis.groupby("urun_analiz",as_index=False).agg(Ciro=("toplam_tutar","sum"),Adet=("adet","sum"))
        c1,c2,c3=st.columns(3)
        c1.metric("Ürün Çeşidi",satis["urun_analiz"].nunique())
        c2.metric("Kategori",satis["kategori_analiz"].nunique())
        c3.metric("Satılan Ürün Adedi",tr_sayi(satis["adet"].sum()))
        grafik(px.bar(kategori,x="kategori_analiz",y="Ciro",color="kategori_analiz",title="Kategori Bazında Ciro"),"urun_kat")
        c1,c2=st.columns(2)
        with c1:
            grafik(px.bar(urun.nlargest(10,"Adet").sort_values("Adet"),x="Adet",y="urun_analiz",orientation="h",title="En Çok Satılan 10 Ürün"),"urun_adet")
        with c2:
            grafik(px.bar(urun.nlargest(10,"Ciro").sort_values("Ciro"),x="Ciro",y="urun_analiz",orientation="h",title="En Fazla Ciro Sağlayan 10 Ürün"),"urun_ciro")
        st.subheader("Ürün Performans Tablosu")
        tablo(urun.sort_values("Ciro",ascending=False).round(2),"urun_tablo")

    elif sayfa == menu[5]:
        bolge=satis.groupby("bolge_analiz",as_index=False).agg(Ciro=("toplam_tutar","sum"),Musteri=("musteri_id","nunique"),Satis_Kaydi=("siparis_id","count"))
        bolge["Musteri_Basina_Ciro"]=(bolge["Ciro"]/bolge["Musteri"]).round(2)
        sehir=satis.groupby("sehir_analiz",as_index=False).agg(Ciro=("toplam_tutar","sum"),Musteri=("musteri_id","nunique"))
        st.info("Bir müşteri birden fazla bölgede alışveriş yapmış olabilir. Bölgesel benzersiz müşteri sayıları toplanarak genel müşteri sayısı hesaplanmamalıdır.")
        grafik(px.bar(bolge.sort_values("Ciro",ascending=False),x="bolge_analiz",y="Ciro",color="bolge_analiz",title="Bölgelere Göre Ciro"),"bolge_ciro")
        c1,c2=st.columns(2)
        with c1:
            grafik(px.bar(sehir.nlargest(10,"Ciro").sort_values("Ciro"),x="Ciro",y="sehir_analiz",orientation="h",title="En Yüksek Ciroya Sahip 10 Şehir"),"sehir_ciro")
        with c2:
            grafik(px.bar(bolge.sort_values("Musteri_Basina_Ciro",ascending=False),x="bolge_analiz",y="Musteri_Basina_Ciro",title="Bölgelere Göre Müşteri Başına Ciro"),"bolge_ort")
        tablo(bolge.sort_values("Ciro",ascending=False).round(2),"bolge_tablo")

    elif sayfa == menu[6]:
        c1,c2=st.columns(2)
        with c1:
            grafik(px.scatter(rfm,x="Frequency",y="Monetary",color="Segment",hover_data=["musteri_id","Recency"],title="Alışveriş Sıklığı ve Harcama"),"dav_scatter")
        with c2:
            grafik(px.histogram(rfm,x="Recency",nbins=25,title="Son Alışverişten Beri Geçen Günler"),"dav_recency")
        c1,c2=st.columns(2)
        with c1:
            grafik(px.histogram(rfm,x="Frequency",title="Sipariş Sıklığı Dağılımı"),"dav_freq")
        with c2:
            grafik(px.box(rfm,x="Segment",y="Monetary",color="Segment",title="Segmentlere Göre Harcama Dağılımı"),"dav_box")
        st.metric("Sıklık-Harcama Korelasyonu",f"{rfm['Frequency'].corr(rfm['Monetary']):.3f}")
        st.subheader("En Çok Harcama Yapan 15 Müşteri")
        tablo(rfm.nlargest(15,"Monetary")[["musteri_id","Segment","Frequency","Recency","Monetary"]],"dav_top")

    elif sayfa == menu[7]:
        sec=st.selectbox("Segment seç",sorted(rfm["Segment"].dropna().unique()))
        grup=rfm[rfm["Segment"]==sec]
        c1,c2,c3=st.columns(3)
        c1.metric("Müşteri Sayısı",len(grup))
        c2.metric("Segment Cirosu",para(grup["Monetary"].sum()))
        c3.metric("Ortalama Harcama",para(grup["Monetary"].mean()))
        st.subheader("Önerilen Pazarlama Yaklaşımı")
        for oner in grup["Pazarlama_Onerisi"].dropna().unique():
            st.success(oner)
        st.subheader("Bu Segmentteki Müşteriler")
        tablo(grup[["musteri_id","Recency","Frequency","Monetary","RFM_Score","Pazarlama_Onerisi"]].sort_values("Monetary",ascending=False),"paz_tablo")
        csv_indir(grup,f"{norm(sec)}_musteriler.csv","Segment Listesini İndir","paz_indir")

    elif sayfa == menu[8]:
        st.subheader("Analiz Dosyaları")
        c1,c2, bosluk=st.columns([1,1,1.5], gap="small")
        with c1:
            csv_indir(rfm,"RFM_Musteri_Analizi.csv","RFM Müşteri Analizi","rap_rfm")
            csv_indir(segment,"Musteri_Segment_Raporu.csv","Segment Raporu","rap_seg")
        with c2:
            csv_indir(ozet,"Proje_Genel_Ozet.csv","Proje Genel Özeti","rap_ozet")
            csv_indir(satis,"Temizlenmis_Satis_Verileri.csv","Temizlenmiş Satış Verileri","rap_satis")
        st.subheader("Proje Genel Özeti")
        tablo(ozet,"rap_ozet_tablo")
        st.subheader("Veri Kalitesi Kontrolü")
        kontroller = pd.DataFrame([
            {"Kontrol":"RFM müşteri ID benzersiz", "Durum":"BAŞARILI" if rfm["musteri_id"].is_unique else "KONTROL GEREKİYOR"},
            {"Kontrol":"RFM toplamı ile satış toplamı uyumlu", "Durum":"BAŞARILI" if abs(rfm["Monetary"].sum()-satis["toplam_tutar"].sum()) < .01 else "KONTROL GEREKİYOR"},
            {"Kontrol":"Segment müşteri sayıları uyumlu", "Durum":"BAŞARILI" if segment["Musteri_Sayisi"].sum()==len(rfm) else "KONTROL GEREKİYOR"},
            {"Kontrol":"RFM skorları 1-5 arasında", "Durum":"BAŞARILI" if rfm[["R_Score","F_Score","M_Score"]].apply(pd.to_numeric,errors="coerce").ge(1).all().all() and rfm[["R_Score","F_Score","M_Score"]].apply(pd.to_numeric,errors="coerce").le(5).all().all() else "KONTROL GEREKİYOR"}
        ])
        tablo(kontroller,"rap_kontrol")
        st.caption("Veri setinin gerçek ticari işlem kaynağı bağımsız olarak doğrulanmamıştır; örnek proje verisi olarak değerlendirilmelidir.")
