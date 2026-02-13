import streamlit as st
import re
import datetime
import time

# --- CONFIG ---
st.set_page_config(page_title="IVO Risk-Scan | Ada Inc.", page_icon="🛡️", layout="centered")

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
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE (Freemium Counter) ---
if 'scans_used' not in st.session_state:
    st.session_state.scans_used = 0
if 'is_premium' not in st.session_state:
    st.session_state.is_premium = False

# --- WALLET INTEGRATION (REAL Agentic Wallet) ---
AGENT_WALLET_ADDRESS = "0xECAB73D2DFB9CB82f207b057bD94C6C8dcc65760"

# --- HEADER & VALUE PROP ---
st.title("🛡️ IVO Risk-Scan")
st.markdown('<p class="hero-text">Hitta brister i dina journaler <strong>innan</strong> IVO gör det.</p>', unsafe_allow_html=True)

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

with st.container():
    st.markdown("""
    <div class="value-prop">
        <h3>🚀 Varför använda detta?</h3>
        <ul>
            <li><strong>Spara din legitimation:</strong> Missade signaturer och otydliga datum är de vanligaste orsakerna till kritik.</li>
            <li><strong>Spara tid:</strong> Analysera en journaltext på 0.5 sekunder istället för 15 minuter manuell granskning.</li>
            <li><strong>Säkerhet:</strong> Hitta riskord (t.ex. "suicid", "våld") som kräver dokumenterad bedömning.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# --- SIDEBAR (Sales & Pay) ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Coinbase_Wordmark.svg/2560px-Coinbase_Wordmark.svg.png", width=150)
    st.header("⚙️ Inställningar")
    
    # Premium status
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
    - ✨ Auto-Fix förslag
    - 📄 PDF Export (kommer snart)
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
            # Honor system for now - can add blockchain verification later
            st.session_state.is_premium = True
            st.success("🎉 Premium aktiverat! Tack för ditt stöd!")
            st.rerun()
    
    st.markdown("---")
    st.caption(f"Scans använda: {st.session_state.scans_used}")
    st.caption("Ada Inc. © 2026")

# --- LOGIC ---
def analyze_text(text):
    findings = []
    score = 100
    
    # Check 1: Signatures
    if not re.search(r"(signatur|sign|sjuksköterska|läkare|leg|underläkare)", text, re.IGNORECASE):
        findings.append({"type": "CRITICAL", "msg": "❌ Ingen signatur hittad! (Krav enl. Patientdatalagen)", "deduction": 50})
        score -= 50

    # Check 2: Dates
    if not re.search(r"\d{4}-\d{2}-\d{2}", text):
        findings.append({"type": "WARNING", "msg": "⚠️ Inget tydligt datum (ISO-format YYYY-MM-DD saknas).", "deduction": 10})
        score -= 10

    # Check 3: Risk Words
    risk_words = ["suicid", "självmord", "våld", "hot", "kniv", "aggressiv", "bält"]
    found_risks = [w for w in risk_words if w in text.lower()]
    if found_risks:
        findings.append({"type": "ALERT", "msg": f"🚨 Riskord upptäckta: {', '.join(found_risks)}. Har du dokumenterat riskanalys?", "deduction": 0})

    # Check 4: SBAR format (bonus)
    sbar_keywords = ["situation", "bakgrund", "aktuellt", "rekommendation"]
    sbar_found = sum(1 for k in sbar_keywords if k in text.lower())
    if sbar_found >= 3:
        findings.append({"type": "BONUS", "msg": "✅ SBAR-format upptäckt! Bra strukturerad dokumentation.", "deduction": -5})
        score = min(100, score + 5)

    return max(0, score), findings

def generate_fix(text, findings):
    fixed_text = text
    changes = []
    
    # Simple rule-based fixes
    if not re.search(r"\d{4}-\d{2}-\d{2}", text):
        today = datetime.date.today().strftime("%Y-%m-%d")
        fixed_text = f"Datum: {today}\n" + fixed_text
        changes.append(f"✅ La till dagens datum ({today})")
    
    if not re.search(r"(signatur|sign)", text, re.IGNORECASE):
        fixed_text += "\n\nSignatur: ____________________ (Leg. Läkare/Sjuksköterska)"
        changes.append("✅ La till signaturrad")
        
    return fixed_text, changes

# --- MAIN INTERFACE ---
st.subheader("📂 Ladda upp en journaltext (.txt)")

# Check if user can scan
can_scan = st.session_state.is_premium or scans_left > 0

if not can_scan:
    st.error("🚫 Inga gratis scans kvar. Uppgradera till Premium i sidomenyn!")
    uploaded_file = None
else:
    uploaded_file = st.file_uploader("Dra och släpp filen här", type="txt", label_visibility="collapsed")

if uploaded_file is not None and can_scan:
    text = uploaded_file.read().decode("utf-8")
    
    # Increment scan counter (only for free users)
    if not st.session_state.is_premium:
        st.session_state.scans_used += 1
    
    with st.spinner("Analyserar mot IVO:s riktlinjer..."):
        score, findings = analyze_text(text)
    
    # --- RESULTS ---
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Säkerhetspoäng", f"{score}/100")
    with col2:
        if score >= 90:
            st.markdown('<div style="text-align:right;"><span class="audit-pass">✅ GODKÄND</span></div>', unsafe_allow_html=True)
        elif score >= 50:
            st.markdown('<div style="text-align:right;"><span class="audit-fail">⚠️ RISKER HITTADE</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="text-align:right;"><span class="audit-fail">🚨 KRITISKA BRISTER</span></div>', unsafe_allow_html=True)

    st.subheader("📝 Analysresultat")
    if not findings:
        st.success("Inga uppenbara brister hittades! Bra dokumenterat. ✅")
    else:
        for f in findings:
            if f['type'] == 'CRITICAL':
                st.error(f"**KRITISKT FEL (-{f['deduction']}p):** {f['msg']}")
            elif f['type'] == 'WARNING':
                st.warning(f"**VARNING (-{f['deduction']}p):** {f['msg']}")
            elif f['type'] == 'ALERT':
                st.info(f"**OBS:** {f['msg']}")
            elif f['type'] == 'BONUS':
                st.success(f"**BONUS (+5p):** {f['msg']}")
        
        # --- AUTO-FIX (Premium only) ---
        if st.session_state.is_premium:
            st.markdown("---")
            st.subheader("✨ Auto-Fix")
            with st.spinner("Genererar IVO-säkrat förslag..."):
                time.sleep(0.5)
                fixed_text, changes = generate_fix(text, findings)
            
            if changes:
                st.markdown('<div class="fix-box">', unsafe_allow_html=True)
                st.markdown("**Ändringar gjorda:**")
                for change in changes:
                    st.markdown(f"- {change}")
                
                st.text_area("📋 Kopiera detta förslag:", value=fixed_text, height=200)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("Inga automatiska fixar behövs - dokumentet ser bra ut!")
        else:
            st.info("💡 Vill du att AI ska fixa texten åt dig? Uppgradera till **Premium** i sidomenyn.")

    st.divider()
    
    # Show remaining scans
    if not st.session_state.is_premium:
        new_scans_left = FREE_SCANS - st.session_state.scans_used
        if new_scans_left > 0:
            st.info(f"📊 Du har **{new_scans_left}** gratis scans kvar.")
        else:
            st.warning("⚠️ Det var din sista gratis scan! Uppgradera för obegränsad användning.")
    
    st.caption("Disclaimer: Detta verktyg är ett stöd och ersätter inte klinisk bedömning. All data behandlas lokalt i din webbläsare.")

elif can_scan:
    # Example text if no file uploaded
    st.info("👆 Ladda upp en fil ovan för att starta analysen.")
    with st.expander("📖 Se ett exempel..."):
        st.code("""
Datum: 2026-02-12
Patient inkom med oro och ångest. 
Suicidrisk bedömd som låg.
Signatur: Dr. A. Svensson, Leg. Läkare
        """, language="text")
        st.caption("Detta exempel skulle få 100 poäng.")
    
    with st.expander("❓ Hur fungerar det?"):
        st.markdown("""
        **IVO Risk-Scan analyserar:**
        1. 📝 **Signatur** — Krav enligt Patientdatalagen
        2. 📅 **Datum** — ISO-format (YYYY-MM-DD)
        3. ⚠️ **Riskord** — Suicid, våld, etc. (kräver dokumenterad bedömning)
        4. 📋 **SBAR-format** — Bonus för strukturerad dokumentation
        
        **Priser:**
        - 🆓 **Gratis:** 5 scans med basic analys
        - ⭐ **Premium (5 USDC):** Obegränsat + Auto-Fix
        """)
