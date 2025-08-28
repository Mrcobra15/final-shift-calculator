import streamlit as st
import pandas as pd
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from calendar import monthrange
import calendar
from streamlit.components.v1 import html as st_html

# =========================================
# Basis & Config
# =========================================
st.set_page_config(page_title="SKC • Minimal V2.1", page_icon="🗓️", layout="wide")

# =========================================
# Thema / Styling (modern, licht & zwevend)
# =========================================
st.markdown("""
<style>
:root{
  /* iets donkerder grijs voor rustiger look */
  --bg:#e9edf3;
  --panel:#ffffff;
  --ink:#0f172a;          /* slate-900 */
  --muted:#64748b;        /* slate-500 */
  --border:#e5e7eb;       /* gray-200 */
  --head:#f1f5f9;         /* slate-100 */
  --accent:#ffd84d;       /* zacht geel */

  --red:#fee2e2;          /* zacht rood */
  --green:#dcfce7;        /* zacht groen */
  --blue:#dbeafe;         /* zacht blauw */
  --purple:#f3e8ff;       /* zacht paars */

  --shadow:0 8px 24px rgba(15,23,42,0.08);
  --shadow-lg:0 14px 40px rgba(15,23,42,0.12);
  --radius:16px;
}

html, body, .stApp, .block-container { background: var(--bg) !important; color: var(--ink) !important; }

/* Header + logo */
.header-wrap { display:flex; align-items:flex-end; justify-content:space-between; gap:16px; }
.brand { display:flex; align-items:flex-end; gap:12px; }
.brand-block { display:flex; flex-direction:column; align-items:center; width:max-content; }
.logo  { font: 900 58px/0.9 ui-sans-serif, system-ui; color:#e11d48; -webkit-text-stroke: 2.2px #ffffff; text-shadow: 0 1px 0 rgba(255,255,255,0.6); letter-spacing:2px; }
.sub   { font: 11px/1 ui-sans-serif; color:var(--muted); margin-top:2px; white-space:nowrap; }
.band  { height:4px; background:var(--accent); border-radius:3px; margin:12px 0 20px; box-shadow: var(--shadow); }

/* Panels & Cards (zwevend) */
.panel { background:var(--panel); border:1px solid var(--border); border-radius:var(--radius); padding:16px; box-shadow: var(--shadow-lg); }
.section-title { margin:0 0 12px 0; font: 800 18px/1.1 ui-sans-serif; letter-spacing:.2px; }

.cards { display:flex; gap:12px; flex-wrap:wrap; }
.card  { background:#fff; border:1px solid var(--border); border-radius:14px; padding:12px 14px; box-shadow: var(--shadow); min-width:160px; }
.card .t { font:12px/1.2 ui-sans-serif; color:var(--muted); }
.card .v { font:800 22px/1.2 ui-sans-serif; color:var(--ink); }

/* Dataframes (zwevend) */
[data-testid="stDataFrame"] { background:#fff; border:1px solid var(--border); border-radius:14px; box-shadow: var(--shadow); padding:6px; }
thead tr th { background: var(--head) !important; border-bottom:1px solid var(--border) !important; }

/* Inputs: ALTIJD licht, ongeacht systeem dark mode */
:root, html, body { color-scheme: light !important; }
input, textarea, select, .stTextInput input, .stNumberInput input,
div[data-baseweb="select"]>div, [role="combobox"] {
  background:#fff !important; color:#111 !important; -webkit-text-fill-color:#111 !important;
  border:1px solid var(--border) !important; border-radius:12px !important; box-shadow: var(--shadow);
}
[role="listbox"], [data-baseweb="popover"] {
  background:#fff !important; color:#111 !important; border:1px solid var(--border) !important; border-radius:12px !important; box-shadow: var(--shadow);
}
input[type=number]::-webkit-outer-spin-button,
input[type=number]::-webkit-inner-spin-button { -webkit-appearance: inner-spin-button; margin: 0; }
input:-webkit-autofill { -webkit-box-shadow: 0 0 0 1000px #fff inset !important; -webkit-text-fill-color:#111 !important; }
@media (prefers-color-scheme: dark) {
  .stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"]>div, input, select, textarea {
    background:#fff !important; color:#111 !important; -webkit-text-fill-color:#111 !important;
  }
}

/* Kalender */
.cal { width:100%; border-collapse:separate; border-spacing:10px; }
.cal th { text-align:center; font:700 13px/1.2 ui-sans-serif; color:var(--muted); }
.cell { background:#fff; border:1px solid var(--border); border-radius:14px; padding:10px; min-height:96px; box-shadow: var(--shadow); }
.dnum { font:800 13px/1 ui-sans-serif; color:#0f172a; opacity:.9; }
.badge { display:inline-block; margin-top:6px; padding:4px 8px; border-radius:999px; font:700 12px/1 ui-sans-serif; border:1px solid rgba(0,0,0,0.05); }
.badge-red    { background:var(--red); }
.badge-blue   { background:var(--blue); }
.badge-green  { background:var(--green); }
.badge-purple { background:var(--purple); }

/* Buttons */
.stButton>button, .stDownloadButton>button {
  border-radius:12px !important; padding:10px 16px !important; border:1px solid var(--border) !important; box-shadow: var(--shadow) !important; font-weight:700;
}

/* Helpers */
.grid-2 { display:grid; grid-template-columns: 1fr 1fr; gap:16px; }
@media (max-width: 900px){ .grid-2{ grid-template-columns: 1fr; } }
.small { color:var(--muted); font-size:12px; }

/* Print minimal */
@media print {
  .no-print { display:none !important; }
  .band, .stSidebar, header, footer { display:none !important; }
  .panel { box-shadow:none; }
  body, .stApp, .block-container { background:#fff !important; }
}
</style>
""", unsafe_allow_html=True)

# =========================================
# Constantes & helpers
# =========================================
SUGGESTIES = ["vv6", "vv7.6", "ll7.6", "ll6.25", "ll3.8", "ln7.6", "ln6", "n10", "bijs", "fdrecup"]

# eenvoudige (configureerbare) uren per code voor totaaluren
SHIFT_HOURS = {
    "vv6": 6.0, "vv7.6": 7.6, "ll7.6": 7.6, "ll6.25": 6.25, "ll3.8": 3.8,
    "ln7.6": 7.6, "ln6": 6.0, "n10": 10.0, "bijs": 0.0, "fdrecup": 0.0, "": 0.0
}
MONTH_NL = ["januari","februari","maart","april","mei","juni","juli","augustus","september","oktober","november","december"]
DOW_NL = ["Ma","Di","Wo","Do","Vr","Za","Zo"]

def norm_code(s: str) -> str:
    """Normaliseer een code: lowercase, geen spaties."""
    return (s or "").strip().lower().replace(" ", "")

def ensure_state():
    if "current_date" not in st.session_state:
        st.session_state.current_date = date.today()
    if "entries" not in st.session_state:
        st.session_state.entries = []  # {"datum": date, "code": str}
    if "calc_month_key" not in st.session_state:
        st.session_state.calc_month_key = None
    if "_do_print" not in st.session_state:
        st.session_state["_do_print"] = False

def add_or_replace_entry(d: date, code: str):
    """Voeg shift toe; vervang bestaande voor dezelfde datum (stabielere UX)."""
    code = norm_code(code)
    for i, e in enumerate(st.session_state.entries):
        if e["datum"] == d:
            st.session_state.entries[i] = {"datum": d, "code": code}
            return
    st.session_state.entries.append({"datum": d, "code": code})

def month_calendar_grid(y: int, m: int):
    cal = calendar.Calendar(firstweekday=0)  # Maandag=0
    return [list(w) for w in cal.monthdatescalendar(y, m)]

def code_to_color(code: str) -> str:
    c = (code or "").lower()
    if c == "":         return "green"
    if c == "n10":      return "purple"
    if c == "bijs":     return "blue"
    if c == "fdrecup":  return "green"
    return "red"

def badge_class(color: str) -> str:
    return {"red":"badge-red","blue":"badge-blue","green":"badge-green","purple":"badge-purple"}[color]

def month_filter_df(df: pd.DataFrame, y: int, m: int) -> pd.DataFrame:
    if df.empty: 
        return df
    return df[(df["Datum"].dt.year == int(y)) & (df["Datum"].dt.month == int(m))].copy()

ensure_state()

# =========================================
# Header (logo)
# =========================================
cL, _ = st.columns([7,5])
with cL:
    st.markdown(
        "<div class='header-wrap'>"
        " <div class='brand'>"
        "  <div class='brand-block'>"
        "    <div class='logo'>SKC</div>"
        "    <div class='sub'>Shift&nbsp;Kalender&nbsp;Calculator</div>"
        "  </div>"
        " </div>"
        "</div>",
        unsafe_allow_html=True
    )
st.markdown("<div class='band'></div>", unsafe_allow_html=True)

# =========================================
# Maandnavigatie
# =========================================
nav = st.container()
with nav:
    c1,c2,c3,c4,c5 = st.columns([1,1,1,2,2])
    today = date.today()
    year  = c4.number_input("Jaar", 2000, 2100, value=st.session_state.current_date.year, step=1)
    month = c5.selectbox("Maand", list(range(1,13)), index=st.session_state.current_date.month-1, format_func=lambda m: MONTH_NL[m-1])
    if c1.button("←", help="Vorige maand"): d = date(int(year), int(month), 1) - relativedelta(months=1); year,month = d.year, d.month
    if c2.button("Vandaag"): year, month = today.year, today.month
    if c3.button("→", help="Volgende maand"): d = date(int(year), int(month), 1) + relativedelta(months=1); year,month = d.year, d.month

# Clamp huidige dag binnen maand
last_day = monthrange(int(year), int(month))[1]
st.session_state.current_date = st.session_state.current_date.replace(
    year=int(year), month=int(month), day=min(st.session_state.current_date.day, last_day)
)

# =========================================
# Invoerblok (datum + suggesties + custom)
# =========================================
st.markdown("<div class='panel'>", unsafe_allow_html=True)
st.markdown(f"<div class='section-title'>Shift toevoegen</div>", unsafe_allow_html=True)

colD, colShift, colOK = st.columns([1,2,1])

with colD:
    st.caption("Datum")
    dcol1, dcol2 = st.columns(2)
    if dcol1.button("◀︎", use_container_width=True):
        st.session_state.current_date -= timedelta(days=1)
    if dcol2.button("▶︎", use_container_width=True):
        st.session_state.current_date += timedelta(days=1)
    st.markdown(f"<div style='font:800 16px/1.2 ui-sans-serif'>{st.session_state.current_date:%d-%m-%Y}</div>", unsafe_allow_html=True)

with colShift:
    st.caption("Shift (suggesties) — of typ zelf")
    code_choice = st.selectbox(
        "Kies (of laat op vrij)",
        options=["(vrij)"] + SUGGESTIES,
        index=0,
        placeholder="bv. vv6, ll3.8, n10…",
        label_visibility="collapsed"
    )
    code_custom = st.text_input("of typ zelf", value="", placeholder="bv. ln6", label_visibility="collapsed")
    code_final = norm_code(code_custom) if code_custom.strip() else ("" if code_choice == "(vrij)" else norm_code(code_choice))

with colOK:
    st.caption("Actie")
    if st.button("✅ OK", use_container_width=True, type="primary"):
        add_or_replace_entry(st.session_state.current_date, code_final)
        st.session_state.current_date += timedelta(days=1)
        st.success("Shift opgeslagen en naar volgende datum gesprongen.")

st.markdown("</div>", unsafe_allow_html=True)

# =========================================
# Overzicht + Tellers + Download CSV
# =========================================
st.markdown("<div class='panel'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>Overzicht</div>", unsafe_allow_html=True)

if st.session_state.entries:
    df = pd.DataFrame(st.session_state.entries)
    df["Datum"] = pd.to_datetime(df["datum"])
    df["Code"] = df["code"]
    df["DatumStr"] = df["Datum"].dt.strftime("%d-%m-%Y")

    dfm = month_filter_df(df, int(year), int(month))

    total_days = len(dfm)
    total_hours = float(sum(SHIFT_HOURS.get(c, 0.0) for c in dfm["Code"])) if not dfm.empty else 0.0

    st.markdown("<div class='cards'>"
                f"<div class='card'><div class='t'>Totaal dagen (maand)</div><div class='v'>{total_days}</div></div>"
                f"<div class='card'><div class='t'>Totaal uren (maand)</div><div class='v'>{total_hours:.2f} u</div></div>"
                "</div>", unsafe_allow_html=True)

    show = dfm.sort_values(["Datum","Code"])[["DatumStr","Code"]].rename(columns={"DatumStr":"Datum"})
    st.dataframe(show, use_container_width=True, hide_index=True)

    # Acties + download CSV (huidige maand)
    left, mid, right = st.columns([1,2,7])
    with left:
        if st.button("↩︎ Laatste verwijderen"):
            if st.session_state.entries:
                st.session_state.entries.pop()
                st.experimental_rerun()
    with mid:
        if st.button("🗑️ Alles wissen"):
            st.session_state.entries = []
            st.experimental_rerun()
    with right:
        if not dfm.empty:
            out = dfm.copy()
            out["Uren"] = out["Code"].apply(lambda c: SHIFT_HOURS.get(c, 0.0))
            out = out[["DatumStr","Code","Uren"]].rename(columns={"DatumStr":"Datum"})
            st.download_button(
                "⬇️ Download CSV (deze maand)",
                data=out.to_csv(index=False).encode("utf-8"),
                file_name=f"skc_{int(year)}_{int(month):02d}.csv",
                mime="text/csv",
            )
else:
    st.info("Nog niets ingevoerd. Voeg shifts toe met de OK-knop.")

st.markdown("</div>", unsafe_allow_html=True)

# =========================================
# Maand berekenen → Kalender + Print + Legende
# =========================================
def render_calendar(y: int, m: int, entries: list[dict]):
    # per-dag lijst met codes
    by_day = {}
    for e in entries:
        d = e["datum"]
        if d.year == int(y) and d.month == int(m):
            by_day.setdefault(d, []).append(e["code"])

    weeks = month_calendar_grid(int(y), int(m))
    html = ["<table class='cal'>"]
    html.append("<thead><tr>" + "".join(f"<th>{h}</th>" for h in DOW_NL) + "</tr></thead><tbody>")
    for wk in weeks:
        html.append("<tr>")
        for d in wk:
            inside = f"<div class='dnum'>{d.day}</div>"
            # badges
            codes = by_day.get(d, [])
            if len(codes) == 0 and d.month == int(m):
                inside += f"<div class='badge badge-green'>vrij</div>"
            for c in codes:
                col = code_to_color(c)
                inside += f"<div class='badge {badge_class(col)}'>{c if c else 'vrij'}</div>"
            style = "" if d.month == int(m) else "opacity:.4;"
            html.append(f"<td style='padding:0'><div class='cell' style='{style}'>{inside}</div></td>")
        html.append("</tr>")
    html.append("</tbody></table>")
    st.markdown("".join(html), unsafe_allow_html=True)

st.markdown("<div class='panel'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>Maand berekenen</div>", unsafe_allow_html=True)

if st.button("📅 Maand berekenen", type="primary"):
    st.session_state.calc_month_key = f"{int(year)}-{int(month):02d}"

# Toon kalender + print, enkel na berekenen
if st.session_state.calc_month_key == f"{int(year)}-{int(month):02d}":
    # Titel, metrics, print
    colT, colM1, colM2, colBtn = st.columns([3,1.2,1.2,1])
    with colT:
        st.subheader(f"{MONTH_NL[int(month)-1].capitalize()} {int(year)}")

    # Metrics voor de kalender
    if "df" in locals():
        df_src = df.copy()
    else:
        df_src = pd.DataFrame(st.session_state.entries)
        if not df_src.empty:
            df_src["Datum"] = pd.to_datetime(df_src["datum"])

    if not df_src.empty:
        dfm_cal = month_filter_df(df_src.rename(columns={"datum":"Datum"}), int(year), int(month))
        total_days_cal = len(dfm_cal)
        total_hours_cal = float(sum(SHIFT_HOURS.get(c, 0.0) for c in dfm_cal["code"])) if not dfm_cal.empty else 0.0
    else:
        total_days_cal = 0; total_hours_cal = 0.0

    with colM1: st.metric("Dagen", f"{total_days_cal}")
    with colM2: st.metric("Uren", f"{total_hours_cal:.2f} u")
    with colBtn:
        if st.button("🖨️ Afdrukken", key="print_btn", help="Print of bewaar als PDF"):
            st.session_state["_do_print"] = True

    render_calendar(int(year), int(month), st.session_state.entries)

    # Legende (subtiel)
    st.markdown(
        "<div class='small' style='margin-top:8px'>"
        "<strong>Legende:</strong> "
        "<span class='badge badge-red'>shift</span> "
        "<span class='badge badge-purple'>n10</span> "
        "<span class='badge badge-blue'>bijs</span> "
        "<span class='badge badge-green'>vrij / fdrecup</span>"
        "</div>",
        unsafe_allow_html=True
    )

    # Betrouwbare print trigger
    if st.session_state.get("_do_print"):
        st_html("<script>window.print();</script>", height=0)
        st.session_state["_do_print"] = False
else:
    st.caption("Klik op **Maand berekenen** om de kalender te tonen.")

st.markdown("</div>", unsafe_allow_html=True)
