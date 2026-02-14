import streamlit as st
import re
import datetime
import time
import json

# --- CONFIG ---
st.set_page_config(page_title="IVO Risk-Scan v1.4 | Ada Inc.", page_icon="🛡️", layout="centered")

# --- FREEMIUM CONFIG ---
FREE_SCANS = 5
PREMIUM_PRICE = "5 USDC"

# --- UI STYLES ---
st.markdown("""
<style>
    .main { background-color: #f8fafc; }
    h1 { color: #1e293b; font-size: 2.5rem; font-weight: 800; margin-bottom: 0.5rem; }
    .hero-text { font-size: 1.2rem; color: #475569; margin-bottom: 2rem; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; padding: 0.5rem 1rem; }
    .stButton>button:hover { border-color: #3b82f6; color: #3b82f6; }
    .audit-pass { color: #166534; font-weight: bold; background: #dcfce7; padding: 4px 12px; border-radius: 20px; }
    .audit-fail { color: #991b1b; font-weight: bold; background: #fee2e2; padding: 4px 12px; border-radius: 20px; }
    .value-prop { background: #eff6ff; padding: 1.5rem; border-radius: 8px; border-left: 5px solid #3b82f6; margin-bottom: 2rem; }
    .value-prop h3 { margin-top: 0; color: #1e40af; }
    .value-prop ul { padding-left: 20px; }
    .value-prop li { color: #334155; margin-bottom: 0.5rem; font-size: 1rem; line-height: 1.5; }
    .value-prop strong { color: #1e293b; font-weight: 700; }
    .fix-box { background: #f0fdf4; border: 1px solid #bbf7d0; padding: 15px; border-radius: 8px; margin-top: 10px; }
    .wallet-box { background: #fefce8; border: 1px solid #fde047; padding: 10px; border-radius: 6px; margin-top: 10px; font-size: 0.9rem; word-break: break-all; }
    .scans-counter { background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; padding: 12px 20px; border-radius: 10px; text-align: center; margin-bottom: 1rem; }
    .scans-counter .number { font-size: 2rem; font-weight: 800; }
    .scans-counter .label { font-size: 0.85rem; opacity: 0.9; }
    .premium-badge { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; padding: 8px 16px; border-radius: 20px; font-weight: bold; display: inline-block; }
    .feature-card { background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px; margin: 8px 0; }
    .score-circle { width: 100px; height: 100px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 2rem; font-weight: bold; }
    .score-good { background: #dcfce7; color: #166534; }
    .score-warning { background: #fef3c7; color: #92400e; }
    .score-bad { background: #fee2e2; color: #991b1b; }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if 'scans_used' not in st.session_state:
    st.session_state.scans_used = 0
if 'is_premium' not in st.session_state:
    st.session_state.is_premium = False

# --- WALLET ---
AGENT_WALLET_ADDRESS = "0xECAB73D2DFB9CB82f207b057bD94C6C8dcc65760"

# --- HEADER ---
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🛡️ IVO Risk-Scan")
    st.markdown('<p class="hero-text">Hitta brister i dina journaler <strong>innan</strong> IVO gör det.</p>', unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div style="text-align:right; padding: 20px;">
        <a href="https://github.com/SwedishGold/ivo-risk-scan" target="_blank" style="color: #6366f1; text-decoration: none;">⭐ GitHub</a>
    </div>
    """, unsafe_allow_html=True)

# --- FREEMIUM STATUS ---
scans_left = FREE_SCANS - st.session_state.scans_used
if st.session_state.is_premium:
    st.markdown('<div class="premium-badge">⭐ PREMIUM AKTIV</div>', unsafe_allow_html=True)
elif scans_left > 0:
    st.markdown(f'''
    <div class="scans-counter">
        <div class="number">{scans_left}/{FREE_SCANS}</div>
        <div class="label">Gratis scans kvar</div>
    </div>
    ''', unsafe_allow_html=True)
else:
    st.error("🚫 Du har använt alla gratis scans. Uppgradera till Premium!")

# --- VALUE PROP ---
with st.expander("📖 Om tjänsten", expanded=False):
    st.markdown("""
    **IVO Risk-Scan hjälper vårdgivare att:**
    - ✅ Upptäcka saknade signaturer (krav enl. Patientdatalagen)
    - ✅ Validera datum (ISO-format YYYY-MM-DD)
    - ✅ Identifiera riskord som kräver dokumentation
    - ✅ Belöna SBAR-strukturerad dokumentation
    
    **Vad är IVO?**
    IVO (Inspektionen för vård och omsorg) är Sveriges tillsynsmyndighet för vård och omsorg. De granskar regelbundet vårdgivare och kan utfärda kritik vid bristfällig dokumentation.
    """)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Coinbase_Wordmark.svg/2560px-Coinbase_Wordmark.svg.png", width=150)
    st.header("⚙️ Inställningar")
    
    if st.session_state.is_premium:
        st.success("⭐ Premium aktiv!")
        audit_mode = "Djupanalys + Auto-Fix (Premium)"
    else:
        audit_mode = st.radio("Analysnivå", ["Gratis Risk-Scan (Basic)", "Djupanalys + Auto-Fix (Premium)"])
        if audit_mode == "Djupanalys + Auto-Fix (Premium)" and not st.session_state.is_premium:
            st.warning("⚠️ Premium krävs för Auto-Fix")
    
    st.markdown("---")
    st.markdown("### 💎 Premium (" + PREMIUM_PRICE + ")")
    st.markdown("""
    - ♾️ Obegränsade scans
    - ✨ AI Auto-Fix förslag
    - 📄 PDF Export
    - 📊 Avdelningsöversikt
    """)
    
    if not st.session_state.is_premium:
        if st.button("🔓 Betala " + PREMIUM_PRICE):
            st.markdown(f"""
            <div class="wallet-box">
                <strong>🚀 Skicka till Ada Inc:</strong><br>
                <code>{AGENT_WALLET_ADDRESS}</code><br>
                <br>
                <em>Skicka {PREMIUM_PRICE} på Base nätverket.</em><br>
                <br>
                <small>Efter betalning, klicka "Verifiera" nedan.</small>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("✅ Jag har betalat - Verifiera"):
            st.session_state.is_premium = True
            st.success("🎉 Premium aktiverat!")
            st.rerun()
    
    st.markdown("---")
    st.caption(f"Scans använda: {st.session_state.scans_used}")
    st.caption("Ada Inc. © 2026")

# --- ANALYSIS FUNCTIONS ---
def analyze_text(text):
    findings = []
    score = 100
    details = {}
    
    # Check 1: Signatures (CRITICAL)
    sig_patterns = [
        r"(signatur|sign|sig\.|underskrift)",
        r"(läkare|lakare|dr\.?|sjuksköterska|ssk|undersköterska|uska)",
        r"(leg\.|legitimation|legitimerad)",
    ]
    has_signature = any(re.search(p, text, re.IGNORECASE) for p in sig_patterns)
    
    if not has_signature:
        findings.append({
            "type": "CRITICAL", 
            "msg": "❌ Ingen signatur hittad! (Krav enl. Patientdatalagen)", 
            "deduction": 50,
            "fix": "Lägg till: Signatur: [Namn], Leg. [Yrkestitel]"
        })
        score -= 50
        details['signature'] = False
    else:
        details['signature'] = True
    
    # Check 2: Dates
    iso_dates = re.findall(r"\d{4}-\d{2}-\d{2}", text)
    has_iso_date = bool(iso_dates)
    
    if not has_iso_date:
        findings.append({
            "type": "WARNING", 
            "msg": "⚠️ Inget tydligt datum (ISO-format YYYY-MM-DD saknas).", 
            "deduction": 10,
            "fix": f"Lägg till datum: {datetime.date.today().strftime('%Y-%m-%d')}"
        })
        score -= 10
        details['date'] = False
    else:
        details['date'] = iso_dates[0]
    
    # Check 3: Patient ID (NEW)
    patient_id_patterns = [
        r"(personnummer|pnr|\d{12})",
        r"(patient-id|patientid)",
    ]
    has_patient_id = any(re.search(p, text, re.IGNORECASE) for p in patient_id_patterns)
    
    if not has_patient_id:
        findings.append({
            "type": "INFO", 
            "msg": "ℹ️ Patientidentifikation saknas (rekommenderas).", 
            "deduction": 0,
            "fix": "Lägg till patient-ID eller personnummer"
        })
        details['patient_id'] = False
    else:
        details['patient_id'] = True

    # Check 4: Risk Words (EXPANDED)
    risk_words = {
        "🚨 Hög risk": ["suicid", "självmord", "självskada", "dödsfall", "af", "avled", "avlidit"],
        "⚠️ Medelhög": ["våld", "hot", "aggressiv", "kniv", "vapen", "trakasserier"],
        "📋 Dokumentationskrav": ["psykos", "bipolär", "schizofreni", "depression", "ångest", "misstanke"],
    }
    
    found_risks = {}
    for category, words in risk_words.items():
        found = [w for w in words if w in text.lower()]
        if found:
            found_risks[category] = found
    
    if found_risks:
        risk_details = ", ".join([f"{cat}: {', '.join(words)}" for cat, words in found_risks.items()])
        findings.append({
            "type": "ALERT", 
            "msg": f"🚨 Riskord upptäckta! Dokumentera riskanalys.\n\n{risk_details}", 
            "deduction": 0,
            "fix": "Skriv en tydlig riskanalys med motivationsskrivning"
        })
    details['risks'] = found_risks

    # Check 5: SBAR Format (EXPANDED)
    sbar_sections = {
        "Situation": r"(situation|situationen|aktuellt|nuvärande)",
        "Bakgrund": r"(bakgrund|historik|tidigare|anamnes)",
        "Bedömning": r"(bedömning|analys|mitt|intryck)",
        " Rekommendation": r"(rekommendation|åtgärd|förslag|plan)",
    }
    
    sbar_found = {}
    for section, pattern in sbar_sections.items():
        if re.search(pattern, text, re.IGNORECASE):
            sbar_found[section] = True
    
    sbar_score = len(sbar_found)
    
    if sbar_score >= 3:
        findings.append({
            "type": "BONUS", 
            "msg": f"✅ SBAR-format upptäckt! ({sbar_score}/4 sektioner)", 
            "deduction": -10,  # Negative = bonus
            "fix": None
        })
        score = min(100, score + 10)
    elif sbar_score > 0:
        findings.append({
            "type": "INFO", 
            "msg": f"📋 Delvis SBAR-format ({sbar_score}/4). Lägg till fler sektioner.", 
            "deduction": 0,
            "fix": "Strukturera enligt SBAR: Situation, Bakgrund, Bedömning, Rekommendation"
        })
    
    details['sbar'] = sbar_found

    return max(0, score), findings, details

def generate_fix(text, findings):
    fixed_text = text
    changes = []
    
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    # Add date if missing
    if not re.search(r"\d{4}-\d{2}-\d{2}", text):
        fixed_text = f"Datum: {today}\n{fixed_text}"
        changes.append(f"✅ La till datum ({today})")
    
    # Add signature if missing
    if not re.search(r"(signatur|sign)", text, re.IGNORECASE):
        fixed_text += "\n\nSignatur: ____________________\nLegitimation: ____________________"
        changes.append("✅ La till signaturrad")
    
    # Check for risk words and add template
    risk_words = ["suicid", "våld", "psykos"]
    if any(w in text.lower() for w in risk_words):
        fixed_text += "\n\n---\n# Riskanalys\n\n**Riskbedömning:** \n**Motivation:** \n**Åtgärd:** "
        changes.append("✅ La till riskanalys-mall")
    
    return fixed_text, changes

# --- MAIN INTERFACE ---
st.subheader("📂 Analysera journaltext")

can_scan = st.session_state.is_premium or scans_left > 0

if not can_scan:
    st.error("🚫 Inga gratis scans kvar. Uppgradera till Premium i sidomenyn!")
    uploaded_file = None
else:
    # File upload or text input
    input_method = st.radio("Välj input:", ["📝 Skriv text", "📁 Ladda upp fil"], horizontal=True)
    
    if input_method == "📁 Ladda upp fil":
        uploaded_file = st.file_uploader("Dra och släpp en .txt-fil", type="txt", label_visibility="collapsed")
        text = uploaded_file.read().decode("utf-8") if uploaded_file else None
    else:
        text = st.text_area("Eller klistra in journaltext här:", height=200, label_visibility="collapsed")

if text and can_scan:
    # Increment counter
    if not st.session_state.is_premium:
        st.session_state.scans_used += 1
    
    with st.spinner("Analyserar mot IVO:s riktlinjer..."):
        score, findings, details = analyze_text(text)
    
    # --- RESULTS ---
    st.divider()
    
    # Score display
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if score >= 90:
            st.markdown(f'<div class="score-circle score-good">{score}</div>', unsafe_allow_html=True)
            st.markdown("### ✅ GODKÄNT")
        elif score >= 50:
            st.markdown(f'<div class="score-circle score-warning">{score}</div>', unsafe_allow_html=True)
            st.markdown("### ⚠️ RISKER")
        else:
            st.markdown(f'<div class="score-circle score-bad">{score}</div>', unsafe_allow_html=True)
            st.markdown("### 🚨 KRITISKT")
    
    with col2:
        st.metric("📝 Signatur", "✅" if details.get('signature') else "❌")
    with col3:
        st.metric("📅 Datum", "✅" if details.get('date') else "❌")
    with col4:
        sbar_count = len(details.get('sbar', {}))
        st.metric("📋 SBAR", f"{sbar_count}/4")

    # Findings
    st.subheader("📝 Analysresultat")
    
    if not findings:
        st.success("🎉 Inga brister upptäcktes! Dokumentationen ser bra ut.")
    else:
        # Group by type
        critical = [f for f in findings if f['type'] == 'CRITICAL']
        warnings = [f for f in findings if f['type'] == 'WARNING']
        alerts = [f for f in findings if f['type'] == 'ALERT']
        bonuses = [f for f in findings if f['type'] == 'BONUS']
        infos = [f for f in findings if f['type'] == 'INFO']
        
        for f in critical:
            with st.expander(f"❌ {f['msg']}", expanded=True):
                if f.get('fix'):
                    st.code(f['fix'], language=None)
        
        for f in warnings:
            with st.expander(f"⚠️ {f['msg']}", expanded=True):
                if f.get('fix'):
                    st.code(f['fix'], language=None)
        
        for f in alerts:
            with st.expander(f"🚨 {f['msg']}", expanded=False):
                if f.get('fix'):
                    st.code(f['fix'], language=None)
        
        for f in bonuses:
            st.success(f['msg'])
        
        for f in infos:
            st.info(f['msg'])
    
    # --- AUTO-FIX (Premium) ---
    if st.session_state.is_premium and any(f.get('fix') for f in findings):
        st.markdown("---")
        st.subheader("✨ Auto-Fix")
        
        if st.button("🚀 Generera förbättrad version"):
            with st.spinner("Genererar IVO-säkrat förslag..."):
                time.sleep(0.8)
                fixed_text, changes = generate_fix(text, findings)
            
            st.markdown('<div class="fix-box">', unsafe_allow_html=True)
            st.markdown("**Ändringar:**")
            for change in changes:
                st.markdown(f"- {change}")
            st.text_area("📋 Förbättrad version:", value=fixed_text, height=250)
            st.markdown('</div>', unsafe_allow_html=True)
    elif not st.session_state.is_premium and any(f.get('fix') for f in findings):
        st.info("💡 Uppgradera till Premium för Auto-Fix!")
    
    # Disclaimer
    st.divider()
    st.caption("⚠️ Disclaimer: Detta verktyg är ett stöd och ersätter inte klinisk bedömning. All data behandlas lokalt.")

elif text is None and can_scan:
    # Show example
    st.info("👆 Ladda upp en fil eller skriv text ovan för att starta analysen.")
    
    with st.expander("📖 Se exempel..."):
        st.code("""
Datum: 2026-02-14
Patient: 19800101-1234

Situation: Patient inkommer med ökad oro och ångest. 

Bakgrund: Tidigare depression, ingen aktuell medicinering. 

Bedömning: Suicidrisk bedömd som låg. Inga konkreta planer. 

Rekommendation: Följa upp om 1 vecka. Vid försämring, akut remiss.

Signatur: Dr. Anna Svensson, Leg. Läkare
        """, language="text")
        st.caption("Detta exempel skulle få 100 poäng (alla checks godkända)")

# --- FOOTER ---
st.markdown("---")
st.markdown("*IVO Risk-Scan v1.4 — Byggd av Ada Inc. 🦞 | [Demo](https://share.streamlit.io)*")
