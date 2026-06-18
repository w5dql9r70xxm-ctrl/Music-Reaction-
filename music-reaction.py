import streamlit as st
import google.generativeai as genai
import tempfile
import os
import random

# ១. ការកំណត់ទំព័រ
st.set_page_config(page_title="Music Reaction Prompt", page_icon="🎶", layout="centered", initial_sidebar_state="collapsed")

# ២. ការប្រើប្រាស់ Session State 
if 'ai_response' not in st.session_state:
    st.session_state.ai_response = ""
if 'scene1_prompt' not in st.session_state:
    st.session_state.scene1_prompt = ""
if 'scene2_prompt' not in st.session_state:
    st.session_state.scene2_prompt = ""
if 'char_desc' not in st.session_state:
    st.session_state.char_desc = "A young, stylish Asian person in their 20s, wearing a black oversized hoodie and a silver chain."
if 'api_keys' not in st.session_state:
    st.session_state.api_keys = []
if 'app_lang' not in st.session_state:
    st.session_state.app_lang = "Khmer (ខ្មែរ)"

# ៣. CSS Theme (ដោះស្រាយបញ្ហាប្រអប់ Upload)
st.markdown("""
<style>
    /* ផ្ទៃខាងក្រោយទូទៅ */
    .stApp { background-color: #0d1117; }
    
    /* កែសម្រួល Sidebar */
    [data-testid="stSidebar"] { background-color: #161b22 !important; }
    [data-testid="stSidebar"] * { color: #f0f6fc !important; }
    
    /* ពណ៌ចំណងជើងទូទៅ */
    h1, h2, h3, h4, h5, h6 { color: #ffffff !important; }
    
    .glowing-box {
        border: 2px solid #00e5ff; border-radius: 12px; padding: 20px 15px;
        text-align: center; box-shadow: 0 0 15px rgba(0, 229, 255, 0.4);
        margin-bottom: 20px; background-color: #161b22;
    }
    .main-title { color: #ffffff; font-size: 26px; font-weight: 900; margin-bottom: 5px; text-transform: uppercase; }
    .sub-title { color: #d400ff; font-size: 12px; font-weight: 700; letter-spacing: 1px; }
    p, label, span { color: #f0f6fc !important; }
    
    /* ប្រអប់វាយអក្សរ និង Selectbox */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: #0d1117 !important; color: #00e5ff !important; border: 1px solid #30363d !important;
    }
    
    /* --- ដោះស្រាយបញ្ហា File Uploader (ប្រអប់ Upload) --- */
    [data-testid="stFileUploadDropzone"] {
        background-color: #161b22 !important; /* ផ្ទៃពណ៌ខ្មៅងងឹត */
        border: 1px dashed #00e5ff !important; /* បន្ទាត់ជុំវិញពណ៌ខៀវ */
        border-radius: 8px !important;
    }
    [data-testid="stFileUploadDropzone"] * {
        color: #f0f6fc !important; /* បង្ខំអក្សរខាងក្នុងទាំងអស់ឱ្យចេញពណ៌ស */
    }
    /* ប៊ូតុង "Browse files" នៅក្នុង File Uploader */
    [data-testid="stFileUploadDropzone"] button {
        background-color: #1f2937 !important;
        color: #00e5ff !important;
        border: 1px solid #00e5ff !important;
    }
    [data-testid="stFileUploadDropzone"] button:hover {
        background-color: #00e5ff !important;
        color: #000000 !important;
    }
    
    /* Tabs */
    div[data-baseweb="tab-list"] { gap: 8px; }
    div[data-baseweb="tab"] { background-color: #1f2937; border-radius: 8px; padding: 8px 15px; border: 1px solid #374151; }
    div[data-baseweb="tab"][aria-selected="true"] { background-color: #d400ff; border: none; }
    div[data-baseweb="tab"] p { color: white !important; font-weight: bold; }
    
    /* Buttons */
    .stButton>button { background-color: #00e5ff !important; color: #000000 !important; font-weight: bold !important; border-radius: 8px !important; border: none !important; }
    .stButton>button:hover { background-color: #d400ff !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# ៤. ប្រព័ន្ធបកប្រែ UI
ui = {
    "Khmer (ខ្មែរ)": {
        "tab1": "🎬 បង្កើត Prompts", "tab2": "⚙️ ការកំណត់តួអង្គ និងរូបភាព",
        "api_title": "🔑 ភ្ជាប់ API Keys", "api_desc": "បញ្ចូល API Keys ច្រើន (១ ជួរ ១ Key)",
        "lang_app": "🌐 ភាសាកម្មវិធី:",
        "lang_video": "🗣️ ភាសាក្នុងវីដេអូ/ចម្រៀង:",
        "cast_btn": "🎲 Auto Cast (ស្វែងរកតួអង្គថ្មី)", "char_desc": "ពណ៌នាតួអង្គ (Character Description):",
        "loc": "ទីតាំង (Location):", "cam": "ម៉ូតកាមេរ៉ា (Camera Style):", "light": "ពន្លឺ (Lighting):",
        "upload": "Upload អូឌីយ៉ូ / វីដេអូ", "drop_time": "⏱️ កំណត់វគ្គ Drop:",
        "gen_btn": "✨ វិភាគ & បង្កើត Prompts", "download": "📥 ទាញយក Prompts (.txt)"
    },
    "English": {
        "tab1": "🎬 Generate Prompts", "tab2": "⚙️ Character & Visuals",
        "api_title": "🔑 API Keys Setup", "api_desc": "Enter multiple keys (1 per line)",
        "lang_app": "🌐 App Language:",
        "lang_video": "🗣️ Video Audio Language:",
        "cast_btn": "🎲 Auto Cast (New Character)", "char_desc": "Character Description:",
        "loc": "Location:", "cam": "Camera Style:", "light": "Lighting:",
        "upload": "Upload Audio / Video", "drop_time": "⏱️ Set Drop Timestamp:",
        "gen_btn": "✨ Analyze & Generate Prompts", "download": "📥 Download Prompts (.txt)"
    }
}

# ៥. របារចំហៀង (Sidebar) 
with st.sidebar:
    st.markdown("### 🌐 Settings & Languages")
    st.session_state.app_lang = st.selectbox("App Interface Language:", ["Khmer (ខ្មែរ)", "English"])
    t = ui[st.session_state.app_lang] 
    
    st.markdown(f"**{t['lang_video']}**")
    video_lang = st.selectbox("", ["English", "Khmer", "Thai", "Korean", "Spanish", "Other"], label_visibility="collapsed")
    
    st.divider()
    
    st.markdown(f"### {t['api_title']}")
    st.caption(t['api_desc'])
    api_input = st.text_area("", height=150, label_visibility="collapsed")
    
    if api_input:
        st.session_state.api_keys = [k.strip() for k in api_input.split('\n') if k.strip()]
        
    if len(st.session_state.api_keys) > 0:
        st.success(f"✅ {len(st.session_state.api_keys)} Keys Connected")
    else:
        st.warning("⚠️ No API Key")

# ៦. Header UI
st.markdown("""
<div class="glowing-box">
    <div class="main-title">🎶 Music Reaction Prompt</div>
    <div class="sub-title">VIDEO PROMPT & AUDIO SYNC WORKSTATION</div>
</div>
""", unsafe_allow_html=True)

# ៧. Tabs
tab1, tab2 = st.tabs([t['tab1'], t['tab2']])

# --- TAB 2: Visuals ---
with tab2:
    st.markdown("### 👤 Character & Visuals")
    if st.button(t['cast_btn'], use_container_width=True):
        if len(st.session_state.api_keys) > 0:
            with st.spinner("Casting..."):
                try:
                    genai.configure(api_key=random.choice(st.session_state.api_keys))
                    cast_model = genai.GenerativeModel('models/gemini-3.5-flash')
                    cast_prompt = "Generate a highly detailed, 1-sentence description of a unique, trendy, and stylish person for a cinematic AI video prompt. Specify their age, ethnicity, cinematic streetwear/fashion, and one distinct facial feature or accessory. English only."
                    st.session_state.char_desc = cast_model.generate_content(cast_prompt).text.strip()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.error("⚠️ Please add API Keys in Sidebar!")
            
    st.text_area(t['char_desc'], key="char_desc", height=100)
    
    location = st.selectbox(t['loc'], [
        "Bustling city street / sidewalk", 
        "Professional neon-lit podcast studio", 
        "Inside a modern car at night", 
        "Cozy aesthetic bedroom with LED lights"
    ])
    camera_style = st.selectbox(t['cam'], [
        "Handheld documentary camera",
        "Smooth Steadicam tracking shot",
        "Ultra-wide VLOG angle",
        "Low angle hero shot",
        "Dynamic camera with crash zooms"
    ])
    lighting_style = st.selectbox(t['light'], [
        "Cinematic moody lighting with deep shadows",
        "Neon cyberpunk glow (vibrant pinks and blues)",
        "Golden hour sunlight (warm and cinematic)"
    ])

# --- TAB 1: ផ្នែកចម្បង ---
with tab1:
    st.caption(t['upload'])
    # ទីតាំង Upload (File Uploader) ដែលត្រូវបានកែ CSS រួច
    uploaded_file = st.file_uploader("", type=['mp3', 'wav', 'm4a'], label_visibility="collapsed")

    if uploaded_file is not None:
        st.audio(uploaded_file, format='audio/mp3')
        st.markdown(t['drop_time'])
        
        c1, c2 = st.columns(2)
        with c1:
            drop_min = st.number_input("Min", min_value=0, value=0, step=1, label_visibility="collapsed")
        with c2:
            drop_sec = st.number_input("Sec", min_value=0, max_value=59, value=30, step=1, label_visibility="collapsed")
            
        time_string = f"{drop_min}:{drop_sec:02d}"
        
        if st.button(t['gen_btn'], use_container_width=True):
            if len(st.session_state.api_keys) == 0:
                st.error("⚠️ Please open Sidebar to add API Keys.")
            else:
                with st.spinner("Processing Audio... 🎧"):
                    tmp_file_path = None
                    try:
                        genai.configure(api_key=random.choice(st.session_state.api_keys))
                        
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_file_path = tmp_file.name

                        audio_file = genai.upload_file(path=tmp_file_path)
                        model = genai.GenerativeModel('models/gemini-3.5-flash')
                        
                        prompt_instruction = f"""
                        Listen to the audio track. The vocal/spoken language is in {video_lang}.
                        The main climax/'drop' is at {time_string}.
                        
                        Context:
                        - Subject: {st.session_state.char_desc}
                        - Location: {location}
                        - Camera: {camera_style}
                        - Lighting: {lighting_style}
                        
                        Tasks:
                        1. Analyze the audio drop at {time_string}. Determine the required 'Motion Speed'.
                        2. Write 'Scene 3' Prompt using exact formula: "[Camera] of [Subject], [Sudden physical reaction and Motion Speed matching the audio drop]. [Location]. [Lighting]. Photorealistic, high quality."
                        3. Write 'Scene 4' Prompt (Continuous vibe).
                        
                        CRITICAL RULE: The final output MUST be written ENTIRELY in English to be used in an AI Video Generator.
                        """
                        
                        response = model.generate_content([prompt_instruction, audio_file])
                        st.session_state.ai_response = response.text
                        
                        st.session_state.scene1_prompt = f"{camera_style} of {st.session_state.char_desc}, stopping abruptly and looking friendly at the camera. {location}. {lighting_style}. Photorealistic, continuous motion, high quality."
                        st.session_state.scene2_prompt = f"Close-up {camera_style} of {st.session_state.char_desc}, putting on large over-ear headphones and closing eyes to tune in. {location}. {lighting_style}. Photorealistic, seamless motion, high quality."
                        
                        st.success("ជោគជ័យ! / Success! 🎉")
                        
                    except Exception as e:
                        st.error(f"Error: {e}")
                    finally:
                        if tmp_file_path and os.path.exists(tmp_file_path):
                            os.remove(tmp_file_path)

    # ផ្នែកបង្ហាញ 
    if st.session_state.scene1_prompt:
        st.divider()
        st.markdown("### English Video Prompts (Ready to Copy)")
        s1 = st.text_area("🎬 Scene 1", value=st.session_state.scene1_prompt, height=100)
        s2 = st.text_area("🎬 Scene 2", value=st.session_state.scene2_prompt, height=100)
        s34 = st.text_area("🔥 Scene 3 & 4", value=st.session_state.ai_response, height=200)
                
        full_export_text = f"--- MUSIC REACTION PROMPTS (ENGLISH) ---\nTimestamp Drop: {time_string}\n\n[Scene 1]\n{s1}\n\n[Scene 2]\n{s2}\n\n[Scene 3 & 4]\n{s34}\n"
        st.download_button(
            label=t['download'],
            data=full_export_text,
            file_name="music_reaction_prompts.txt",
            mime="text/plain",
            use_container_width=True
        )
