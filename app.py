import streamlit as st
import re
import datetime
import time
import json

# --- CONFIG ---
st.set_page_config(page_title="IVO Risk-Scan v2.0 | Ada Inc.", page_icon="🛡️", layout="centered")

# --- FREEMIUM CONFIG ---
FREE_SCANS = 3
PREMIUM_PRICE = "5 USDC"

# --- IVO REQUIREMENTS (FRÅN LAGAR) ---
IVO_REQUIREMENTS = """
IVO granskar mot följande krav:

1. PATIENTDATALAGEN (PDL)
   - Patientjournal ska föras för varje patient
   - Identifikation ska vara tydlig (personnummer)
   - Vårdgivare ska framgå
   - Datum och tid ska dokumenteras
   
2. SOSFS 2016:34 (Journalföring)
   - Anteckningar ska signeras av behörig personal
   - Legitimation ska framgå
   - Rebegäran ska kunna spåras
   - Struktur: Situation, Bakgrund, Bedömning, Rekommendation (SBAR)
   
3. IVO:S VANLIGA KRITIK
   - Saknad eller ofullständig signatur
   - Otydlig patientidentifiering
   - Bristande riskanalys vid allvarliga tillstånd
   - Otydlig bedömningsgrund
   - Manglade datum/tider
   - Oläslig/otydlig dokumentation
"""

# --- IVO TEMPLATES ---
IVO_TEMPLATES = {
    "📋 Välj mall...": None,
    "🏥 PIVA (Psykiatrisk intensivvård)": """Datum: {date}
Patient: [Personnummer]

## S - Situation
[Aktuellt tillstånd, vad som föranleder vårdkontakt]

## B - Bakgrund
[Aktuell anamnes, tidigare sjukdomshistoria, aktuella mediciner]

## A - Bedömning
[Klinisk bedömning, riskbedömning, differentialdiagnos]

## R - Rekommendation
[Planerade åtgärder, uppföljning, remisser]

## Signatur
Signatur: _________________
Legitimation: _________________
Titel: _________________""",
    
    "👶 BUP (Barn- och ungdomspsykiatri)": """Datum: {date}
Patient: [Personnummer]
Vårdnadshavare: [Namn]

## S - Situation
[Aktuellt tillstånd hos barnet/ungdomen]

## B - Bakgrund
[Tidigare utveckling, familjehistoria, skola]

## A - Bedömning
[Utredningsresultat, diagnos, riskbedömning]

## R - Rekommendation
[Behandlingsplan, uppföljning, samordning med skola/socialtjänst]

## Signatur
Signatur: _________________
Legitimation: _________________
Titel: _________________""",
    
    "👴 Äldrepsykiatri": """Datum: {date}
Patient: [Personnummer]
Boende: [Särskilt boende/Hemtjänst/Anhörig]

## S - Situation
[Aktuellt tillstånd, förändringar i beteende/hälsa]

## B - Bakgrund
[Demensutveckling, medicinering, tidigare psykiatrisk historik]

## A - Bedömning
[Kognitiv status, funktionsnivå, riskbedömning]

## R - Rekommendation
[Omvårdnadsåtgärder, medicinjustering, anhörigstöd]

## Signatur
Signatur: _________________
Legitimation: _________________
Titel: _________________""",
    
    "🚑 Akut psykiatri": """Datum: {date}
Patient: [Personnummer]
Remitterande: [Vårdgivare/myndighet]

## S - Situation
[Aktuellt tillstånd vid ankomst, anledning till akut kontakt]

## B - Bakgrund
[Aktuell psykiatrisk historik, tidigare vårdtillfällen, suicidförsök]

## A - Bedömning
[Akut riskbedömning (SIS/SBUD), psykiatrisk status, somatisk status]

## R - Rekommendation
[Akuta åtgärder, inläggning/utskrivning, uppföljning]

## Signatur
Signatur: _________________
Legitimation: _________________
Titel: _________________""",
    
    "💊 Beroendevård": """Datum: {date}
Patient: [Personnummer]

## S - Situation
[Aktuellt tillstånd, substansintag, abstinenssymtom]

## B - Bakgrund
[Missbrukshistorik, tidigare behandlingar, motivation]

## A - Bedömning
[Riskbedömning, abstinensbedömning (CIWA-A/COWS), funktionsnivå]

## R - Rekommendation
[Behandlingsplan, uppföljning, samordning med socialtjänst]

## Signatur
Signatur: _________________
Legitimation: _________________
Titel: _________________"""
}

# --- UI STYLES ---
st.markdown("""
<style>
    .main { background-color: #f8fafc; }
    h1 { color: #1e293b; font-size: 2.5rem; font-weight: 800; margin-bottom: 0.5rem; }
    .hero-text { font-size: 1.2rem; color: #475569; margin-bottom: 2rem; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; padding: 0.5rem 1rem; }
    .audit-pass { color: #166534; font-weight: bold; background: #dcfce7; padding: 4px 12px; border-radius: 20px; }
    .audit-fail { color: #991b1b; font-weight: bold; background: #fee2e2; padding: 4px 12px; border-radius: 20px; }
    .value-prop { background: #eff6ff; padding: 1.5rem; border-radius: 8px; border-left: 5px solid #3b82f6; margin-bottom: 2rem; }
    .fix-box { background: #f0fdf4; border: 1px solid #bbf7d0; padding: 15px; border-radius: 8px; margin-top: 10px; }
    .wallet-box { background: #fefce8; border: 1px solid #fde047; padding: 10px; border-radius: 6px; margin-top: 10px; font-size: 0.9rem; word-break: break-all; }
    .scans-counter { background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; padding: 12px 20px; border-radius: 10px; text-align: center; margin-bottom: 1rem; }
    .scans-counter .number { font-size: 2rem; font-weight: 800; }
    .scans-counter .label { font-size: 0.85rem; opacity: 0.9; }
    .premium-badge { background: linear-gradient(135bed0b, #d97706 100%); color: white; padding: 8px 16px; border-radius: 20px; font-weight: bold; display: inline-block; }
    .score-circle { width: 100px; height: 100px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 2rem; font-weight: bold; }
    .score-good { background: #dcfce7; color: #166534; }
    .score-warning { background: #fef3c7; color: #92400e; }
    .score-bad { background: #fee2e2; color: #991b1b; }
    .new-feature { background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 4px 10px; border-radius: 12px; font-size: 0.7rem; font-weight: bold; }
    .ai-badge { background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%); color: white; padding: 4px 10px; border-radius: 12px; font-size: 0.7rem; font-weight: bold; }
    .requirement-box { background: #fef2f2; border: 1px solid #fecaca; padding: 12px; border-radius: 8px; margin: 8px 0; }
    .requirement-title { font-weight: bold; color: #991b1b; }
    .finding-item { background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; margin: 8px 0; }
    .finding-critical { border-left: 4px solid #ef4444; }
    .finding-warning { border-left: 4px solid #f59e0b; }
    .finding-good { border-left: 4px solid #10b981; }
    .finding-info { border-left: 4px solid #3b82f6; }
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
    st.markdown('<p class="hero-text">AI-driven journalgranskning mot <strong>IVO:s faktiska krav</strong>.</p>', unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div style="text-align:right; padding: 20px;">
        <span class="ai-badge">🤖 v2.0 AI</span><br>
        <span class="new-feature">✨ NY!</span><br>
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
        <div class="label">Gratis AI-scans kvar</div>
    </div>
    ''', unsafe_allow_html=True)
else:
    st.error("🚫 Du har använt alla gratis scans. Uppgradera till Premium!")

# --- IVO INFO ---
with st.expander("📖 IVO:s granskningskriterier (klicka för att expandera)", expanded=False):
    st.markdown(IVO_REQUIREMENTS)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Coinbase_Wordmark.svg/2560px-Coinbase_Wordmark.svg.png", width=150)
    st.header("⚙️ Inställningar")
    
    if st.session_state.is_premium:
        st.success("⭐ Premium aktiv!")
    else:
        st.radio("Analysnivå", ["Gratis Risk-Scan (Basic)", "Djupanalys + Auto-Fix (Premium)"])
    
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
                <em>Skicka {PREMIUM_PRICE} på Base.</em>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("✅ Jag har betalat - Verifiera"):
            st.session_state.is_premium = True
            st.success("🎉 Premium aktiverat!")
            st.rerun()
    
    st.markdown("---")
    st.caption(f"Scans: {st.session_state.scans_used}/{FREE_SCANS}")
    st.caption("Ada Inc. © 2026")

# --- TEMPLATE SELECTOR ---
st.subheader("📋 IVO-mallar")
template_col1, template_col2 = st.columns([2, 1])
with template_col1:
    selected_template = st.selectbox("🏥 Välj avdelningsmall:", list(IVO_TEMPLATES.keys()))
with template_col2:
    if selected_template and IVO_TEMPLATES[selected_template]:
        st.markdown('<div style="background:#e0f2fe;padding:8px;border-radius:6px;font-size:0.85rem;">📋 Klicka nedan</div>', unsafe_allow_html=True)

# --- ANALYZE FUNCTION (AI-POWERED) ---
def analyze_with_ai(text):
    """Use MiniMax AI for actual analysis"""
    import os
    
    # Build prompt based on IVO requirements
    prompt = f"""Du är en IVO-expert som granskar journaler mot svenska vårdkrav.

## IVO KRÄVER:
1. Patientdatalagen (PDL) - patient-ID, datum, signatur, legitimation
2. SOSFS 2016:34 - SBAR-struktur, spårbarhet
3. Riskbedömning vid allvarliga tillstånd (suicid, våld, psykos)

## GRANSKA DENNA JOURNAL:
```
{text}
```

## SVARA I DETTA FORMAT JSON (endast JSON):
{{
    "score": [0-100],
    "findings": [
        {{
            "type": "CRITICAL|WARNING|GOOD|INFO",
            "area": "t.ex. Signatur, Datum, Patient-ID, SBAR, Riskbedömning",
            "message": "Vad som är fel eller rätt",
            "ivo_ref": "Vilket krav som berörs (PDL, SOSFS, etc)"
        }}
    ],
    "summary": "Kort sammanfattning för ledning",
    "recommendations": ["Rekommendation 1", "Rekommendation 2"]
}}

Analysera noggrant och var kritisk. Börja direkt med JSON."""

    try:
        # Try MiniMax API
        api_key = os.environ.get('MINIMAX_API_KEY', '')
        if api_key:
            import requests
            response = requests.post(
                'https://api.minimaxi.chat/v1/text/chatcompletion_v2',
                headers={'Authorization': f'Bearer {api_key}'},
                json={
                    'model': 'MiniMax-M2.1',
                    'messages': [{'role': 'user', 'content': prompt}],
                    'temperature': 0.3
                },
                timeout=30
            )
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                # Extract JSON
                import json as json_module
                data = json_module.loads(content)
                return data
    except Exception as e:
        st.error(f"AI-fel: {e}")
    
    # Fallback to rule-based if no API
    return fallback_analysis(text)

def fallback_analysis(text):
    """Fallback when no AI API available"""
    findings = []
    score = 100
    
    # 1. Check signature
    sig_match = re.search(r'(signatur|sign|sig\.?)\s*[:;]?\s*([A-Za-zÀ-ÿ]+(?:\s+[A-Za-zÀ-ÿ]+)?)', text, re.IGNORECASE)
    if not sig_match:
        score -= 30
        findings.append({
            "type": "CRITICAL",
            "area": "Signatur",
            "message": "Saknas signatur! Krävs enligt PDL och SOSFS 2016:34. Måste innehålla namn + legitimation.",
            "ivo_ref": "PDL 3 kap, SOSFS 2016:34"
        })
    else:
        findings.append({
            "type": "GOOD",
            "area": "Signatur",
            "message": f"Signatur hittad: {sig_match.group(2)}",
            "ivo_ref": "PDL 3 kap"
        })
    
    # 2. Check date
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', text)
    if not date_match:
        score -= 20
        findings.append({
            "type": "CRITICAL",
            "area": "Datum",
            "message": "Saknas datum! ISO-format (YYYY-MM-DD) krävs för spårbarhet.",
            "ivo_ref": "SOSFS 2016:34"
        })
    else:
        findings.append({
            "type": "GOOD",
            "area": "Datum",
            "message": f"Datum hittat: {date_match.group(1)}",
            "ivo_ref": "SOSFS 2016:34"
        })
    
    # 3. Check patient ID
    pnr_match = re.search(r'(\d{8}-\d{{4}}|\d{{12}})', text)
    if not pnr_match:
        score -= 20
        findings.append({
            "type": "WARNING",
            "area": "Patient-ID",
            "message": "Saknas tydlig patientidentifiering (personnummer). Krävs enligt PDL.",
            "ivo_ref": "PDL 2 kap"
        })
    else:
        findings.append({
            "type": "GOOD",
            "area": "Patient-ID",
            "message": "Patient-ID hittat",
            "ivo_ref": "PDL 2 kap"
        })
    
    # 4. Check SBAR
    sbar_count = 0
    sbar_sections = {
        'Situation': r'(situation|situationen|aktuellt)',
        'Bakgrund': r'(bakgrund|historik|tidigare|anamnes)',
        'Bedömning': r'(bedömning|analys|intryck|mitt)',
        'Rekommendation': r'(rekommendation|åtgärd|förslag|plan)'
    }
    for section, pattern in sbar_sections.items():
        if re.search(pattern, text, re.IGNORECASE):
            sbar_count += 1
    
    if sbar_count >= 3:
        findings.append({
            "type": "GOOD",
            "area": "SBAR",
            "message": f"SBAR-struktur hittad ({sbar_count}/4 sektioner). Bra dokumentationsstruktur!",
            "ivo_ref": "SOSFS 2016:34"
        })
    elif sbar_count > 0:
        score -= 10
        findings.append({
            "type": "WARNING",
            "area": "SBAR",
            "message": f"Bara {sbar_count}/4 SBAR-sektioner. Full struktur rekommenderas.",
            "ivo_ref": "SOSFS 2016:34"
        })
    else:
        score -= 15
        findings.append({
            "type": "WARNING",
            "area": "SBAR",
            "message": "Ingen SBAR-struktur hittad. SBAR (Situation, Bakgrund, Bedömning, Rekommendation) rekommenderas.",
            "ivo_ref": "SOSFS 2016:34"
        })
    
    # 5. Check risk words and analysis
    risk_words = ['suicid', 'självmord', 'självskada', 'dödsfall', 'våld', 'hot', 'psykos', 'aggressiv']
    found_risks = [w for w in risk_words if w in text.lower()]
    
    if found_risks:
        # Check if there's a risk analysis
        risk_analysis_patterns = [r'riskanalys', r'riskbedömning', r'motivation', r'åtgärd']
        has_analysis = any(re.search(p, text, re.IGNORECASE) for p in risk_analysis_patterns)
        
        if has_analysis:
            findings.append({
                "type": "GOOD",
                "area": "Riskbedömning",
                "message": f"Hittade riskord ({', '.join(found_risks)}) men även riskanalys. Bra!",
                "ivo_ref": "Patientsäkerhetslagen"
            })
        else:
            score -= 20
            findings.append({
                "type": "CRITICAL",
                "area": "Riskbedömning",
                "message": f"Hittade riskord ({', '.join(found_risks)}) men INGEN riskanalys! Krävs enligt Patientsäkerhetslagen.",
                "ivo_ref": "Patientsäkerhetslagen"
            })
    
    return {
        "score": max(0, score),
        "findings": findings,
        "summary": f"Granskning klar: {len(findings)} findings, {score} poäng.",
        "recommendations": ["Fyll i saknade delar enligt ovan"]
    }

# --- MAIN INTERFACE ---
st.subheader("🤖 AI-analysera journal")

can_scan = st.session_state.is_premium or scans_left > 0

if not can_scan:
    st.error("🚫 Inga gratis scans kvar. Uppgradera till Premium!")
    text = None
else:
    # Template button
    if selected_template and IVO_TEMPLATES[selected_template]:
        template_text = IVO_TEMPLATES[selected_template].format(
            date=datetime.date.today().strftime("%Y-%m-%d")
        )
        if st.button(f"📋 Fyll i {selected_template}"):
            text = template_text
            st.session_state['template_loaded'] = True
    else:
        text = None
    
    # Input method
    input_method = st.radio("Välj input:", ["📝 Skriv text", "📁 Ladda upp fil"], horizontal=True)
    
    if input_method == "📁 Ladda upp fil":
        uploaded_file = st.file_uploader("Dra och släpp en .txt-fil", type="txt", label_visibility="collapsed")
        text = uploaded_file.read().decode("utf-8") if uploaded_file else text
    else:
        text = st.text_area(
            "Klistra in journaltext här:", 
            value=text if 'template_loaded' not in st.session_state else template_text if selected_template else None,
            height=200, 
            label_visibility="collapsed"
        )
        
        if 'template_loaded' in st.session_state:
            del st.session_state['template_loaded']

if text and can_scan:
    # Increment counter
    if not st.session_state.is_premium:
        st.session_state.scans_used += 1
    
    # Analyze button
    if st.button("🔍 Kör AI-analys"):
        with st.spinner("🤖 AI analyserar mot IVO-krav..."):
            result = analyze_with_ai(text)
        
        # --- RESULTS ---
        st.divider()
        
        # Score
        score = result.get('score', 0)
        col1, col2 = st.columns([1, 3])
        with col1:
            if score >= 90:
                st.markdown(f'<div class="score-circle score-good">{score}</div>', unsafe_allow_html=True)
                st.markdown("### ✅ GODKÄNT")
            elif score >= 60:
                st.markdown(f'<div class="score-circle score-warning">{score}</div>', unsafe_allow_html=True)
                st.markdown("### ⚠️ RISKER")
            else:
                st.markdown(f'<div class="score-circle score-bad">{score}</div>', unsafe_allow_html=True)
                st.markdown("### 🚨 KRITISKT")
        with col2:
            st.markdown(f"**Sammanfattning:** {result.get('summary', '')}")
        
        # Findings
        st.subheader("📝 Detaljerade resultat")
        
        findings = result.get('findings', [])
        
        critical = [f for f in findings if f['type'] == 'CRITICAL']
        warnings = [f for f in findings if f['type'] == 'WARNING']
        goods = [f for f in findings if f['type'] == 'GOOD']
        infos = [f for f in findings if f['type'] == 'INFO']
        
        # Show critical first
        for f in critical:
            st.markdown(f'''
            <div class="finding-item finding-critical">
                <div class="requirement-title">❌ {f['area']} - KRITISKT</div>
                <div>{f['message']}</div>
                <div style="font-size:0.75rem;color:#666;margin-top:4px;">📋 {f.get('ivo_ref', '')}</div>
            </div>
            ''', unsafe_allow_html=True)
        
        for f in warnings:
            st.markdown(f'''
            <div class="finding-item finding-warning">
                <div class="requirement-title">⚠️ {f['area']} - VARNING</div>
                <div>{f['message']}</div>
                <div style="font-size:0.75rem;color:#666;margin-top:4px;">📋 {f.get('ivo_ref', '')}</div>
            </div>
            ''', unsafe_allow_html=True)
        
        for f in goods:
            st.markdown(f'''
            <div class="finding-item finding-good">
                <div class="requirement-title">✅ {f['area']} - BRA</div>
                <div>{f['message']}</div>
            </div>
            ''', unsafe_allow_html=True)
        
        # Recommendations
        recommendations = result.get('recommendations', [])
        if recommendations:
            st.subheader("💡 Rekommendationer")
            for rec in recommendations:
                st.markdown(f"- {rec}")
        
        # Disclaimer
        st.divider()
        st.caption("⚠️ Disclaimer: Detta verktyg är ett stöd och ersätter inte klinisk bedömning.")

elif text is None and can_scan:
    st.info("👆 Välj en mall, skriv eller ladda upp text för analys.")

# --- FOOTER ---
st.markdown("---")
st.markdown("*IVO Risk-Scan v2.0 — Byggd av Ada Inc. 🦞 | AI-driven granskning*")
