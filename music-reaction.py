import streamlit as st
import google.generativeai as genai
import tempfile
import os

# ១. ការកំណត់ទំព័រ (ប្រើ "centered" ដើម្បីឱ្យត្រូវនឹងទំហំអេក្រង់ទូរស័ព្ទដៃ)
st.set_page_config(page_title="OmniReact AI", page_icon="📱", layout="centered", initial_sidebar_state="collapsed")

# ២. ការប្រើប្រាស់ Session State
if 'ai_response' not in st.session_state:
    st.session_state.ai_response = ""
if 'scene1_prompt' not in st.session_state:
    st.session_state.scene1_prompt = ""
if 'scene2_prompt' not in st.session_state:
    st.session_state.scene2_prompt = ""
if 'char_desc' not in st.session_state:
    st.session_state.char_desc = "A young, stylish Asian person in their 20s, wearing a black oversized hoodie and a silver chain."
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

# ៣. CSS (សម្រួលសម្រាប់ Mobile Device)
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    
    .glowing-box {
        border: 2px solid #d400ff;
        border-radius: 12px;
        padding: 20px 15px;
        text-align: center;
        box-shadow: 0 0 12px rgba(212, 0, 255, 0.3);
        margin-bottom: 20px;
        background-color: #161b22;
    }
    
    .main-title {
        color: white;
        font-size: 26px; /* បន្ថយទំហំអក្សរសម្រាប់អេក្រង់តូច */
        font-weight: 800;
        margin-bottom: 5px;
        font-family: sans-serif;
    }
    
    .sub-title {
        color: #00e5ff;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1px;
    }

    div[data-baseweb="tab-list"] { gap: 5px; }
    div[data-baseweb="tab"] {
        background-color: #1f2937;
        border-radius: 8px;
        padding: 8px 12px;
        border: none;
        color: white;
        font-size: 14px;
    }
    div[data-baseweb="tab"]:focus { outline: none; }
    div[data-testid="stTabs"] [data-baseweb="tab-highlight"] { background-color: transparent; }
</style>
""", unsafe_allow_html=True)

# ៤. របារចំហៀង (Sidebar) សម្រាប់ API Key
with st.sidebar:
    st.markdown("## 🔑 Setup API Key")
    api_input = st.text_input("បញ្ចូល Gemini API Key:", type="password", value=st.session_state.api_key)
    if api_input:
        st.session_state.api_key = api_input
    st.info("ចាំបាច់ត្រូវមាន API Key ដើម្បីវិភាគសំឡេង និង Auto Cast។")
    st.divider()
    st.caption("📱 OmniReact AI - Mobile Version")

# ៥. Header UI
st.markdown("""
<div class="glowing-box">
    <div class="main-title">⚡ OmniReact AI</div>
    <div class="sub-title">VIDEO PROMPT & AUDIO SYNC APP</div>
</div>
""", unsafe_allow_html=True)

# ៦. Tabs សម្រាប់ទូរស័ព្ទ (ដក Tab ទី៣ចេញ)
tab1, tab2 = st.tabs(["🎬 Generate", "👤 Visuals"])

# --- TAB 2: ការកំណត់រូបភាព និងតួអង្គ ---
with tab2:
    st.markdown("### 👤 Character (តួអង្គ)")
    if st.button("🎲 Auto Cast (ស្វែងរកតួអង្គថ្មី)", use_container_width=True):
        if st.session_state.api_key:
            with st.spinner("Casting..."):
                try:
                    genai.configure(api_key=st.session_state.api_key)
                    cast_model = genai.GenerativeModel('models/gemini-3.5-flash')
                    cast_prompt = "Generate a highly detailed, 1-sentence description of a unique, trendy, and stylish person for a cinematic AI video prompt. Specify their age, ethnicity, cinematic streetwear/fashion, and one distinct facial feature or accessory. English only."
                    cast_response = cast_model.generate_content(cast_prompt)
                    st.session_state.char_desc = cast_response.text.strip()
                    st.rerun()
                except Exception as e:
                    st.error(f"បញ្ហា: {e}")
        else:
            st.warning("⚠️ សូមបញ្ចូល API Key ក្នុង Sidebar សិន!")
            
    st.text_area("Character Description:", key="char_desc", height=100)
    st.divider()
    
    st.markdown("### 🏙️ Environment (បរិយាកាស)")
    location = st.selectbox("ទីតាំង (Location):", [
        "Bustling city street / sidewalk", 
        "Professional neon-lit podcast studio", 
        "Inside a modern car at night", 
        "Cozy aesthetic bedroom with LED lights",
        "Underground subway station"
    ])
    camera_style = st.selectbox("ម៉ូតកាមេរ៉ា (Camera Style):", [
        "Handheld documentary camera",
        "Smooth Steadicam tracking shot",
        "Ultra-wide VLOG angle",
        "Low angle hero shot",
        "Dynamic camera with crash zooms"
    ])
    lighting_style = st.selectbox("ពន្លឺ (Lighting):", [
        "Cinematic moody lighting with deep shadows",
        "Neon cyberpunk glow (vibrant pinks and blues)",
        "Golden hour sunlight (warm and cinematic)",
        "High-contrast dramatic studio lighting",
        "Natural overcast daylight (realistic and raw)"
    ])

# --- TAB 1: ផ្នែកចម្បងសម្រាប់ Generate Prompts ---
with tab1:
    st.caption("Upload Video / Audio Track")
    uploaded_file = st.file_uploader("", type=['mp3', 'wav', 'm4a'], help="100MB max")

    if uploaded_file is not None:
        st.audio(uploaded_file, format='audio/mp3')
        st.markdown("⏱️ **កំណត់វគ្គ Drop:**")
        
        c1, c2 = st.columns(2)
        with c1:
            drop_min = st.number_input("នាទី", min_value=0, value=0, step=1)
        with c2:
            drop_sec = st.number_input("វិនាទី", min_value=0, max_value=59, value=30, step=1)
            
        time_string = f"{drop_min}:{drop_sec:02d}"
        
        if st.button("✨ វិភាគ & បង្កើត Prompts", use_container_width=True):
            if not st.session_state.api_key:
                st.error("⚠️ សូមបើក Sidebar (សញ្ញា > ខាងឆ្វេងលើ) ដើម្បីបញ្ចូល API Key សិន។")
            else:
                with st.spinner("កំពុងវិភាគ... 🎧"):
                    tmp_file_path = None
                    try:
                        genai.configure(api_key=st.session_state.api_key)
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_file_path = tmp_file.name

                        audio_file = genai.upload_file(path=tmp_file_path)
                        model = genai.GenerativeModel('models/gemini-3.5-flash')
                        
                        prompt_instruction = f"""
                        Listen to the audio track. The main climax/'drop' is at {time_string}.
                        
                        Context:
                        - Subject: {st.session_state.char_desc}
                        - Location: {location}
                        - Camera: {camera_style}
                        - Lighting: {lighting_style}
                        
                        Tasks:
                        1. Analyze the audio drop at {time_string}. Determine the required 'Motion Speed'.
                        2. Write 'Scene 3' Prompt using exact formula: "[Camera] of [Subject], [Sudden physical reaction and Motion Speed matching the audio drop]. [Location]. [Lighting]. Photorealistic, high quality."
                        3. Write 'Scene 4' Prompt (Continuous vibe).
                        
                        Do not write explanations. Just output the two formatted prompts clearly.
                        """
                        
                        response = model.generate_content([prompt_instruction, audio_file])
                        
                        st.session_state.ai_response = response.text
                        st.session_state.scene1_prompt = f"{camera_style} of {st.session_state.char_desc}, stopping abruptly and looking friendly at the camera. {location}. {lighting_style}. Photorealistic, continuous motion, high quality."
                        st.session_state.scene2_prompt = f"Close-up {camera_style} of {st.session_state.char_desc}, putting on large over-ear headphones and closing eyes to tune in. {location}. {lighting_style}. Photorealistic, seamless motion, high quality."
                        
                        st.success("ជោគជ័យ! 🎉")
                        
                    except Exception as e:
                        st.error(f"បញ្ហា: {e}")
                    finally:
                        if tmp_file_path and os.path.exists(tmp_file_path):
                            os.remove(tmp_file_path)

    # ផ្នែកបង្ហាញ និងទាញយក Prompts (រៀបជាជួរឈរតែមួយសម្រាប់ Mobile)
    if st.session_state.scene1_prompt or st.session_state.scene2_prompt or st.session_state.ai_response:
        st.divider()
        st.markdown("### Generated Prompts")
        s1 = st.text_area("🎬 Scene 1 (៥ វិនាទី)", value=st.session_state.scene1_prompt, height=100)
        s2 = st.text_area("🎬 Scene 2 (៥ វិនាទី)", value=st.session_state.scene2_prompt, height=100)
        s34 = st.text_area("🔥 Scene 3 & 4", value=st.session_state.ai_response, height=200)
                
        full_export_text = f"--- OMNIREACT AI PROMPTS ---\nTimestamp Drop: {time_string}\n\n[Scene 1]\n{s1}\n\n[Scene 2]\n{s2}\n\n[Scene 3 & 4]\n{s34}\n"
        st.download_button(
            label="📥 ទាញយក Prompts (.txt)",
            data=full_export_text,
            file_name="omnireact_prompts.txt",
            mime="text/plain",
            use_container_width=True
        )
