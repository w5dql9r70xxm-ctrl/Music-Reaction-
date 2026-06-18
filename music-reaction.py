import streamlit as st
import google.generativeai as genai
import tempfile
import os

# ១. ការកំណត់ទំព័រ
st.set_page_config(page_title="Omni Flash Music Reaction Director", page_icon="⚡", layout="wide")

# ២. ការប្រើប្រាស់ Session State
if 'ai_response' not in st.session_state:
    st.session_state.ai_response = ""
if 'scene1_prompt' not in st.session_state:
    st.session_state.scene1_prompt = ""
if 'scene2_prompt' not in st.session_state:
    st.session_state.scene2_prompt = ""
if 'char_desc' not in st.session_state:
    st.session_state.char_desc = "A young, stylish Asian person in their 20s, wearing a black oversized hoodie and a silver chain."

st.title("⚡ Omni Flash Music Reaction Director")
st.markdown("កម្មវិធីសរសេរ Prompts ត្រូវស្តង់ដារ **Omni Flash Model**! រចនាសម្ព័ន្ធអត្ថបទខ្លី ច្បាស់ ផ្តោតលើចលនា និងពន្លឺ Cinematic។")

# របារចំហៀង (Sidebar) 
with st.sidebar:
    st.header("⚙️ ការកំណត់ទូទៅ")
    api_key = st.text_input("🔑 បញ្ចូល Gemini API Key:", type="password")
    
    st.divider()
    st.subheader("👤 ការកំណត់ទិដ្ឋភាព (Visuals)")
    
    # Auto Cast
    if api_key:
        if st.button("🎲 Auto Cast (ឱ្យ AI បង្កើតតួអង្គថ្មី)", use_container_width=True):
            with st.spinner("កំពុងស្វែងរកតួអង្គ..."):
                try:
                    genai.configure(api_key=api_key)
                    cast_model = genai.GenerativeModel('models/gemini-3.5-flash')
                    cast_prompt = "Generate a highly detailed, 1-sentence description of a unique, trendy, and stylish person for a cinematic AI video prompt. Specify their age, ethnicity, cinematic streetwear/fashion, and one distinct facial feature or accessory. English only."
                    cast_response = cast_model.generate_content(cast_prompt)
                    st.session_state.char_desc = cast_response.text.strip()
                    st.rerun()
                except Exception as e:
                    st.error(f"បញ្ហា: {e}")
    else:
        st.info("បញ្ចូល API Key សិន ដើម្បីប្រើមុខងារ Auto Cast")

    st.text_area("ពណ៌នាតួអង្គ (Character Description):", key="char_desc")
    
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
    
    # ជម្រើសពន្លឺថ្មី (Lighting Options)
    lighting_style = st.selectbox("ពន្លឺ & ពណ៌ (Lighting & Color):", [
        "Cinematic moody lighting with deep shadows",
        "Neon cyberpunk glow (vibrant pinks and blues)",
        "Golden hour sunlight (warm and cinematic)",
        "High-contrast dramatic studio lighting",
        "Natural overcast daylight (realistic and raw)"
    ])

# ផ្នែកចម្បងនៃកម្មវិធី
if api_key:
    genai.configure(api_key=api_key)

    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.subheader("🎵 ជំហានទី១: Upload & កំណត់នាទី")
        uploaded_file = st.file_uploader("Upload Audio (MP3, WAV)", type=['mp3', 'wav', 'm4a'])

        if uploaded_file is not None:
            st.audio(uploaded_file, format='audio/mp3')
            st.markdown("⏱️ **នាទីវគ្គ Hype (Drop):**")
            c1, c2 = st.columns(2)
            with c1:
                drop_min = st.number_input("នាទី", min_value=0, value=0, step=1)
            with c2:
                drop_sec = st.number_input("វិនាទី", min_value=0, max_value=59, value=30, step=1)
                
            time_string = f"{drop_min}:{drop_sec:02d}"
            
            if st.button("✨ វិភាគ និងបង្កើតវីដេអូ Prompts", use_container_width=True):
                with st.spinner(f"AI កំពុងវិភាគនាទីទី {time_string}... 🎧"):
                    tmp_file_path = None
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_file_path = tmp_file.name

                        audio_file = genai.upload_file(path=tmp_file_path)
                        model = genai.GenerativeModel('models/gemini-3.5-flash')
                        
                        # Meta-Prompt ថ្មី រៀបចំជាពិសេសសម្រាប់ Omni Flash
                        prompt_instruction = f"""
                        Listen to the audio track. The main climax/'drop' is at {time_string}.
                        
                        Context for Omni Flash Video Model:
                        - Subject: {st.session_state.char_desc}
                        - Location: {location}
                        - Camera: {camera_style}
                        - Lighting: {lighting_style}
                        
                        Tasks:
                        1. Analyze the audio drop at {time_string}. Determine the required 'Motion Speed' (e.g., fast-paced energetic motion, slow-motion awe, rhythmic headbanging).
                        2. Write 'Scene 3' Prompt. MUST USE THIS EXACT FORMULA: 
                           "[Camera] of [Subject], [Sudden physical reaction and Motion Speed matching the audio drop]. [Location]. [Lighting]. Photorealistic, high quality."
                        3. Write 'Scene 4' Prompt (Continuous vibe). MUST USE THE SAME FORMULA, continuing the action smoothly.
                        
                        Do not write explanations. Just output the two formatted prompts clearly.
                        """
                        
                        response = model.generate_content([prompt_instruction, audio_file])
                        
                        # បង្កើត Prompts ដោយប្រើរូបមន្ត Omni Flash
                        st.session_state.ai_response = response.text
                        st.session_state.scene1_prompt = f"{camera_style} of {st.session_state.char_desc}, stopping abruptly and looking friendly at the camera. {location}. {lighting_style}. Photorealistic, continuous motion, high quality."
                        st.session_state.scene2_prompt = f"Close-up {camera_style} of {st.session_state.char_desc}, putting on large over-ear headphones and closing eyes to tune in. {location}. {lighting_style}. Photorealistic, seamless motion, high quality."
                        
                        st.success("ជោគជ័យ! លទ្ធផលនៅខាងស្តាំ 👉")
                        
                    except Exception as e:
                        st.error(f"បញ្ហា: {e}")
                    finally:
                        if tmp_file_path and os.path.exists(tmp_file_path):
                            os.remove(tmp_file_path)

    with col2:
        st.subheader("🎥 Omni Flash Prompts (កែសម្រួលបាន)")
        
        s1 = st.text_area("🎬 Scene 1: ស្ទាក់សួរ (៥ វិនាទី)", value=st.session_state.scene1_prompt, height=100)
        s2 = st.text_area("🎬 Scene 2: ពាក់កាស (៥ វិនាទី)", value=st.session_state.scene2_prompt, height=100)
        s34 = st.text_area("🔥 Scene 3 & 4: Reaction & Vibe", value=st.session_state.ai_response, height=250)
                
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
            label="📥 ទាញយក Prompts ទាំងអស់ (.txt)",
            data=full_export_text,
            file_name="omni_flash_prompts.txt",
            mime="text/plain",
            use_container_width=True
        )
else:
    st.info("👈 សូមបញ្ចូល Gemini API Key នៅរបារចំហៀងខាងឆ្វេង។")
