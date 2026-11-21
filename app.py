import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import json

st.set_page_config(
    page_title="माझी सुरक्षा AI | Garware Hi-Tech Films",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Noto+Sans+Devanagari:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', 'Noto Sans Devanagari', sans-serif; }
    #MainMenu, footer, header {visibility: hidden;}
    .hero-banner {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 60%, #b91c1c 100%);
        padding: 24px 20px; border-radius: 16px; color: white;
        box-shadow: 0 10px 25px -5px rgba(30, 58, 138, 0.4);
        margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.12);
    }
    .hero-badge {
        display: inline-block; background: #facc15; color: #0f172a;
        font-weight: 700; font-size: 12px; padding: 4px 10px;
        border-radius: 20px; margin-bottom: 8px;
    }
    .hero-title { font-size: 25px; font-weight: 700; margin: 0; line-height: 1.2; }
    .hero-sub { font-size: 13px; color: #e2e8f0; margin-top: 8px; margin-bottom: 0; }
    .report-card {
        background: #1e293b; border: 1px solid #334155;
        border-radius: 14px; padding: 18px; margin-bottom: 14px;
    }
    .marathi-box {
        background: rgba(56, 189, 248, 0.08); border-left: 4px solid #38bdf8;
        padding: 12px 14px; border-radius: 8px; margin-top: 10px;
        color: #e0f2fe; font-size: 14px;
    }
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #dc2626 0%, #ea580c 100%);
        color: white; font-weight: 700; border: none;
        padding: 14px 20px; border-radius: 12px; font-size: 16px;
        box-shadow: 0 6px 20px rgba(220, 38, 38, 0.35);
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-banner">
    <span class="hero-badge">🛡️ GARWARE HI-TECH FILMS • माझी सुरक्षा AI</span>
    <h1 class="hero-title">Smart Safety Observation Assistant</h1>
    <p class="hero-sub">फोटो अपलोड करा • ३ सेकंदात AI रिपोर्ट मिळवा • एका क्लिकवर पोर्टल ऑटो-फिल करा</p>
</div>
""", unsafe_allow_html=True)

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = st.text_input("🔑 Gemini API Key टाका:", type="password")

PORTAL_URL = "https://mazisuraksha.garwarehitechfilms.com/"

with st.expander("👤 तुमची माहिती (पोर्टलवर Auto-Fill होण्यासाठी)", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        origin_type = st.selectbox("1. Originated From:", ["Employee", "Contract", "Visitor", "Trainee"])
        user_name = st.text_input("2. तुमचे पूर्ण नाव:", placeholder="उदा. Ganesh Jadhav")
    with col2:
        plant_area = st.text_input("5. Plant / Area:", placeholder="उदा. Waluj / BOPET / CPP")
        user_mobile = st.text_input("3. मोबाईल नंबर:", placeholder="उदा. 9876543210")
    exact_loc = st.text_input("6. नेमके ठिकाण (Exact Location / Sub area):", placeholder="उदा. Line 2, Winding Section")

st.markdown("### 📸 साईटचा फोटो अपलोड करा")
uploaded_file = st.file_uploader("फोटो निवडा", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="अपलोड केलेला साईट फोटो", use_container_width=True)

    if st.button("⚡ AI विश्लेषण करा आणि Auto-Fill तयार करा", use_container_width=True):
        if not api_key:
            st.error("कृपया आधी Gemini API Key सेट करा!")
        else:
            with st.spinner("🚀 AI फोटोतील सुरक्षा बारकावे तपासत आहे..."):
                try:
                    fast_img = image.copy()
                    fast_img.thumbnail((650, 650))

                    client = genai.Client(api_key=api_key)
                    prompt = """
                    You are a Senior Industrial Safety Officer at Garware Hi-Tech Films.
                    Analyze this workplace photo and identify any safety hazard, unsafe act, or improvement opportunity.

                    1. Classify strictly into ONE exact category:
                       Unsafe Act, Unsafe Condition, Near Miss, Unsafe Practice, Unsafe Environmental Factor, Safety improvement
                    2. Risk Level: "High", "Medium", or "Low".
                    3. Crisp English 'description_en' (2-3 lines max).
                    4. Actionable English 'recommendation_en' (2-3 lines max).
                    5. Clear Marathi translations: 'description_mr' and 'recommendation_mr'.

                    Return ONLY valid JSON:
                    {"type": "...", "risk": "...", "description_en": "...", "recommendation_en": "...", "description_mr": "...", "recommendation_mr": "..."}
                    """

                    last_err = ""
                    response = None
                    for m in ['gemini-3.8-flash', 'gemini-3.1-flash', 'gemini-2.5-flash']:
                        try:
                            response = client.models.generate_content(
                                model=m,
                                contents=[prompt, fast_img],
                                config=types.GenerateContentConfig(
                                    response_mime_type="application/json",
                                    temperature=0.2
                                )
                            )
                            if response:
                                break
                        except Exception as err:
                            last_err = str(err)
                            continue

                    if not response:
                        raise Exception(last_err)

                    st.session_state['report'] = json.loads(response.text)

                except Exception as e:
                    st.error(f"त्रुटी आली: {e}")

if 'report' in st.session_state:
    res = st.session_state['report']
    risk_val = res.get('risk', 'Medium')
    risk_color = "#ef4444" if "High" in risk_val else ("#f59e0b" if "Medium" in risk_val else "#10b981")

    st.markdown(f"""
    <div class="report-card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
            <span style="background:#3b82f6; color:white; padding:4px 12px; border-radius:20px; font-size:13px; font-weight:700;">📌 {res['type']}</span>
            <span style="background:{risk_color}; color:white; padding:4px 12px; border-radius:20px; font-size:12px; font-weight:700;">⚠️ {risk_val} Risk</span>
        </div>
        <div class="marathi-box">
            <b>🇮🇳 मराठी सारांश:</b><br>
            • <b>काय चूक आहे:</b> {res['description_mr']}<br>
            • <b>काय दुरुस्त करावे:</b> {res['recommendation_mr']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### ✏️ पोर्टलसाठी इंग्रजी मजकूर")
    cats = ["Unsafe Act", "Unsafe Condition", "Near Miss", "Unsafe Practice", "Unsafe Environmental Factor", "Safety improvement"]
    final_type = st.selectbox("4. Type of observation:", cats, index=cats.index(res["type"]) if res["type"] in cats else 1)
    final_desc = st.text_area("7. Short Description of observation:", value=res["description_en"], height=90)
    final_rec = st.text_area("8. Recommendation:", value=res["recommendation_en"], height=90)

    st.divider()
    st.markdown("### ⚡ १-क्लिक पोर्टल Auto-Fill")

    safe_origin = json.dumps(origin_type)
    safe_name = json.dumps(user_name)
    safe_mobile = json.dumps(user_mobile)
    safe_plant = json.dumps(plant_area)
    safe_loc = json.dumps(exact_loc)
    safe_type = json.dumps(final_type)
    safe_desc = json.dumps(final_desc)
    safe_rec = json.dumps(final_rec)

    js_code = f"""javascript:(function(){{
        function setVal(el, val){{ if(el && val){{ el.value = val; el.dispatchEvent(new Event('input', {{bubbles:true}})); el.dispatchEvent(new Event('change', {{bubbles:true}})); }} }}
        function selectOpt(sel, txt){{ if(!sel || !txt) return; for(let opt of sel.options){{ if(opt.text.toLowerCase().includes(txt.toLowerCase())){{ sel.value = opt.value; sel.dispatchEvent(new Event('change', {{bubbles:true}})); break; }} }} }}
        let inputs = document.querySelectorAll('input[type="text"], input[type="tel"], input[type="number"]');
        let textareas = document.querySelectorAll('textarea');
        let selects = document.querySelectorAll('select');
        if(selects[0]) selectOpt(selects[0], {safe_origin});
        if(selects[1]) selectOpt(selects[1], {safe_type});
        if(selects[2]) selectOpt(selects[2], {safe_plant});
        if(inputs[0]) setVal(inputs[0], {safe_name});
        if(inputs[1]) setVal(inputs[1], {safe_mobile});
        if(inputs[2]) setVal(inputs[2], {safe_loc});
        if(textareas[0]) setVal(textareas[0], {safe_desc});
        if(textareas[1]) setVal(textareas[1], {safe_rec});
        alert('✅ माझी सुरक्षा फॉर्म यशस्वीरित्या ऑटो-फिल झाला आहे! आता फोटो निवडा आणि CAPTCHA टाका.');
    }})();"""

    one_line_js = " ".join(js_code.split())
    st.code(one_line_js, language="javascript")
    st.link_button("🌐 'माझी सुरक्षा' पोर्टल उघडा (Open Website)", PORTAL_URL, type="primary", use_container_width=True)
