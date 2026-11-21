import streamlit as st
import google.generativeai as genai
from PIL import Image
import json

st.set_page_config(page_title="माझी सुरक्षा - Auto-Fill AI App", page_icon="🦺", layout="centered")

st.title("🦺 माझी सुरक्षा - AI Auto-Fill App")
st.markdown("फोटो अपलोड करा, AI रिपोर्ट तयार करेल आणि एका क्लिकवर **Garware Safety Portal** ऑटो-फिल करा.")

try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    api_key = st.text_input("तुमची Gemini API Key टाका:", type="password")
    if api_key:
        genai.configure(api_key=api_key)

PORTAL_URL = "https://mazisuraksha.garwarehitechfilms.com/"

with st.expander("👤 तुमची माहिती भरा (पोर्टलवर Auto-Fill होण्यासाठी)", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        user_name = st.text_input("तुमचे पूर्ण नाव (Name of Person):", placeholder="उदा. Ganesh Jadhav")
    with col2:
        user_mobile = st.text_input("मोबाईल नंबर (Mobile Number):", placeholder="उदा. 9876543210")
    
    exact_loc = st.text_input("नेमके ठिकाण (Exact Location / Sub area):", placeholder="उदा. Line 2, Winding Section")

uploaded_file = st.file_uploader("📸 साईटचा फोटो निवडा किंवा कॅमेऱ्याने काढा", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="अपलोड केलेला फोटो", use_container_width=True)

    if st.button("🚀 फोटो तपासा आणि Auto-Fill तयार करा", type="primary", use_container_width=True):
        if not api_key:
            st.error("कृपया आधी Gemini API Key टाका!")
        else:
            with st.spinner("AI फोटोचे विश्लेषण करत आहे..."):
                try:
                    model = genai.GenerativeModel('gemini-3.8-flash')
                    
                    prompt = """
                    You are an expert Industrial Safety Officer. Analyze the uploaded workplace image for safety observations.
                    
                    1. Classify the observation strictly into ONE of the following exact categories:
                       - Unsafe Act
                       - Unsafe Condition
                       - Near Miss
                       - Unsafe Practice
                       - Unsafe Environmental Factor
                       - Safety improvement
                    
                    2. Provide a professional, clear 'Short Description of observation' (what is wrong or observed) in English.
                    3. Provide a practical 'Recommendation' (corrective/preventive action) in English.
                    4. Provide Marathi translations for both.

                    Return ONLY a valid JSON object:
                    {
                        "type": "exact category from list",
                        "description_en": "English short description",
                        "recommendation_en": "English recommendation",
                        "description_mr": "Marathi short description",
                        "recommendation_mr": "Marathi recommendation"
                    }
                    """

                    response = model.generate_content([prompt, image])
                    raw_text = response.text.strip().replace("```json", "").replace("```", "")
                    result = json.loads(raw_text)

                    st.success("✅ रिपोर्ट तयार आहे!")
                    
                    st.subheader("📋 तयार झालेला रिपोर्ट")
                    st.write(f"**Type:** `{result['type']}`")
                    st.info(f"**English Description:** {result['description_en']}\n\n**मराठी:** {result['description_mr']}")
                    st.warning(f"**English Recommendation:** {result['recommendation_en']}\n\n**मराठी:** {result['recommendation_mr']}")

                    st.divider()

                    st.subheader("⚡ ऑटो-फिल (Auto-Fill) कसे कराल?")
                    
                    safe_name = json.dumps(user_name)
                    safe_mobile = json.dumps(user_mobile)
                    safe_loc = json.dumps(exact_loc)
                    safe_type = json.dumps(result["type"])
                    safe_desc = json.dumps(result["description_en"])
                    safe_rec = json.dumps(result["recommendation_en"])

                    js_code = f"""javascript:(function(){{
                        function setVal(el, val){{ if(el){{ el.value = val; el.dispatchEvent(new Event('input', {{bubbles:true}})); el.dispatchEvent(new Event('change', {{bubbles:true}})); }} }}
                        let inputs = document.querySelectorAll('input[type="text"], input[type="tel"], input[type="number"]');
                        let textareas = document.querySelectorAll('textarea');
                        let selects = document.querySelectorAll('select');
                        
                        if(inputs[0]) setVal(inputs[0], {safe_name});
                        if(inputs[1]) setVal(inputs[1], {safe_mobile});
                        if(inputs[2]) setVal(inputs[2], {safe_loc});
                        
                        if(textareas[0]) setVal(textareas[0], {safe_desc});
                        if(textareas[1]) setVal(textareas[1], {safe_rec});
                        
                        selects.forEach(s => {{
                            for(let opt of s.options){{
                                if(opt.text.toLowerCase().includes({safe_type}.toLowerCase())){{
                                    s.value = opt.value;
                                    s.dispatchEvent(new Event('change', {{bubbles:true}}));
                                }}
                            }}
                        }});
                        alert('✅ माझी सुरक्षा फॉर्म ऑटो-फिल झाला आहे! आता फोटो जोडा आणि CAPTCHA टाका.');
                    }})();"""

                    one_line_js = " ".join(js_code.split())

                    st.markdown("**पायरी १:** खालील बॉक्सच्या उजव्या कोपऱ्यातील **Copy** बटणावर क्लिक करा:")
                    st.code(one_line_js, language="javascript")

                    st.markdown("**पायरी २:** खालील बटणावर क्लिक करून कंपनीची वेबसाईट उघडा:")
                    st.link_button("🌐 'माझी सुरक्षा' वेबसाईट उघडा", PORTAL_URL, type="primary", use_container_width=True)

                    st.markdown("""
                    **पायरी ३ (महत्त्वाचे):**
                    1. कंपनीची वेबसाईट उघडल्यावर Chrome च्या सर्वात वरच्या **Address Bar (लिंक जिथे दिसते तिथे)** क्लिक करा.
                    2. तिथे कॉपी केलेला कोड **Paste** करा आणि कीबोर्डवर **Enter / Go** दाबा. *(टीप: पेस्ट केल्यावर जर सुरुवातीचा `javascript:` शब्द निघून गेला असेल तर तो हाताने टाईप करा).*
                    3. तुमचा संपूर्ण फॉर्म आपोआप भरला जाईल! फक्त फोटो निवडा आणि गणित (CAPTCHA) सोडवून **Submit** करा.
                    """)

                except Exception as e:
                    st.error(f"त्रुटी आली: {e}")
                  
