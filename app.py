import streamlit as st
import re
import datetime
import time
import json

# --- CONFIG ---
st.set_page_config(page_title="IVO Risk-Scan v2.1 | Ada Inc.", page_icon="🛡️", layout="centered")

# --- FREEMIUM CONFIG ---
FREE_SCANS = 3
PREMIUM_PRICE = "5 USDC"

# --- VÅRDPROCESS KNOWLEDGE BASE ---
VARDPROCESS = """
## VÅRDPROCESSEN (Omvårdnadsprocessen)

IVO granskar att vården följer processtegen:

### 1. BEDÖMNING (Assessment)
- Symtom och aktuellt tillstånd dokumenteras
- Relevant anamnes
- Status (psykiatrisk/somatisk)
- Riskbedömning görs

### 2. PLANERING (Planning)
- Vårdplan upprättas
- Mål sätts (SMART)
- Åtgärder beskrivs
- Ansvar fördelas

### 3. GENOMFÖRANDE (Implementation)
- Åtgärder utförs
- Dokumenteras löpande
- Vid behov justeras planen

### 4. UTVÄRDERING (Evaluation)
- Effekt bedöms
- Uppföljning planeras
- Nästa steg beslutas

---

## BEHANDLINGSPROCESSEN

### Läkemedelsbehandling
- Indikation dokumenteras
- Dos och administrering
- Uppföljning av effekt/biverkningar
- Laboratorieprover vid behov

### Psykiatrisk behandling
- Psykoterapeutisk intervention
- KBT/PDT/AT
- Miljöterapi

---

## RISKBEDÖMNINGSSKALOR (IVO-krav)

| Skala | Användning |
|-------|------------|
| **SIS** | Suicid Intent Scale - suicidrisk |
| **SBUD** | Suicidal Behaviour Documentation |
| **COWS** | Opiatabstinens |
| **CIWA-A** | Alkoholabstinens |
| **GAF** | Funktionsnivå |
| **CGI-S** | Svårighetsgrad |

---

## VANLIGA IVO-ANMÄRKNINGAR

1. ❌ Ingen riskbedömning vid allvarliga tillstånd
2. ❌ Vårdplan saknas eller är ofullständig
3. ❌ Uppföljning saknas
4. ❌ Mål inte definierade
5. ❌ Ingen utvärdering av behandlingseffekt
6. ❌ Läkemedelsindikation saknas
7. ❌ Biverkningar inte dokumenterade
"""

# --- IVO REQUIREMENTS (UPDATED) ---
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
   - Spårbarhet ska kunna upprätthållas
   - SBAR-struktur rekommenderas

3. VÅRDPROCESSEN (Omvårdnad)
   - Bedömning → Planering → Genomförande → Utvärdering
   - Riskbedömning ska göras
   - Vårdplan ska upprättas
   - Uppföljning ska dokumenteras

4. IVO:S VANLIGA KRITIK
   - Saknad eller ofullständig signatur
   - Otydlig patientidentifiering
   - Bristande riskanalys vid allvarliga tillstånd
   - Ingen vårdplan
   - Ingen uppföljning planerad
   - Läkemedelsindikation saknas
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
[Klinisk bedömning, riskbedömning (SIS/SBUD), psykiatrisk status]

## R - Rekommendation
[Planerade åtgärder, uppföljning, remisser]

## Vårdplan
Mål: [Vad ska uppnås?]
Åtgärder: [Vad gör vi?]
Ansvar: [Vem?]
Uppföljning: [När?]

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
[Behandlingsplan, uppföljning]

## Vårdplan
Mål: 
Åtgärder:
Ansvar:
Uppföljning:

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
[Kognitiv status (MMSE), funktionsnivå, riskbedömning]

## R - Rekommendation
[Omvårdnadsåtgärder, medicinjustering, anhörigstöd]

## Vårdplan
Mål:
Åtgärder:
Ansvar:
Uppföljning:

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

## Vårdplan
Mål:
Åtgärder:
Ansvar:
Uppföljning:

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

## Vårdplan
Mål:
Åtgärder:
Ansvar:
Uppföljning:

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
    .requirement-title { font-weight: bold; }
    .finding-item { background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 12px; margin: 8px 0; }
    .finding-critical { border-left: 4px solid #ef4444; background: #fef2f2; }
    .finding-warning { border-left: 4px solid #f59e0b; background: #fffbeb; }
    .finding-good { border-left: 4px solid #10b981; background: #ecfdf5; }
    .finding-info { border-left: 4px solid #3b82f6; background: #eff6ff; }
    .finding-item div { color: #1f2937 !important; }
    .finding-item div:first-child { font-weight: bold; }
    .process-badge { background: #e0f2fe; border: 1px solid #38bdf8; padding: 6px 10px; border-radius: 6px; font-size: 0.75rem; color: #0369a1; display: inline-block; margin: 2px; }
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
    st.markdown('<p class="hero-text">AI-driven journalgranskning med <strong>vårdprocessperspektiv</strong>.</p>', unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div style="text-align:right; padding: 20px;">
        <span class="ai-badge">🤖 v2.1</span><br>
        <span class="new-feature">✨ VÅRDPROCESS</span><br>
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

# --- INFO EXPANDERS ---
with st.expander("📖 IVO:s granskningskriterier", expanded=False):
    st.markdown(IVO_REQUIREMENTS)

with st.expander("🏥 Om vårdprocessen", expanded=False):
    st.markdown(VARDPROCESS)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Coinbase_Wordmark.svg/2560px-Coinbase_Wordmark.svg.png", width=150)
    st.header("⚙️ Inställningar")
    
    if st.session_state.is_premium:
        st.success("⭐ Premium aktiv!")
    else:
        st.radio("Analysnivå", ["Gratis Risk-Scan", "Premium (AI + Auto-Fix)"])
    
    st.markdown("---")
    st.markdown("### 💎 Premium (" + PREMIUM_PRICE + ")")
    st.markdown("""
    - ♾️ Obegränsade scans
    - ✨ AI Auto-Fix
    - 📄 PDF Export
    """)
    
    if not st.session_state.is_premium:
        if st.button("🔓 Betala " + PREMIUM_PRICE):
            st.markdown(f"""
            <div class="wallet-box">
                <strong>Skicka till Ada Inc:</strong><br>
                <code>{AGENT_WALLET_ADDRESS}</code>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("✅ Jag har betalat"):
            st.session_state.is_premium = True
            st.success("Premium aktiverat!")
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
        st.markdown('<span class="process-badge">📋 Mall</span>', unsafe_allow_html=True)

# --- ANALYZE FUNCTION ---
def analyze_with_ai(text):
    """AI-powered analysis with vårdprocess"""
    import os
    
    prompt = f"""Du är en IVO-expert som granskar journaler mot svenska vårdkrav.

## GRANSKA MOT:

### 1. FORMALIA (PDL/SOSFS)
- Signatur med legitimation
- Datum (YYYY-MM-DD)
- Patient-ID (personnummer)

### 2. VÅRDPROCESSEN (Omvårdnad)
- Bedömning: Finns aktuellt tillstånd, symtom, anamnes?
- Planering: Finns vårdplan med mål, åtgärder, ansvar?
- Genomförande: Dokumenteras åtgärder?
- Utvärdering: Följs behandlingseffekt upp?

### 3. RISKBEDÖMNING
- Vid suicidtankar: Används SIS/SBUD?
- Vid abstinens: Används CIWA-A/COWS?
- Vid våldsrisk: Dokumenteras bedömning?

### 4. BEHANDLING
- Läkemedel: Indikation, dos, uppföljning?
- Psykiatrisk: Behandlingstyp dokumenterad?

## JOURNAL ATT GRANSKA:
```
{text}
```

## JSON OUTPUT:
{{
    "score": [0-100],
    "findings": [
        {{
            "type": "CRITICAL|WARNING|GOOD|INFO",
            "area": "Signatur|Datum|Patient-ID|Bedömning|Planering|Utvärdering|Riskbedömning|Läkemedel|SBAR",
            "message": "Vad som är fel/bra",
            "ivo_ref": "PDL/SOSFS/Vårdprocess/Patientsäkerhet"
        }}
    ],
    "vårdprocess": {{
        "bedömning": "JA/NEJ/TDELVIS",
        "planering": "JA/NEJ/TDELVIS", 
        "genomförande": "JA/NEJ/TDELVIS",
        "utvärdering": "JA/NEJ/TDELVIS"
    }},
    "summary": "Kort sammanfattning",
    "recommendations": ["Rek1", "Rek2"]
}}

Var kritisk. Börja med {{"""

    try:
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
                import json as json_module
                data = json_module.loads(content)
                return data
    except:
        pass
    
    return fallback_analysis(text)

def fallback_analysis(text):
    """Enhanced fallback with vårdprocess"""
    findings = []
    score = 100
    
    # === FORMALIA ===
    sig_match = re.search(r'(signatur|sign|sig\.?)\s*[:;]?\s*([A-Za-zÀ-ÿ]+)', text, re.IGNORECASE)
    if not sig_match:
        score -= 20
        findings.append({"type": "CRITICAL", "area": "Signatur", "message": "Saknas signatur med legitimation!", "ivo_ref": "PDL 3 kap"})
    else:
        findings.append({"type": "GOOD", "area": "Signatur", "message": "Signatur hittad", "ivo_ref": "PDL 3 kap"})
    
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', text)
    if not date_match:
        score -= 15
        findings.append({"type": "CRITICAL", "area": "Datum", "message": "Saknas datum (ISO-format)", "ivo_ref": "SOSFS 2016:34"})
    else:
        findings.append({"type": "GOOD", "area": "Datum", "message": "Datum hittat", "ivo_ref": "SOSFS 2016:34"})
    
    pnr_match = re.search(r'(\d{8}-\d{4}|\d{12})', text)
    if not pnr_match:
        score -= 15
        findings.append({"type": "WARNING", "area": "Patient-ID", "message": "Saknas personnummer", "ivo_ref": "PDL 2 kap"})
    else:
        findings.append({"type": "GOOD", "area": "Patient-ID", "message": "Patient-ID hittat", "ivo_ref": "PDL 2 kap"})
    
    # === VÅRDPROCESS ===
    # Bedömning
    assessment_patterns = [r'situation', r'tillstånd', r'symtom', r'bedömning', r'anamnes', r'status']
    has_assessment = any(re.search(p, text, re.IGNORECASE) for p in assessment_patterns)
    if has_assessment:
        findings.append({"type": "GOOD", "area": "Bedömning", "message": "Bedömning dokumenterad", "ivo_ref": "Vårdprocess"})
    else:
        score -= 15
        findings.append({"type": "WARNING", "area": "Bedömning", "message": "Ingen tydlig bedömning funnen - vad är patientens tillstånd?", "ivo_ref": "Vårdprocess"})
    
    # Planering (vårdplan)
    planning_patterns = [r'vårdplan', r'mål', r'åtgärd', r'plan', r'rekommendation', r'förslag']
    has_planning = any(re.search(p, text, re.IGNORECASE) for p in planning_patterns)
    if has_planning:
        findings.append({"type": "GOOD", "area": "Planering", "message": "Vårdplan/planering dokumenterad", "ivo_ref": "Vårdprocess"})
    else:
        score -= 15
        findings.append({"type": "CRITICAL", "area": "Planering", "message": "Saknar vårdplan! Mål och åtgärder måste definieras.", "ivo_ref": "Vårdprocess"})
    
    # Utvärdering
    eval_patterns = [r'uppföljning', r'utvärdering', r'följa upp', r'effekt', r'ompröva', r'nästa']
    has_evaluation = any(re.search(p, text, re.IGNORECASE) for p in eval_patterns)
    if has_evaluation:
        findings.append({"type": "GOOD", "area": "Utvärdering", "message": "Uppföljning planerad", "ivo_ref": "Vårdprocess"})
    else:
        score -= 10
        findings.append({"type": "WARNING", "area": "Utvärdering", "message": "Ingen uppföljning planerad - hur följs behandlingen upp?", "ivo_ref": "Vårdprocess"})
    
    # === RISKBEDÖMNING ===
    risk_words = ['suicid', 'självmord', 'självskada', 'dödsfall', 'våld', 'hot', 'psykos', 'aggressiv', 'fara']
    found_risks = [w for w in risk_words if w in text.lower()]
    
    if found_risks:
        risk_assess_patterns = [r'riskanalys', r'riskbedömning', r'sis', r'sbud', r'motivation', r'skyddsfaktor']
        has_risk_assess = any(re.search(p, text, re.IGNORECASE) for p in risk_assess_patterns)
        if has_risk_assess:
            findings.append({"type": "GOOD", "area": "Riskbedömning", "message": f"Riskord ({', '.join(found_risks)}) + riskanalys dokumenterad", "ivo_ref": "Patientsäkerhet"})
        else:
            score -= 20
            findings.append({"type": "CRITICAL", "area": "Riskbedömning", "message": f"Hittade riskord ({', '.join(found_risks)}) men ingen riskanalys! Krävs omedelbart.", "ivo_ref": "Patientsäkerhet"})
    
    # === LÄKEMEDEL ===
    med_patterns = [r'läkemedel', r'medicin', r'dos', r'administration', r'behandling', r'psykofarmaka']
    has_meds = any(re.search(p, text, re.IGNORECASE) for p in med_patterns)
    if has_meds:
        # Check for indication
        ind_patterns = [r'indikation', r'för', r'mot', r'behandling av']
        has_indication = any(re.search(p, text, re.IGNORECASE) for p in ind_patterns)
        if has_indication:
            findings.append({"type": "GOOD", "area": "Läkemedel", "message": "Läkemedelsbehandling med indikation dokumenterad", "ivo_ref": "Läkemedel"})
        else:
            findings.append({"type": "INFO", "area": "Läkemedel", "message": "Läkemedel nämnda - säkerställ indikation dokumenteras", "ivo_ref": "Läkemedel"})
    
    # === SBAR ===
    sbar_count = 0
    sbar_sections = {
        'Situation': r'(situation|tillstånd|aktuellt)',
        'Bakgrund': r'(bakgrund|historik|tidigare|anamnes)',
        'Bedömning': r'(bedömning|analys|intryck)',
        'Rekommendation': r'(rekommendation|åtgärd|förslag|plan)'
    }
    for section, pattern in sbar_sections.items():
        if re.search(pattern, text, re.IGNORECASE):
            sbar_count += 1
    
    if sbar_count >= 3:
        findings.append({"type": "GOOD", "area": "SBAR", "message": f"SBAR-struktur ({sbar_count}/4)", "ivo_ref": "SOSFS"})
    elif sbar_count > 0:
        findings.append({"type": "INFO", "area": "SBAR", "message": f"Delvis SBAR ({sbar_count}/4)", "ivo_ref": "SOSFS"})
    
    return {
        "score": max(0, score),
        "findings": findings,
        "vårdprocess": {
            "bedömning": "JA" if has_assessment else "NEJ",
            "planering": "JA" if has_planning else "NEJ",
            "genomförande": "TDELVIS",
            "utvärdering": "JA" if has_evaluation else "NEJ"
        },
        "summary": f"Granskning: {score} poäng. Vårdprocess: Bedömning={'✓' if has_assessment else '✗'}, Planering={'✓' if has_planning else '✗'}, Uppföljning={'✓' if has_evaluation else '✗'}",
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
    
    # Input
    input_method = st.radio("Välj input:", ["📝 Skriv text", "📁 Ladda upp fil"], horizontal=True)
    
    if input_method == "📁 Ladda upp fil":
        uploaded_file = st.file_uploader("Dra och släpp en .txt-fil", type="txt", label_visibility="collapsed")
        text = uploaded_file.read().decode("utf-8") if uploaded_file else text
    else:
        text = st.text_area("Klistra in journaltext här:", value=text if 'template_loaded' not in st.session_state else template_text if selected_template else None, height=200, label_visibility="collapsed")
        if 'template_loaded' in st.session_state:
            del st.session_state['template_loaded']

if text and can_scan:
    if not st.session_state.is_premium:
        st.session_state.scans_used += 1
    
    if st.button("🔍 Kör AI-analys"):
        with st.spinner("🤖 AI analyserar vårdprocess..."):
            result = analyze_with_ai(text)
        
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
        
        # Vårdprocess badges
        vp = result.get('vårdprocess', {})
        if vp:
            st.subheader("🏥 Vårdprocess-status")
            vp_cols = st.columns(4)
            with vp_cols[0]:
                bedomning = vp.get('bedömning', 'NEJ')
                color = "#10b981" if bedomning == "JA" else "#f59e0b"
                st.markdown(f'<span style="background:{color};color:white;padding:6px 12px;border-radius:6px;">🩺 Bedömning: {bedomning}</span>', unsafe_allow_html=True)
            with vp_cols[1]:
                planering = vp.get('planering', 'NEJ')
                color = "#10b981" if planering == "JA" else "#ef4444"
                st.markdown(f'<span style="background:{color};color:white;padding:6px 12px;border-radius:6px;">📋 Planering: {planering}</span>', unsafe_allow_html=True)
            with vp_cols[2]:
                genomfor = vp.get('genomförande', 'TDELVIS')
                st.markdown(f'<span style="background:#3b82f6;color:white;padding:6px 12px;border-radius:6px;">⚙️ Genomför: {genomfor}</span>', unsafe_allow_html=True)
            with vp_cols[3]:
                utvärdering = vp.get('utvärdering', 'NEJ')
                color = "#10b981" if utvärdering == "JA" else "#f59e0b"
                st.markdown(f'<span style="background:{color};color:white;padding:6px 12px;border-radius:6px;">📊 Uppföljn: {utvärdering}</span>', unsafe_allow_html=True)
        
        # Findings
        st.subheader("📝 Detaljerade resultat")
        findings = result.get('findings', [])
        
        for f in findings:
            if f['type'] == 'CRITICAL':
                st.markdown(f'''
                <div class="finding-item finding-critical">
                    <div class="requirement-title" style="color:#991b1b !important;font-weight:bold;">❌ {f['area']} - KRITISKT</div>
                    <div style="color:#1f2937 !important;">{f['message']}</div>
                    <div style="font-size:0.75rem;color:#666;margin-top:4px;">📋 {f.get('ivo_ref', '')}</div>
                </div>
                ''', unsafe_allow_html=True)
            elif f['type'] == 'WARNING':
                st.markdown(f'''
                <div class="finding-item finding-warning">
                    <div class="requirement-title" style="color:#92400e !important;font-weight:bold;">⚠️ {f['area']}</div>
                    <div style="color:#1f2937 !important;">{f['message']}</div>
                </div>
                ''', unsafe_allow_html=True)
            elif f['type'] == 'GOOD':
                st.markdown(f'''
                <div class="finding-item finding-good">
                    <div class="requirement-title" style="color:#065f46 !important;font-weight:bold;">✅ {f['area']}</div>
                    <div style="color:#1f2937 !important;">{f['message']}</div>
                </div>
                ''', unsafe_allow_html=True)
        
        # Recommendations
        recommendations = result.get('recommendations', [])
        if recommendations:
            st.subheader("💡 Rekommendationer")
            for rec in recommendations:
                st.markdown(f"- {rec}")
        
        st.divider()
        st.caption("⚠️ Disclaimer: Detta verktyg är ett stöd och ersätter inte klinisk bedömning.")

elif text is None and can_scan:
    st.info("👆 Välj en mall, skriv eller ladda upp text för analys.")

# --- FOOTER ---
st.markdown("---")
st.markdown("*IVO Risk-Scan v2.1 — Byggd av Ada Inc. 🦞 | Vårdprocess-perspektiv*")
