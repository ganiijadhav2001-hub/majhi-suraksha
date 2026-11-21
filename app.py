import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import json

# --- पेज कॉन्फिगरेशन ---
st.set_page_config(
    page_title="माझी सुरक्षा AI | Garware Hi-Tech Films",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- प्रिमियम कस्टम CSS (Modern Corporate UI) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Noto+Sans+Devanagari:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', 'Noto Sans Devanagari', sans-serif;
    }

    /* Streamlit चे डिफॉल्ट हेडर आणि फुटर लपवणे (App सारख्या लूकसाठी) */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* मुख्य ब्यानर कार्ड */
    .hero-banner {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 60%, #b91c1c 100%);
        padding: 24px 20px;
        border-radius: 16px;
        color: white;
        box-shadow: 0 10px 25px -5px rgba(30, 58, 138, 0.4);
        margin-bottom: 20px;
        border: 1px solid rgba(255,255,255,0.12);
    }
    .hero-badge {
        display: inline-block;
        background: #facc15;
        color: #0f172a;
        font-weight: 700;
        font-size: 12px;
        padding: 4px 10px;
        border-radius: 20px;
        margin-bottom: 8px;
        letter-spacing: 0.5px;
    }
    .hero-title {
        font-size: 26px;
        font-weight: 700;
        margin: 0;
        line-height: 1.2;
    }
    .hero-sub {
        font-size: 14px;
        color: #e2e8f0;
        margin-top: 8px;
        margin-bottom: 0;
    }

    /* रिपोर्ट कार्ड्स */
    .report-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 14px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    .card-label {
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: #94a3b8;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .card-value {
        font-size: 15px;
        color: #f8fafc;
        line-height: 1.5;
    }
    .marathi-box {
        background: rgba(56, 189, 248, 0.08);
        border-left: 4px solid #38bdf8;
        padding: 12px 14px;
        border-radius: 8px;
        margin-top: 10px;
        color: #e0f2fe;
        font-size: 14px;
    }

    /* प्रिमियम बटण */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #dc2626 0%, #ea580c 100%);
        color: white;
        font-weight: 700;
        border: none;
        padding: 14px 20px;
        border-radius: 12px;
        font-size: 16px;
        box-shadow: 0 6px 20px rgba(220, 38, 38, 0.35);
        transition: all 0.2s ease;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(220, 38, 38, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# --- प्रिमियम हेडर ब्यानर ---
st.markdown("""
<div class="hero-banner">
    <span class="hero-badge">🛡️ GARWARE HI-TECH FILMS • माझी सुरक्षा AI</span>
    <h1 class="hero-title">Smart Safety Observation Assistant</h1>
    <p class="hero-sub">फोटो अपलोड करा • ३ सेकंदात AI रिपोर्ट मिळवा • एका क्लिकवर पोर्टल ऑटो-फिल करा</p>
</div>
""", unsafe_allow_html=True)

# --- API Key सेटअप ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = st.text_input("🔑 Gemini API Key टाका:", type="password")

PORTAL_URL = "https://mazisuraksha.garwarehitechfilms.com/"

# --- १. युजरची माहिती विभाग ---
with st.expander("👤 तुमची माहिती (पोर्टलवर Auto-Fill होण्यासाठी)", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        origin_type = st.selectbox("1. Originated From:", ["Employee", "Contract", "Visitor", "Trainee"])
        user_name = st.text_input("2. तुमचे पूर्ण नाव:", placeholder="उदा. Ganesh Jadhav")
    with col2:
        plant_area = st.text_input("5. Plant / Area:", placeholder="उदा. Waluj / BOPET / CPP")
        user_mobile = st.text_input("3. मोबाईल नंबर:", placeholder="उदा. 9876543210")
    
    exact_loc = st.text_input("6. नेमके ठिकाण (Exact Location / Sub area):", placeholder="उदा. Line 2, Winding Section, Pillar No. 14")

# --- २. फोटो अपलोड विभाग ---
st.markdown("### 📸 साईटचा फोटो अपलोड करा")
uploaded_file = st.file_uploader("कॅमेऱ्याने फोटो काढा किंवा गॅलरीतून निवडा", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="अपलोड केलेला साईट फोटो", use_container_width=True)

    if st.button("⚡ AI विश्लेषण करा आणि Auto-Fill तयार करा", use_container_width=True):
        if not api_key:
            st.error("कृपया आधी Gemini API Key सेट करा!")
        else:
            with st.spinner("🚀 AI फोटोतील सुरक्षा बारकावे तपासत आहे..."):
                try:
                    # सुपरफास्ट स्पीडसाठी फोटो कॉम्प्रेस करणे
                    fast_img = image.copy()
                    fast_img.thumbnail((650, 650))

                    client = genai.Client(api_key=api_key)
                    
                    prompt = """
                    You are a Senior Industrial Safety Officer at Garware Hi-Tech Films.
                    Analyze this workplace photo carefully and identify any safety hazard, unsafe act, or improvement opportunity.

                    1. Classify strictly into ONE exact category from this list:
                       - Unsafe Act
                       - Unsafe Condition
                       - Near Miss
                       - Unsafe Practice
                       - Unsafe Environmental Factor
                       - Safety improvement

                    2. Determine Risk Level: "High", "Medium", or "Low".
                    3. Write a crisp, professional 'description_en' (2-3 lines max) in English for the safety portal.
                    4. Write an actionable 'recommendation_en' (2-3 lines max) in English.
                    5. Provide clear, easy-to-understand Marathi translations: 'description_mr' and 'recommendation_mr'.

                    Return ONLY valid JSON:
                    {
                        "type": "...",
                        "risk": "...",
                        "description_en": "...",
                        "recommendation_en": "...",
                        "description_mr": "...",
                        "recommendation_mr": "..."
                    }
                    """

                    # मॉडेल फॉल-बॅक सिस्टम (कधीच एरर येणार नाही)
                    models_to_try = ['gemini-3.8-flash', 'gemini-3.1-flash', 'gemini-2.5-flash']
                    response = None
                    for m in models_to_try:
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
                        except Exception:
                            continue

                    if not response:
                        raise Exception("AI सर्व्हरशी संपर्क होऊ शकला नाही, कृपया पुन्हा प्रयत्न करा.")

                    st.session_state['report'] = json.loads(response.text)

                except Exception as e:
                    st.error(f"त्रुटी आली: {e}")

# --- ३. निकाल आणि एडिटेबल रिपोर्ट ---
if 'report' in st.session_state:
    res = st.session_state['report']
    
    # रिस्क बॅज कलर
    risk_val = res.get('risk', 'Medium')
    risk_color = "#ef4444" if "High" in risk_val else ("#f59e0b" if "Medium" in risk_val else "#10b981")

    st.markdown(f"""
    <div class="report-card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
            <span style="background:#3b82f6; color:white; padding:4px 12px; border-radius:20px; font-size:13px; font-weight:700;">
                📌 {res['type']}
            </span>
            <span style="background:{risk_color}; color:white; padding:4px 12px; border-radius:20px; font-size:12px; font-weight:700;">
                ⚠️ {risk_val} Risk
            </span>
        </div>
        <div class="marathi-box">
            <b>🇮🇳 मराठी सारांश:</b><br>
            • <b>काय चूक आहे:</b> {res['description_mr']}<br>
            • <b>काय दुरुस्त करावे:</b> {res['recommendation_mr']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### ✏️ पोर्टलसाठी इंग्रजी मजकूर (हवे असल्यास बदल करू शकता)")
    final_type = st.selectbox(
        "4. Type of observation:",
        ["Unsafe Act", "Unsafe Condition", "Near Miss", "Unsafe Practice", "Unsafe Environmental Factor", "Safety improvement"],
        index=["Unsafe Act", "Unsafe Condition", "Near Miss", "Unsafe Practice", "Unsafe Environmental Factor", "Safety improvement"].index(res["type"]) if res["type"] in ["Unsafe Act", "Unsafe Condition", "Near Miss", "Unsafe Practice", "Unsafe Environmental Factor", "Safety improvement"] else 1
    )
    final_desc = st.text_area("7. Short Description of observation:", value=res["description_en"], height=90)
    final_rec = st.text_area("8. Recommendation:", value=res["recommendation_en"], height=90)

    st.divider()

    # --- ४. स्मार्ट AUTO-FILL कोड जनरेटर ---
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
        function setVal(el, val){{
            if(el && val){{
                el.value = val;
                el.dispatchEvent(new Event('input', {{bubbles:true}}));
                el.dispatchEvent(new Event('change', {{bubbles:true}}));
            }}
        }}
        function selectOpt(sel, txt){{
            if(!sel || !txt) return;
            for(let opt of sel.options){{
                if(opt.text.toLowerCase().includes(txt.toLowerCase())){{
                    sel.value = opt.value;
                    sel.dispatchEvent(new Event('change', {{bubbles:true}}));
                    break;
                }}
            }}
        }}
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

        alert('✅ माझी सुरक्षा फॉर्म यशस्वीरित्या ऑटो-फिल झाला आहे! आता फक्त फोटो निवडा आणि CAPTCHA टाका.');
    }})();"""

    one_line_js = " ".join(js_code.split())

    st.info("👇 **पायरी १:** खालील बॉक्सच्या उजव्या कोपऱ्यातील **Copy** चिन्हावर क्लिक करा:")
    st.code(one_line_js, language="javascript")

    st.link_button("🌐 पायरी २: 'माझी सुरक्षा' पोर्टल उघडा (Open Website)", PORTAL_URL, type="primary", use_container_width=True)

    with st.expander("ℹ️ ऑटो-फिल कसे वापरायचे? (फक्त १० सेकंद)"):
        st.markdown("""
        1. वरचा कोड **Copy** करा आणि निळे बटण दाबून **माझी सुरक्षा** वेबसाईट उघडा.
        2. वेबसाईट उघडल्यावर Chrome च्या सर्वात वरच्या **URL / Address Bar** वर क्लिक करा.
        3. तिथे कॉपी केलेला कोड **Paste** करा आणि कीबोर्डवर **Enter / Go** दाबा. *(टीप: पेस्ट केल्यावर जर सुरुवातीला `javascript:` नसेल तर ते हाताने टाईप करा).*
        4. तुमचा संपूर्ण फॉर्म आपोआप भरला जाईल! फक्त फोटो जोडा, CAPTCHA सोडवा आणि **Submit** करा.
        """)
