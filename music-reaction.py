import streamlit as st
import google.generativeai as genai
import tempfile
import os

# ១. ការកំណត់ទំព័រ (ត្រូវតែនៅខាងលើគេជានិច្ច)
st.set_page_config(page_title="Omni Flash Director Pro", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

# ២. ការប្រើប្រាស់ Session State សម្រាប់រក្សាទុកទិន្នន័យ
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

# ៣. ការសរសេរ Custom CSS សម្រាប់ UI ថ្មី (Dark Theme & Glowing Box)
st.markdown("""
<style>
    /* ការកំណត់ពណ៌ផ្ទៃខាងក្រោយ (Dark Theme) */
    .stApp {
        background-color: #0e1117;
    }
    
    /* ប្រអប់ចំណងជើងមានពន្លឺ (Glowing Box) */
    .glowing-box {
        border: 2px solid #d400ff; /* ពណ៌ស្វាយ/ស៊ីជម្ពូ */
        border-radius: 15px;
        padding: 30px 20px;
        text-align: center;
        box-shadow: 0 0 15px rgba(212, 0, 255, 0.3); /* ពន្លឺសាយ */
        margin-bottom: 25px;
        background-color: #161b22;
    }
    
    .main-title {
        color: white;
        font-size: 32px;
        font-weight: 800;
        margin-bottom: 10px;
        font-family: sans-serif;
    }
    
    .sub-title {
        color: #00e5ff; /* ពណ៌ខៀវខ្ចី */
        font-size: 14px;
        font-weight: 700;
        letter-spacing: 1.5px;
    }

    /* កែសម្រួល Tab របស់ Streamlit ឱ្យស្រដៀងប៊ូតុង */
    div[data-baseweb="tab-list"] {
        gap: 10px;
    }
    div[data-baseweb="tab"] {
        background-color: #1f2937;
        border-radius: 8px;
        padding: 10px 15px;
        border: none;
        color: white;
    }
    div[data-baseweb="tab"]:focus {
        outline: none;
    }
    
    /* បំបាត់បន្ទាត់ពណ៌ក្រហមខាងលើ Tab របស់ Streamlit */
    div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
        background-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

# ៤. Header UI (Glowing Box)
st.markdown("""
<div class="glowing-box">
    <div class="main-title">Omni Flash Director Pro</div>
    <div class="sub-title">GLOBAL AI VIDEO PROMPT & AUDIO SYNC WORKSTATION</div>
</div>
""", unsafe_allow_html=True)

# ៥. ការបង្កើត Tabs ជំនួស Sidebar 
tab1, tab2, tab3 = st.tabs(["🎬 Generate Prompts", "👤 Visual Settings", "🔑 API Setup"])

# --- TAB 3: ការកំណត់ API ---
with tab3:
    st.markdown("## 🔑 Setup Google Gemini API")
    api_input = st.text_input("បញ្ចូល API Key របស់អ្នកនៅទីនេះ:", type="password", value=st.session_state.api_key)
    if api_input:
        st.session_state.api_key = api_input
    st.info("💡 អ្នកត្រូវបញ្ចូល API Key នៅក្នុង Tab នេះជាមុនសិន ទើបមុខងារ Auto Cast និង វិភាគសំឡេងអាចដំណើរការបាន។")

# --- TAB 2: ការកំណត់រូបភាព និងតួអង្គ ---
with tab2:
    st.markdown("## 👤 Character & Camera Setup")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("### 1️⃣ Character (តួអង្គ)")
        if st.button("🎲 Auto Cast (ឱ្យ AI បង្កើតតួអង្គថ្មី)", use_container_width=True):
            if st.session_state.api_key:
                with st.spinner("កំពុងស្វែងរកតួអង្គ (Casting)..."):
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
                st.warning("⚠️ សូមបញ្ចូល API Key នៅក្នុង Tab 'API Setup' សិន!")
                
        st.text_area("ពណ៌នាតួអង្គ (Character Description):", key="char_desc", height=130)
        
    with col_b:
        st.markdown("### 2️⃣ Environment (បរិយាកាស)")
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
        lighting_style = st.selectbox("ពន្លឺ & ពណ៌ (Lighting & Color):", [
            "Cinematic moody lighting with deep shadows",
            "Neon cyberpunk glow (vibrant pinks and blues)",
            "Golden hour sunlight (warm and cinematic)",
            "High-contrast dramatic studio lighting",
            "Natural overcast daylight (realistic and raw)"
        ])

# --- TAB 1: ផ្នែកចម្បងសម្រាប់ Generate Prompts ---
with tab1:
    st.markdown("## 1️⃣ Generate Prompts (Omni Flash & Veo3)")
    
    col1, col2 = st.columns([1, 1.2])

    # ជួរឈរទី១៖ Upload & វិភាគ
    with col1:
        st.caption("Upload Video / Audio Track")
        uploaded_file = st.file_uploader("", type=['mp3', 'wav', 'm4a'], help="100MB per file • MP3, WAV, M4A")

        if uploaded_file is not None:
            st.audio(uploaded_file, format='audio/mp3')
            st.markdown("⏱️ **កំណត់នាទីវគ្គ Hype (Drop):**")
            
            c1, c2 = st.columns(2)
            with c1:
                drop_min = st.number_input("នាទី", min_value=0, value=0, step=1)
            with c2:
                drop_sec = st.number_input("វិនាទី", min_value=0, max_value=59, value=30, step=1)
                
            time_string = f"{drop_min}:{drop_sec:02d}"
            
            if st.button("✨ វិភាគ Audio និងបង្កើត Prompts", use_container_width=True):
                if not st.session_state.api_key:
                    st.error("⚠️ សូមទៅកាន់ Tab '🔑 API Setup' ដើម្បីបញ្ចូល API Key ជាមុនសិន។")
                else:
                    with st.spinner(f"AI កំពុងវិភាគនាទីទី {time_string}... 🎧"):
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
                            
                            Context for Omni Flash Video Model:
                            - Subject: {st.session_state.char_desc}
                            - Location: {location}
                            - Camera: {camera_style}
                            - Lighting: {lighting_style}
                            
                            Tasks:
                            1. Analyze the audio drop at {time_string}. Determine the required 'Motion Speed' (e.g., fast-paced energetic motion, slow-motion awe).
                            2. Write 'Scene 3' Prompt. MUST USE THIS EXACT FORMULA: 
                               "[Camera] of [Subject], [Sudden physical reaction and Motion Speed matching the audio drop]. [Location]. [Lighting]. Photorealistic, high quality."
                            3. Write 'Scene 4' Prompt (Continuous vibe). MUST USE THE SAME FORMULA, continuing the action smoothly.
                            
                            Do not write explanations. Just output the two formatted prompts clearly.
                            """
                            
                            response = model.generate_content([prompt_instruction, audio_file])
                            
                            st.session_state.ai_response = response.text
                            st.session_state.scene1_prompt = f"{camera_style} of {st.session_state.char_desc}, stopping abruptly and looking friendly at the camera. {location}. {lighting_style}. Photorealistic, continuous motion, high quality."
                            st.session_state.scene2_prompt = f"Close-up {camera_style} of {st.session_state.char_desc}, putting on large over-ear headphones and closing eyes to tune in. {location}. {lighting_style}. Photorealistic, seamless motion, high quality."
                            
                            st.success("ការវិភាគជោគជ័យ! 🎉")
                            
                        except Exception as e:
                            st.error(f"បញ្ហា: {e}")
                        finally:
                            if tmp_file_path and os.path.exists(tmp_file_path):
                                os.remove(tmp_file_path)

    # ជួរឈរទី២៖ បង្ហាញនិងកែសម្រួល Prompts
    with col2:
        st.markdown("### Generated Prompts")
        st.caption("អ្នកអាចចុចកែសម្រួលផ្ទាល់នៅក្នុងប្រអប់មុននឹងទាញយក។")
        
        s1 = st.text_area("🎬 Scene 1 (៥ វិនាទី)", value=st.session_state.scene1_prompt, height=90)
        s2 = st.text_area("🎬 Scene 2 (៥ វិនាទី)", value=st.session_state.scene2_prompt, height=90)
        s34 = st.text_area("🔥 Scene 3 & 4 (វិភាគដោយ AI)", value=st.session_state.ai_response, height=220)
                
        # ប៊ូតុង Download
        if s1 or s2 or s34:
            st.divider()
            full_export_text = f"""--- OMNI FLASH VIDEO PROMPTS ---
Timestamp Drop: {time_string}

[Scene 1]
{s1}

[Scene 2]
{s2}

[Scene 3 & 4]
{s34}
"""
            st.download_button(
                label="📥 ទាញយក Prompts (.txt)",
                data=full_export_text,
                file_name="omni_flash_prompts.txt",
                mime="text/plain",
                use_container_width=True
            )
