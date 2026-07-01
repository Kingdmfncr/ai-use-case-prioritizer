"""
AI Use Case Prioritizer — v2
Portfolio Gisèle Metouck — Projet 7
Option C : Auto-scoring Claude Haiku
Option B : Benchmark sectoriel (6 secteurs × 6 types)
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import os
from datetime import datetime

# ─── Config page ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Use Case Prioritizer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Design system ─────────────────────────────────────────────────────────────
COLORS = {
    "primary":    "#00ff88",
    "warning":    "#ffd700",
    "danger":     "#ff4444",
    "info":       "#4ecdc4",
    "purple":     "#a855f7",
    "bg_main":    "#0a0a0a",
    "bg_surface": "#1a1a2e",
    "bg_sidebar": "#16213e",
    "text_main":  "#ffffff",
    "text_muted": "#888888",
}

CHART_DEFAULTS = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#1a1a2e",
    font_color="#ffffff",
    font_family="sans-serif",
    title_font_color="#00ff88",
    title_font_size=16,
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="white")),
    margin=dict(l=20, r=20, t=40, b=20),
    xaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.1)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.1)"),
)

st.markdown(f"""
<style>
  html,body,.stApp {{ background-color:{COLORS['bg_main']};color:{COLORS['text_main']}; }}
  .stTabs [data-baseweb="tab-list"] {{ background-color:{COLORS['bg_sidebar']};border-radius:8px;padding:4px;gap:4px; }}
  .stTabs [data-baseweb="tab"] {{ color:{COLORS['text_muted']};border-radius:6px;padding:8px 20px;font-size:.9rem; }}
  .stTabs [aria-selected="true"] {{ background-color:{COLORS['bg_surface']};color:{COLORS['primary']};font-weight:600; }}
  .stSidebar {{ background-color:{COLORS['bg_sidebar']}; }}
  .metric-card {{
    background:{COLORS['bg_surface']};border-radius:10px;padding:16px 20px;
    border-left:3px solid {COLORS['primary']};margin-bottom:8px;
  }}
  .metric-card.warn   {{ border-left-color:{COLORS['warning']}; }}
  .metric-card.danger {{ border-left-color:{COLORS['danger']}; }}
  .metric-card.purple {{ border-left-color:{COLORS['purple']}; }}
  .metric-val         {{ font-size:2rem;font-weight:700;color:{COLORS['primary']}; }}
  .metric-val.warn    {{ color:{COLORS['warning']}; }}
  .metric-val.danger  {{ color:{COLORS['danger']}; }}
  .metric-label       {{ font-size:.8rem;color:{COLORS['text_muted']};margin-bottom:4px; }}
  .metric-delta       {{ font-size:.85rem;color:{COLORS['text_muted']};margin-top:4px; }}
  .badge {{ display:inline-block;padding:3px 10px;border-radius:20px;font-size:.75rem;font-weight:700;margin:2px; }}
  .badge-qw {{ background:#003d1a;border:1px solid {COLORS['primary']};color:{COLORS['primary']}; }}
  .badge-sb {{ background:#3d2f00;border:1px solid {COLORS['warning']};color:{COLORS['warning']}; }}
  .badge-fi {{ background:#003d3d;border:1px solid {COLORS['info']};color:{COLORS['info']}; }}
  .badge-q  {{ background:#3d0000;border:1px solid {COLORS['danger']};color:{COLORS['danger']}; }}
  .quadrant-card {{ background:{COLORS['bg_surface']};border-radius:10px;padding:20px;border:1px solid rgba(255,255,255,0.08);margin:8px 0; }}
  .uc-row {{
    background:{COLORS['bg_surface']};border-radius:8px;padding:14px 18px;margin:6px 0;
    border-left:3px solid {COLORS['primary']};display:flex;align-items:center;justify-content:space-between;
  }}
  .score-pill {{ font-size:.9rem;font-weight:700;padding:4px 14px;border-radius:20px;min-width:60px;text-align:center; }}
  .alert-box {{ border-left:4px solid;border-radius:4px;padding:10px 16px;margin:6px 0;font-size:.9rem; }}
  .alert-info   {{ border-color:{COLORS['info']};   background:rgba(78,205,196,.1); }}
  .alert-warn   {{ border-color:{COLORS['warning']};background:rgba(255,215,0,.08); }}
  .alert-danger {{ border-color:{COLORS['danger']}; background:rgba(255,68,68,.08); }}
  .alert-ok     {{ border-color:{COLORS['primary']};background:rgba(0,255,136,.08); }}
  .ai-score-box {{
    background:rgba(0,255,136,.06);border:1px solid rgba(0,255,136,.3);
    border-radius:10px;padding:16px;margin:10px 0;
  }}
  .benchmark-dot {{ display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:4px; }}
  .stButton>button {{
    background:linear-gradient(135deg,#00c66a,#00ff88);color:#000;
    border:none;border-radius:6px;padding:8px 20px;font-weight:600;
  }}
  caption {{ color:{COLORS['text_muted']};font-size:.78rem; }}
</style>
""", unsafe_allow_html=True)

# ─── Benchmark data ─────────────────────────────────────────────────────────────
@st.cache_data
def load_benchmarks() -> dict:
    bench_path = os.path.join(os.path.dirname(__file__), "data", "benchmarks_sectoriels.json")
    try:
        with open(bench_path, "r", encoding="utf-8") as f:
            return json.load(f)["secteurs"]
    except Exception:
        return {}

BENCHMARKS = load_benchmarks()
SECTEUR_OPTIONS = ["(Aucun)"] + list(BENCHMARKS.keys())

# ─── Demo data ─────────────────────────────────────────────────────────────────
DEMO_USE_CASES = [
    {"nom": "Chatbot SAV personnalisé",        "categorie": "Customer Experience",   "description": "Assistant IA pour répondre aux demandes clients en temps réel (retours, stock, recommandations produit)", "impact": 8, "faisabilite": 7, "delai_valeur": 8, "alignement": 9, "risque": 8},
    {"nom": "Prédiction tendances mode (CV)",  "categorie": "Product & Design",      "description": "Vision par ordinateur pour analyser les images social media et détecter les tendances émergentes avant le marché", "impact": 9, "faisabilite": 4, "delai_valeur": 3, "alignement": 9, "risque": 7},
    {"nom": "Moteur de recommandation produit","categorie": "E-commerce",            "description": "Personnalisation des suggestions produit sur le site selon historique d'achat et comportement de navigation", "impact": 8, "faisabilite": 8, "delai_valeur": 7, "alignement": 8, "risque": 9},
    {"nom": "Détection fraude e-commerce",    "categorie": "Sécurité & Conformité", "description": "Modèle de détection des transactions frauduleuses sur les canaux digitaux (ML temps réel)", "impact": 7, "faisabilite": 6, "delai_valeur": 6, "alignement": 6, "risque": 9},
    {"nom": "Optimisation inventaire prédictive","categorie": "Supply Chain",        "description": "Prévision de la demande par SKU et région pour réduire les ruptures et les surstock", "impact": 8, "faisabilite": 5, "delai_valeur": 4, "alignement": 7, "risque": 8},
    {"nom": "Personnalisation email marketing","categorie": "Marketing",             "description": "Génération automatique de contenu email adapté au segment client, au moment d'envoi optimal", "impact": 6, "faisabilite": 9, "delai_valeur": 9, "alignement": 7, "risque": 9},
    {"nom": "Analyse sentiment réseaux sociaux","categorie": "Brand & Insights",    "description": "NLP en temps réel sur les mentions de la marque pour détecter les crises et opportunités", "impact": 6, "faisabilite": 8, "delai_valeur": 7, "alignement": 6, "risque": 8},
    {"nom": "Virtual Try-On (AR)",             "categorie": "Customer Experience",   "description": "Essayage virtuel de produits beauté/mode via la caméra smartphone (technologie AR/ML)", "impact": 9, "faisabilite": 3, "delai_valeur": 2, "alignement": 8, "risque": 7},
]

CATEGORIES = [
    "Customer Experience","Product & Design","E-commerce","Marketing",
    "Supply Chain","Sécurité & Conformité","Brand & Insights",
    "RH & Organisation","Finance","Autre",
]

# ─── Session state ──────────────────────────────────────────────────────────────
def init_state():
    if "use_cases"       not in st.session_state: st.session_state.use_cases = [dict(uc) for uc in DEMO_USE_CASES]
    if "weights"         not in st.session_state: st.session_state.weights   = {"impact":30,"faisabilite":25,"delai_valeur":20,"alignement":15,"risque":10}
    if "narrative_cache" not in st.session_state: st.session_state.narrative_cache = ""
    if "autoscore_cache" not in st.session_state: st.session_state.autoscore_cache = {}  # {nom: {scores, rationale}}

init_state()

# ─── Scoring engine ─────────────────────────────────────────────────────────────
def compute_score(uc: dict, weights: dict) -> float:
    total_w = sum(weights.values()) or 100
    return round(
        (uc["impact"]       * weights["impact"]
       + uc["faisabilite"]  * weights["faisabilite"]
       + uc["delai_valeur"] * weights["delai_valeur"]
       + uc["alignement"]   * weights["alignement"]
       + uc["risque"]       * weights["risque"]) / total_w, 1)

def get_quadrant(impact: int, faisabilite: int) -> str:
    hi, hf = impact >= 6, faisabilite >= 6
    if hi and hf:       return "Quick Win"
    if hi and not hf:   return "Strategic Bet"
    if not hi and hf:   return "Fill-in"
    return "Questionable"

QUAD_META = {
    "Quick Win":     ("badge-qw", "🟢 Quick Win",     "Impact fort + faisabilité élevée"),
    "Strategic Bet": ("badge-sb", "🟡 Strategic Bet", "Impact fort mais complexe"),
    "Fill-in":       ("badge-fi", "🔵 Fill-in",        "Facile mais faible impact"),
    "Questionable":  ("badge-q",  "🔴 Questionable",  "Difficile ET faible impact"),
}

def score_color(s: float) -> str:
    return COLORS["primary"] if s >= 7 else COLORS["warning"] if s >= 5 else COLORS["danger"]

def score_class(s: float) -> str:
    return "" if s >= 7 else "warn" if s >= 5 else "danger"

@st.cache_data
def build_df(use_cases_json: str, weights_json: str) -> pd.DataFrame:
    ucs, weights = json.loads(use_cases_json), json.loads(weights_json)
    rows = [{**uc, "score": compute_score(uc, weights), "quadrant": get_quadrant(uc["impact"], uc["faisabilite"])} for uc in ucs]
    df = pd.DataFrame(rows).sort_values("score", ascending=False).reset_index(drop=True)
    df.index += 1
    return df

def get_df() -> pd.DataFrame:
    return build_df(json.dumps(st.session_state.use_cases), json.dumps(st.session_state.weights))

# ─── Option C : Auto-scoring Claude ────────────────────────────────────────────
def autoscore_with_claude(nom: str, description: str, categorie: str, api_key: str) -> dict | None:
    """Call Claude Haiku, return {scores: {impact,faisabilite,delai_valeur,alignement,risque}, rationale: {dim: str}}"""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        prompt = f"""Tu es un expert en stratégie IA et product management.
Analyse ce cas d'usage IA et attribue un score de 1 à 10 pour chaque dimension.

Nom : {nom}
Catégorie : {categorie}
Description : {description}

Dimensions à noter :
- impact : Potentiel de revenus, réduction de coûts ou avantage concurrentiel (10 = très fort impact business)
- faisabilite : Disponibilité des données + maturité technique nécessaire (10 = très facile à implémenter)
- delai_valeur : Rapidité d'obtention du premier résultat mesurable (10 = valeur en moins d'1 mois)
- alignement : Cohérence avec les OKRs et la stratégie digitale typique du secteur (10 = alignement parfait)
- risque : Niveau de risque RGPD, éthique IA et conformité (10 = risque très faible)

Réponds UNIQUEMENT en JSON valide, sans texte avant ou après :
{{
  "scores": {{
    "impact": <int 1-10>,
    "faisabilite": <int 1-10>,
    "delai_valeur": <int 1-10>,
    "alignement": <int 1-10>,
    "risque": <int 1-10>
  }},
  "rationale": {{
    "impact": "<1 phrase de justification>",
    "faisabilite": "<1 phrase de justification>",
    "delai_valeur": "<1 phrase de justification>",
    "alignement": "<1 phrase de justification>",
    "risque": "<1 phrase de justification>"
  }}
}}"""
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = msg.content[0].text.strip()
        # extract JSON if wrapped in code block
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"): raw = raw[4:]
        return json.loads(raw)
    except Exception as e:
        st.error(f"Erreur auto-scoring : {e}")
        return None

# ─── Option B : Benchmark lookup ───────────────────────────────────────────────
def find_best_benchmark(secteur: str, categorie: str, description: str) -> tuple[str, dict] | tuple[None, None]:
    """Return (type_name, benchmark_dict) or (None, None)"""
    if secteur not in BENCHMARKS:
        return None, None
    cas_types = BENCHMARKS[secteur]["cas_types"]
    # simple keyword match between description+categorie and cas type names
    desc_lower = (description + " " + categorie).lower()
    best_match, best_score = None, 0
    for ct_name in cas_types:
        keywords = ct_name.lower().replace("(", "").replace(")", "").split()
        matches = sum(1 for kw in keywords if kw in desc_lower)
        if matches > best_score:
            best_score, best_match = matches, ct_name
    if best_match and best_score > 0:
        return best_match, cas_types[best_match]
    # fallback: return first cas_type as generic reference
    first = list(cas_types.keys())[0]
    return first, cas_types[first]

# ─── PDF export ────────────────────────────────────────────────────────────────
def generate_pdf(df: pd.DataFrame, company: str, weights: dict, secteur: str) -> bytes:
    try:
        from fpdf import FPDF
    except ImportError:
        return b""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(0, 200, 100)
    pdf.cell(0, 12, "AI Use Case Prioritizer", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 7, f"Rapport — {company} — Secteur : {secteur} — {datetime.today().strftime('%d/%m/%Y')}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    # KPIs
    pdf.set_font("Helvetica", "B", 13); pdf.set_text_color(0,200,100)
    pdf.cell(0, 8, "Synthèse", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10); pdf.set_text_color(40,40,40)
    qw = len(df[df.quadrant=="Quick Win"]); sb = len(df[df.quadrant=="Strategic Bet"])
    for line in [f"Cas d'usage analysés : {len(df)}", f"Quick Wins : {qw}", f"Strategic Bets : {sb}",
                 f"Score moyen portefeuille : {df['score'].mean():.1f}/10"]:
        pdf.cell(0, 6, line, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    # Weights
    pdf.set_font("Helvetica", "B", 12); pdf.set_text_color(0,140,70)
    pdf.cell(0, 8, "Pondérations", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10); pdf.set_text_color(60,60,60)
    labels = {"impact":"Impact Business","faisabilite":"Faisabilité","delai_valeur":"Délai de Valeur","alignement":"Alignement","risque":"Risque"}
    for k,v in weights.items():
        pdf.cell(0, 6, f"  {labels[k]} : {v}%", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    # Table
    pdf.set_font("Helvetica", "B", 12); pdf.set_text_color(0,140,70)
    pdf.cell(0, 8, "Classement", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica","B",9); pdf.set_text_color(255,255,255); pdf.set_fill_color(20,30,60)
    for (txt, w) in [("#",8),("Cas d'usage",68),("Catégorie",40),("Score",20),("Quadrant",44)]:
        pdf.cell(w, 7, txt, border=0, fill=True)
    pdf.ln()
    pdf.set_font("Helvetica","",9)
    for i, row in df.iterrows():
        fill = i % 2 == 0
        pdf.set_fill_color(240,245,240) if fill else pdf.set_fill_color(255,255,255)
        pdf.set_text_color(30,30,30)
        for (txt, w) in [(str(i),8),(str(row["nom"])[:38],68),(str(row["categorie"])[:24],40),(f"{row['score']}/10",20),(str(row["quadrant"]),44)]:
            pdf.cell(w, 6, txt, border=0, fill=fill)
        pdf.ln()
    pdf.ln(6)

    # Top 3
    pdf.set_font("Helvetica","B",12); pdf.set_text_color(0,140,70)
    pdf.cell(0,8,"Top 3 — Détail",new_x="LMARGIN",new_y="NEXT")
    for i, row in df.head(3).iterrows():
        pdf.set_font("Helvetica","B",10); pdf.set_text_color(0,100,50)
        pdf.cell(0,7,f"#{i} {row['nom']} — Score {row['score']}/10",new_x="LMARGIN",new_y="NEXT")
        pdf.set_font("Helvetica","",9); pdf.set_text_color(60,60,60)
        pdf.multi_cell(0,5,row["description"])
        pdf.cell(0,5,f"Impact:{row['impact']}  Faisabilité:{row['faisabilite']}  Délai:{row['delai_valeur']}  Alignement:{row['alignement']}  Risque:{row['risque']}",new_x="LMARGIN",new_y="NEXT")
        pdf.ln(4)

    pdf.set_y(-20); pdf.set_font("Helvetica","I",8); pdf.set_text_color(150,150,150)
    pdf.cell(0,5,"Construit avec l'IA — Gisèle Metouck | Portfolio Data & IA",align="C")
    return bytes(pdf.output())

# ─── AI narrative ───────────────────────────────────────────────────────────────
def generate_narrative(df: pd.DataFrame, company: str, secteur: str, api_key: str) -> str:
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        top3 = df.head(3)[["nom","score","quadrant","categorie","description"]].to_dict("records")
        bench_ctx = f"Secteur de référence : {secteur}." if secteur != "(Aucun)" else ""
        prompt = f"""Tu es consultant IA senior. L'entreprise "{company}" a évalué {len(df)} cas d'usage IA. {bench_ctx}
Top 3 :
{json.dumps(top3, ensure_ascii=False, indent=2)}

Synthèse exécutive 200 mots max, 3 paragraphes :
1. Recommandation principale (quel cas lancer en premier et pourquoi)
2. Séquencement pour le portefeuille complet
3. Point de vigilance principal

Ton = professionnel, direct, orienté décision. Pas de bullets. Pas de titre."""
        msg = client.messages.create(model="claude-haiku-4-5-20251001", max_tokens=450,
                                     messages=[{"role":"user","content":prompt}])
        return msg.content[0].text
    except Exception as e:
        return f"Erreur : {e}"

# ─── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"<h2 style='color:{COLORS['primary']};margin-bottom:4px'>🧠 AI Prioritizer</h2>", unsafe_allow_html=True)
    st.caption("v2 — Auto-scoring IA + Benchmark sectoriel")
    st.divider()

    company = st.text_input("Entreprise / Équipe", value="Mon Entreprise", placeholder="ex: Dior Digital…")
    secteur = st.selectbox("Secteur de référence (benchmark)", SECTEUR_OPTIONS)

    st.divider()
    st.markdown(f"<p style='color:{COLORS['primary']};font-weight:600;font-size:.9rem'>⚖️ Pondérations (%)</p>", unsafe_allow_html=True)
    w = st.session_state.weights
    w["impact"]       = st.slider("Impact Business",        0, 100, w["impact"],       5)
    w["faisabilite"]  = st.slider("Faisabilité Technique",  0, 100, w["faisabilite"],  5)
    w["delai_valeur"] = st.slider("Délai de Valeur",        0, 100, w["delai_valeur"], 5)
    w["alignement"]   = st.slider("Alignement Stratégique", 0, 100, w["alignement"],   5)
    w["risque"]       = st.slider("Risque & Conformité",    0, 100, w["risque"],        5)
    total_w = sum(w.values())
    if total_w != 100:
        st.markdown(f"<div class='alert-box alert-warn'>⚠ Total = {total_w}% (idéal : 100%)</div>", unsafe_allow_html=True)

    st.divider()
    st.markdown(f"<p style='color:{COLORS['primary']};font-weight:600;font-size:.9rem'>🤖 Clé API Anthropic</p>", unsafe_allow_html=True)
    api_key = st.text_input("Clé API (BYOK)", type="password", placeholder="sk-ant-…")
    if api_key:
        st.markdown("<div class='alert-box alert-ok'>✅ Clé saisie — auto-scoring actif</div>", unsafe_allow_html=True)
    else:
        st.caption("Sans clé : scores manuels uniquement")

    st.divider()
    st.caption("[GitHub](https://github.com/Kingdmfncr) · Portfolio Gisèle Metouck")

# ─── Header + KPIs ──────────────────────────────────────────────────────────────
st.markdown(f"""
<h1 style='color:{COLORS['text_main']};margin-bottom:2px'>🧠 AI Use Case Prioritizer</h1>
<p style='color:{COLORS['text_muted']};font-size:.95rem;margin-bottom:16px'>
  {company} · {secteur if secteur != "(Aucun)" else "Secteur non sélectionné"} · Scoring composite 5 dimensions
</p>
""", unsafe_allow_html=True)

df = get_df()
total_uc  = len(df)
avg_score = df["score"].mean()
n_qw      = (df.quadrant == "Quick Win").sum()
n_sb      = (df.quadrant == "Strategic Bet").sum()
top_uc    = df.iloc[0]["nom"] if total_uc > 0 else "—"

c1,c2,c3,c4,c5 = st.columns(5)
with c1:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>Cas analysés</div><div class='metric-val'>{total_uc}</div></div>", unsafe_allow_html=True)
with c2:
    cls = score_class(avg_score)
    st.markdown(f"<div class='metric-card {cls}'><div class='metric-label'>Score moyen</div><div class='metric-val {cls}'>{avg_score:.1f}<span style='font-size:1rem'>/10</span></div></div>", unsafe_allow_html=True)
with c3:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>Quick Wins</div><div class='metric-val'>{n_qw}</div><div class='metric-delta'>Lancer immédiatement</div></div>", unsafe_allow_html=True)
with c4:
    st.markdown(f"<div class='metric-card warn'><div class='metric-label'>Strategic Bets</div><div class='metric-val warn'>{n_sb}</div><div class='metric-delta'>Moyen terme</div></div>", unsafe_allow_html=True)
with c5:
    st.markdown(f"<div class='metric-card purple'><div class='metric-label'>Priorité #1</div><div class='metric-val' style='color:#a855f7;font-size:1rem'>{top_uc[:28]}</div></div>", unsafe_allow_html=True)

# ─── Tabs ────────────────────────────────────────────────────────────────────────
tabs = st.tabs(["📋 Cas d'Usage", "📊 Matrice + Benchmark", "🏆 Classement", "🔬 Simulation", "📄 Rapport & IA"])

# ══════════════════════════════════════════════════════════════════════════════════
# TAB 1 — Cas d'usage + AUTO-SCORING (Option C)
# ══════════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    st.markdown(f"<h2 style='color:{COLORS['primary']}'>📋 Catalogue des cas d'usage</h2>", unsafe_allow_html=True)

    col_reset, _ = st.columns([1, 5])
    with col_reset:
        if st.button("🔄 Réinitialiser démo"):
            st.session_state.use_cases = [dict(uc) for uc in DEMO_USE_CASES]
            st.session_state.autoscore_cache = {}
            st.rerun()

    # ── Add new use case ──
    with st.expander("➕ Ajouter un cas d'usage", expanded=False):
        with st.form("add_uc_form", clear_on_submit=True):
            n1, n2 = st.columns(2)
            nom_new  = n1.text_input("Nom du cas d'usage *")
            cat_new  = n2.selectbox("Catégorie", CATEGORIES)
            desc_new = st.text_area("Description (plus elle est précise, meilleur sera l'auto-scoring)", height=80)

            if api_key:
                use_autoscore = st.checkbox("🤖 Auto-scorer avec Claude Haiku", value=True,
                    help="Claude analyse la description et propose les 5 scores automatiquement")
            else:
                use_autoscore = False
                st.caption("Entrez une clé API en sidebar pour activer l'auto-scoring.")

            if not use_autoscore:
                st.markdown("**Scores manuels (1 = très faible · 10 = excellent)**")
                s1,s2,s3,s4,s5 = st.columns(5)
                imp_new = s1.slider("Impact",     1,10,7,key="imp_new")
                fai_new = s2.slider("Faisabilité",1,10,6,key="fai_new")
                del_new = s3.slider("Délai",      1,10,5,key="del_new")
                ali_new = s4.slider("Alignement", 1,10,7,key="ali_new")
                ris_new = s5.slider("Risque",     1,10,8,key="ris_new")
            else:
                imp_new = fai_new = del_new = ali_new = ris_new = 5  # placeholders

            submitted = st.form_submit_button("Ajouter")
            if submitted:
                if not nom_new.strip():
                    st.error("Le nom est obligatoire.")
                else:
                    if use_autoscore and desc_new.strip():
                        with st.spinner("Claude analyse le cas d'usage…"):
                            result = autoscore_with_claude(nom_new, desc_new, cat_new, api_key)
                        if result:
                            sc = result["scores"]
                            st.session_state.use_cases.append({
                                "nom": nom_new, "categorie": cat_new, "description": desc_new,
                                "impact": sc["impact"], "faisabilite": sc["faisabilite"],
                                "delai_valeur": sc["delai_valeur"], "alignement": sc["alignement"],
                                "risque": sc["risque"],
                            })
                            st.session_state.autoscore_cache[nom_new] = result
                            st.success(f"✅ « {nom_new} » ajouté avec scores auto-générés.")
                            st.rerun()
                        else:
                            st.error("Auto-scoring échoué. Ajoutez manuellement.")
                    else:
                        st.session_state.use_cases.append({
                            "nom": nom_new, "categorie": cat_new, "description": desc_new,
                            "impact": imp_new, "faisabilite": fai_new, "delai_valeur": del_new,
                            "alignement": ali_new, "risque": ris_new,
                        })
                        st.success(f"✅ « {nom_new} » ajouté.")
                        st.rerun()

    st.divider()

    # ── List existing use cases ──
    for idx, uc in enumerate(st.session_state.use_cases):
        sc     = compute_score(uc, st.session_state.weights)
        quad   = get_quadrant(uc["impact"], uc["faisabilite"])
        badge_cls, badge_lbl, _ = QUAD_META[quad]
        col_exp, col_ai, col_del = st.columns([10, 2, 1])

        with col_exp:
            with st.expander(f"**{uc['nom']}** — {sc}/10  |  {badge_lbl}  |  {uc['categorie']}", expanded=False):
                # Show auto-score rationale if available
                cache = st.session_state.autoscore_cache.get(uc["nom"])
                if cache and "rationale" in cache:
                    rat = cache["rationale"]
                    dim_labels = {"impact":"Impact","faisabilite":"Faisabilité","delai_valeur":"Délai","alignement":"Alignement","risque":"Risque"}
                    primary_color = COLORS["primary"]
                    muted_color = COLORS["text_muted"]
                    html_rationale = "".join(
                        f"<div style='margin:3px 0;font-size:.82rem'><span style='color:{primary_color};font-weight:600'>{dim_labels[k]}</span> — {v}</div>"
                        for k,v in rat.items() if k in dim_labels
                    )
                    st.markdown(f"""<div class='ai-score-box'>
                      <div style='font-size:.78rem;color:{muted_color};margin-bottom:8px'>🤖 Scores auto-générés par Claude Haiku</div>
                      {html_rationale}
                    </div>""", unsafe_allow_html=True)

                d1,d2,d3,d4,d5 = st.columns(5)
                new_imp = d1.slider("Impact",     1,10,uc["impact"],      key=f"imp_{idx}")
                new_fai = d2.slider("Faisabilité",1,10,uc["faisabilite"], key=f"fai_{idx}")
                new_del = d3.slider("Délai",      1,10,uc["delai_valeur"],key=f"del_{idx}")
                new_ali = d4.slider("Alignement", 1,10,uc["alignement"],  key=f"ali_{idx}")
                new_ris = d5.slider("Risque",     1,10,uc["risque"],       key=f"ris_{idx}")
                new_desc = st.text_area("Description", value=uc["description"], key=f"desc_{idx}", height=60)
                if st.button("💾 Sauvegarder", key=f"save_{idx}"):
                    st.session_state.use_cases[idx].update({"impact":new_imp,"faisabilite":new_fai,
                        "delai_valeur":new_del,"alignement":new_ali,"risque":new_ris,"description":new_desc})
                    st.rerun()

        with col_ai:
            if api_key:
                if st.button("🤖 Re-scorer", key=f"rescore_{idx}", help="Relancer l'auto-scoring Claude"):
                    with st.spinner("…"):
                        result = autoscore_with_claude(uc["nom"], uc["description"], uc["categorie"], api_key)
                    if result:
                        sc_r = result["scores"]
                        st.session_state.use_cases[idx].update({
                            "impact":sc_r["impact"],"faisabilite":sc_r["faisabilite"],
                            "delai_valeur":sc_r["delai_valeur"],"alignement":sc_r["alignement"],"risque":sc_r["risque"],
                        })
                        st.session_state.autoscore_cache[uc["nom"]] = result
                        st.rerun()

        with col_del:
            if st.button("🗑", key=f"del_{idx}", help="Supprimer"):
                st.session_state.use_cases.pop(idx)
                st.session_state.autoscore_cache.pop(uc["nom"], None)
                st.rerun()

    st.caption("Construit avec l'IA — Gisèle Metouck · Portfolio Data & IA")

# ══════════════════════════════════════════════════════════════════════════════════
# TAB 2 — Matrice + Benchmark sectoriel (Option B)
# ══════════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown(f"<h2 style='color:{COLORS['primary']}'>📊 Matrice Impact × Faisabilité</h2>", unsafe_allow_html=True)

    show_bench = secteur != "(Aucun)" and secteur in BENCHMARKS

    quad_colors = {
        "Quick Win":     COLORS["primary"],
        "Strategic Bet": COLORS["warning"],
        "Fill-in":       COLORS["info"],
        "Questionable":  COLORS["danger"],
    }

    fig_bubble = go.Figure()

    # ── Benchmark overlay (Option B) ──
    if show_bench:
        bench_data = BENCHMARKS[secteur]["cas_types"]
        bx = [v["faisabilite"] for v in bench_data.values()]
        by = [v["impact"]      for v in bench_data.values()]
        bt = list(bench_data.keys())
        bs = [v.get("source","") for v in bench_data.values()]
        fig_bubble.add_trace(go.Scatter(
            x=bx, y=by,
            mode="markers",
            name=f"Benchmark {secteur}",
            marker=dict(size=14, color="rgba(255,255,255,0.0)",
                        line=dict(color="rgba(255,255,255,0.5)", width=2),
                        symbol="circle-open"),
            text=bt,
            customdata=[[t,s] for t,s in zip(bt,bs)],
            hovertemplate="<b>Benchmark : %{customdata[0]}</b><br>Impact : %{y}/10 | Faisabilité : %{x}/10<br><i>Source : %{customdata[1]}</i><extra></extra>",
        ))

    # ── User use cases ──
    for quad, color in quad_colors.items():
        sub = df[df.quadrant == quad]
        if sub.empty: continue
        fig_bubble.add_trace(go.Scatter(
            x=sub["faisabilite"], y=sub["impact"],
            mode="markers+text",
            name=quad,
            text=sub["nom"].str[:22],
            textposition="top center",
            textfont=dict(size=10, color="white"),
            marker=dict(size=sub["score"]*5+8, color=color, opacity=0.85,
                        line=dict(color="white", width=1)),
            customdata=sub[["nom","score","categorie","description"]].values,
            hovertemplate="<b>%{customdata[0]}</b><br>Score : %{customdata[1]}/10<br>Impact : %{y}/10 | Faisabilité : %{x}/10<br>%{customdata[2]}<br><i>%{customdata[3]}</i><extra></extra>",
        ))

    fig_bubble.add_hline(y=6, line_dash="dash", line_color="rgba(255,255,255,0.2)")
    fig_bubble.add_vline(x=6, line_dash="dash", line_color="rgba(255,255,255,0.2)")
    for (x,y,txt) in [(8.5,0.6,"FILL-IN"),(8.5,9.6,"QUICK WIN"),(0.6,0.6,"QUESTIONABLE"),(0.6,9.6,"STRATEGIC BET")]:
        fig_bubble.add_annotation(x=x,y=y,text=txt,showarrow=False,font=dict(size=9,color="rgba(255,255,255,0.2)"),xanchor="center")

    fig_bubble.update_layout(
        **CHART_DEFAULTS,
        title=f"{'Portefeuille vs Benchmark ' + secteur if show_bench else 'Positionnement des cas d'usage'} — taille = score composite",
        height=520,
        xaxis=dict(**CHART_DEFAULTS["xaxis"], title="Faisabilité Technique", range=[0,10.5]),
        yaxis=dict(**CHART_DEFAULTS["yaxis"], title="Impact Business",       range=[0,10.5]),
    )
    st.plotly_chart(fig_bubble, use_container_width=True, key="bubble_chart")

    if show_bench:
        st.markdown(f"""<div class='alert-box alert-info'>
          ⚪ Les cercles vides représentent les benchmarks secteur <strong>{secteur}</strong>.
          Vos cas d'usage (cercles pleins) positionnés au-dessus ou à droite des benchmarks indiquent
          un avantage concurrentiel sur cette dimension. Source : rapports McKinsey, BCG, Gartner 2024.
        </div>""", unsafe_allow_html=True)

        # ── Per-use-case benchmark comparison ──
        st.divider()
        st.markdown(f"<h3 style='color:{COLORS['primary']}'>Votre portefeuille vs. Benchmark {secteur}</h3>", unsafe_allow_html=True)

        bench_rows = []
        for uc in st.session_state.use_cases:
            ct_name, ct_data = find_best_benchmark(secteur, uc["categorie"], uc["description"])
            if ct_data:
                dims = ["impact","faisabilite","delai_valeur","alignement","risque"]
                dim_labels = {"impact":"Impact","faisabilite":"Faisabilité","delai_valeur":"Délai","alignement":"Alignement","risque":"Risque"}
                row = {"Cas d'usage": uc["nom"], "Type référence": ct_name}
                for d in dims:
                    delta = uc[d] - ct_data[d]
                    row[dim_labels[d]] = f"{uc[d]:.0f} (Δ {'+' if delta>=0 else ''}{delta:.1f})"
                bench_rows.append(row)

        if bench_rows:
            df_bench = pd.DataFrame(bench_rows).set_index("Cas d'usage")
            st.dataframe(df_bench, use_container_width=True)
            st.caption(f"Δ = votre score − benchmark médian secteur {secteur}. Vert = au-dessus du marché. Source : {BENCHMARKS[secteur]['description']}.")
    else:
        # Quadrant cards
        st.divider()
        qc1,qc2,qc3,qc4 = st.columns(4)
        for col, quad in zip([qc1,qc2,qc3,qc4], ["Quick Win","Strategic Bet","Fill-in","Questionable"]):
            badge_cls,badge_lbl,desc = QUAD_META[quad]
            count = (df.quadrant==quad).sum()
            names = df[df.quadrant==quad]["nom"].tolist()
            with col:
                st.markdown(f"""<div class='quadrant-card'>
                  <div class='metric-label'>{badge_lbl}</div>
                  <div class='metric-val' style='font-size:1.8rem'>{count}</div>
                  <p style='font-size:.78rem;color:{COLORS["text_muted"]};margin-top:6px'>{desc}</p>
                  {"".join(f"<div style='font-size:.78rem;color:white;margin:2px 0'>• {n[:30]}</div>" for n in names)}
                </div>""", unsafe_allow_html=True)

    st.caption("Construit avec l'IA — Gisèle Metouck · Portfolio Data & IA")

# ══════════════════════════════════════════════════════════════════════════════════
# TAB 3 — Classement + Radar
# ══════════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown(f"<h2 style='color:{COLORS['primary']}'>🏆 Classement détaillé</h2>", unsafe_allow_html=True)

    fcol1, fcol2 = st.columns(2)
    filter_quad = fcol1.multiselect("Quadrant", list(QUAD_META.keys()), default=list(QUAD_META.keys()))
    filter_cat  = fcol2.multiselect("Catégorie", sorted(df["categorie"].unique()), default=list(df["categorie"].unique()))
    df_f = df[df.quadrant.isin(filter_quad) & df.categorie.isin(filter_cat)]

    if df_f.empty:
        st.markdown("<div class='alert-box alert-info'>ℹ Aucun cas ne correspond aux filtres.</div>", unsafe_allow_html=True)
    else:
        for i, row in df_f.iterrows():
            sc = row["score"]; col_sc = score_color(sc)
            badge_cls, badge_lbl, _ = QUAD_META[row["quadrant"]]
            has_ai = row["nom"] in st.session_state.autoscore_cache
            ai_badge = f"<span class='badge badge-qw' style='font-size:.68rem'>🤖 Auto-scoré</span>" if has_ai else ""
            st.markdown(f"""
            <div class='uc-row' style='border-left-color:{col_sc}'>
              <div style='flex:0 0 36px;font-size:1.2rem;font-weight:700;color:{COLORS["text_muted"]}'>{i}</div>
              <div style='flex:1'>
                <div style='font-weight:600;font-size:1rem'>{row["nom"]} {ai_badge}</div>
                <div style='font-size:.78rem;color:{COLORS["text_muted"]}'>{row["categorie"]} · {str(row["description"])[:80]}…</div>
                <div style='margin-top:4px'><span class='badge {badge_cls}'>{badge_lbl}</span></div>
              </div>
              <div style='text-align:right;min-width:90px'>
                <span class='score-pill' style='background:rgba(0,0,0,0.3);border:1px solid {col_sc};color:{col_sc}'>{sc}/10</span>
                <div style='margin-top:6px;background:rgba(255,255,255,0.1);border-radius:4px;height:4px'>
                  <div style='width:{int(sc*10)}%;background:{col_sc};height:4px;border-radius:4px'></div>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

        st.divider()
        st.markdown(f"<h3 style='color:{COLORS['primary']}'>Profil radar</h3>", unsafe_allow_html=True)
        uc_select = st.selectbox("Cas d'usage", df_f["nom"].tolist())
        uc_row = df_f[df_f.nom == uc_select].iloc[0]

        dims   = ["Impact Business","Faisabilité","Délai Valeur","Alignement","Risque/Conf."]
        vals   = [uc_row["impact"],uc_row["faisabilite"],uc_row["delai_valeur"],uc_row["alignement"],uc_row["risque"]]

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=vals+vals[:1], theta=dims+dims[:1], fill="toself", name=uc_select,
            fillcolor="rgba(0,255,136,0.15)", line=dict(color=COLORS["primary"],width=2)))

        # Add benchmark overlay on radar if secteur selected
        if show_bench:
            ct_name, ct_data = find_best_benchmark(secteur, uc_row["categorie"], uc_row["description"])
            if ct_data:
                bvals = [ct_data["impact"],ct_data["faisabilite"],ct_data["delai_valeur"],ct_data["alignement"],ct_data["risque"]]
                fig_radar.add_trace(go.Scatterpolar(
                    r=bvals+bvals[:1], theta=dims+dims[:1], fill="toself",
                    name=f"Benchmark {ct_name[:20]}",
                    fillcolor="rgba(255,215,0,0.08)", line=dict(color=COLORS["warning"],width=1.5,dash="dot")))

        radar_layout = {k:v for k,v in CHART_DEFAULTS.items() if k not in ("xaxis","yaxis")}
        fig_radar.update_layout(**radar_layout, title=f"{uc_select[:40]} — Profil vs Benchmark", height=380,
            polar=dict(bgcolor="#1a1a2e",
                radialaxis=dict(visible=True,range=[0,10],tickfont=dict(color="#888"),gridcolor="rgba(255,255,255,0.1)"),
                angularaxis=dict(tickfont=dict(color="white"),gridcolor="rgba(255,255,255,0.1)")))
        st.plotly_chart(fig_radar, use_container_width=True, key="radar_chart")

    st.caption("Construit avec l'IA — Gisèle Metouck · Portfolio Data & IA")

# ══════════════════════════════════════════════════════════════════════════════════
# TAB 4 — Simulation what-if
# ══════════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown(f"<h2 style='color:{COLORS['primary']}'>🔬 Simulation What-If</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{COLORS['text_muted']}'>Impact des pondérations sur le classement. Modifiez les poids en sidebar.</p>", unsafe_allow_html=True)

    profiles = {
        "Actuel":             dict(st.session_state.weights),
        "Priorité ROI":       {"impact":50,"faisabilite":20,"delai_valeur":15,"alignement":10,"risque":5},
        "Priorité rapidité":  {"impact":20,"faisabilite":20,"delai_valeur":50,"alignement":5, "risque":5},
        "Priorité sécurité":  {"impact":20,"faisabilite":20,"delai_valeur":10,"alignement":10,"risque":40},
    }

    rows_sim = []
    for uc in st.session_state.use_cases:
        row_r = {"nom": uc["nom"]}
        for pname, pw in profiles.items():
            row_r[pname] = compute_score(uc, pw)
        rows_sim.append(row_r)
    df_sim = pd.DataFrame(rows_sim).set_index("nom")

    fig_sim = go.Figure()
    sim_colors = [COLORS["primary"],COLORS["warning"],COLORS["info"],COLORS["danger"]]
    for pname, color in zip(profiles.keys(), sim_colors):
        fig_sim.add_trace(go.Bar(name=pname, x=df_sim.index, y=df_sim[pname], marker_color=color, opacity=0.85))

    fig_sim.update_layout(**CHART_DEFAULTS, title="Score par profil de pondération", barmode="group", height=420,
        xaxis=dict(**CHART_DEFAULTS["xaxis"],tickangle=-30,tickfont=dict(size=10)),
        yaxis=dict(**CHART_DEFAULTS["yaxis"],title="Score /10",range=[0,10.5]))
    st.plotly_chart(fig_sim, use_container_width=True, key="sim_chart")

    st.divider()
    st.markdown(f"<h3 style='color:{COLORS['primary']}'>Impact sur le classement</h3>", unsafe_allow_html=True)
    rank_rows = []
    for pname, pw in profiles.items():
        ranked = sorted(st.session_state.use_cases, key=lambda u: compute_score(u, pw), reverse=True)
        for rank, uc in enumerate(ranked, 1):
            rank_rows.append({"Profil":pname,"Rang":rank,"Cas d'usage":uc["nom"]})
    df_rank = pd.DataFrame(rank_rows).pivot(index="Cas d'usage",columns="Profil",values="Rang")
    df_rank = df_rank.sort_values("Actuel")
    st.dataframe(df_rank.style.background_gradient(cmap="RdYlGn_r",vmin=1,vmax=len(st.session_state.use_cases)).format("{:.0f}"),
                 use_container_width=True)
    st.caption("Classement (1 = meilleur). Vert = bien classé.")

    st.caption("Construit avec l'IA — Gisèle Metouck · Portfolio Data & IA")

# ══════════════════════════════════════════════════════════════════════════════════
# TAB 5 — Rapport & IA
# ══════════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown(f"<h2 style='color:{COLORS['primary']}'>📄 Rapport & Narrative IA</h2>", unsafe_allow_html=True)

    # Summary table
    st.markdown(f"<h3 style='color:{COLORS['primary']}'>Synthèse portefeuille</h3>", unsafe_allow_html=True)
    cols_disp = ["nom","categorie","score","quadrant","impact","faisabilite","delai_valeur","alignement","risque"]
    rename_map = {"nom":"Cas d'usage","categorie":"Catégorie","score":"Score","quadrant":"Quadrant",
                  "impact":"Impact","faisabilite":"Faisabilité","delai_valeur":"Délai","alignement":"Alignement","risque":"Risque"}
    st.dataframe(df[cols_disp].rename(columns=rename_map)
                   .style.background_gradient(subset=["Score"],cmap="RdYlGn",vmin=0,vmax=10),
                 use_container_width=True)

    # Benchmark summary if secteur selected
    if show_bench:
        st.divider()
        st.markdown(f"<h3 style='color:{COLORS['primary']}'>Position vs. Benchmark {secteur}</h3>", unsafe_allow_html=True)
        above_bench = []
        for uc in st.session_state.use_cases:
            _, ct_data = find_best_benchmark(secteur, uc["categorie"], uc["description"])
            if ct_data:
                avg_uc    = (uc["impact"]+uc["faisabilite"]+uc["delai_valeur"]+uc["alignement"]+uc["risque"])/5
                avg_bench = (ct_data["impact"]+ct_data["faisabilite"]+ct_data["delai_valeur"]+ct_data["alignement"]+ct_data["risque"])/5
                delta = avg_uc - avg_bench
                above_bench.append({"nom":uc["nom"],"avg_uc":avg_uc,"avg_bench":avg_bench,"delta":delta})
        if above_bench:
            df_pos = pd.DataFrame(above_bench).sort_values("delta",ascending=False)
            winners = df_pos[df_pos.delta > 0]
            losers  = df_pos[df_pos.delta <= 0]
            if not winners.empty:
                st.markdown(f"<div class='alert-box alert-ok'>✅ <strong>{len(winners)} cas d'usage au-dessus du benchmark</strong> : {', '.join(winners['nom'].tolist())}</div>", unsafe_allow_html=True)
            if not losers.empty:
                st.markdown(f"<div class='alert-box alert-warn'>⚠ <strong>{len(losers)} cas d'usage en-dessous du benchmark</strong> : {', '.join(losers['nom'].tolist())}</div>", unsafe_allow_html=True)

    st.divider()

    # AI narrative
    st.markdown(f"<h3 style='color:{COLORS['primary']}'>🤖 Narrative exécutive (Claude Haiku)</h3>", unsafe_allow_html=True)

    if api_key:
        if st.button("Générer la narrative"):
            with st.spinner("Analyse du portefeuille en cours…"):
                st.session_state.narrative_cache = generate_narrative(df, company, secteur, api_key)
        if st.session_state.narrative_cache:
            st.markdown(f"""<div style='background:{COLORS["bg_surface"]};border-left:4px solid {COLORS["primary"]};
              border-radius:8px;padding:20px;margin:12px 0;line-height:1.7;font-size:.95rem'>
              {st.session_state.narrative_cache.replace(chr(10),"<br>")}
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='alert-box alert-info'>ℹ Entrez votre clé API en sidebar pour générer la narrative.</div>", unsafe_allow_html=True)
        top1 = df.iloc[0]
        top2 = df.iloc[1] if len(df)>1 else None
        fallback = f"""L'analyse de votre portefeuille de {len(df)} cas d'usage IA révèle {n_qw} Quick Win{'s' if n_qw>1 else ''} et {n_sb} Strategic Bet{'s' if n_sb>1 else ''}.

La priorité absolue est <strong style='color:{COLORS["primary"]}'>{top1["nom"]}</strong> (score {top1["score"]}/10).
{f'En parallèle, <strong>{top2["nom"]}</strong> (score {top2["score"]}/10) mérite d\'être planifié.' if top2 is not None else ""}

Le score moyen du portefeuille ({avg_score:.1f}/10) indique un pipeline équilibré.
Connectez votre clé API pour une analyse approfondie et personnalisée."""
        st.markdown(f"""<div style='background:{COLORS["bg_surface"]};border-left:4px solid {COLORS["text_muted"]};
          border-radius:8px;padding:20px;margin:12px 0;line-height:1.7;font-size:.95rem;color:{COLORS["text_muted"]}'>
          {fallback}</div>""", unsafe_allow_html=True)

    st.divider()

    # PDF export
    st.markdown(f"<h3 style='color:{COLORS['primary']}'>📥 Export PDF</h3>", unsafe_allow_html=True)
    if st.button("Générer le rapport PDF"):
        with st.spinner("Génération…"):
            pdf_bytes = generate_pdf(df, company, st.session_state.weights, secteur)
        if pdf_bytes:
            st.download_button(
                label="⬇ Télécharger le rapport",
                data=pdf_bytes,
                file_name=f"ai_prioritizer_{company.lower().replace(' ','_')}_{datetime.today().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
            )
        else:
            st.error("fpdf2 non installé.")

    st.caption("Construit avec l'IA — Gisèle Metouck · Portfolio Data & IA")
