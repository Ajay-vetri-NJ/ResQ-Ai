import streamlit as st
import requests
import base64
import pydeck as pdk
import pandas as pd
import io
import time
from PIL import Image

# --- PAGE CONFIG ---
st.set_page_config(page_title="ResQ AI", page_icon="🚨", layout="wide")
st.title("🚨 ResQ AI: Autonomous Disaster Commander")

# --- SIDEBAR: CONTROLS ---
st.sidebar.header("⚙️ Configuration")
# We use st.secrets for cloud deployment, or fallback to input
# This prevents the app from crashing if secrets aren't set yet
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    st.sidebar.success("✅ API Key Loaded from Secrets")
else:
    api_key = st.sidebar.text_input("🔑 Google API Key", type="password")

model_choice = st.sidebar.selectbox(
    "🤖 AI Model", 
    ["gemini-1.5-flash-001", "gemini-1.5-flash", "gemini-pro-vision", "gemini-1.5-pro"]
)

demo_mode = st.sidebar.checkbox("⚠️ Enable Demo Mode (Simulation)", value=False)

# --- FUNCTION: API CALL ---
def analyze_image_with_gemini(image_bytes, key, model_name):
    if demo_mode:
        time.sleep(2)
        return "HAZARD: Industrial Fire\nSEVERITY: 9/10\nACTION: Dispatch Unit Alpha & Evacuate Zone B."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
    
    b64_data = base64.b64encode(image_bytes).decode('utf-8')
    payload = {
        "contents": [{
            "parts": [
                {"text": "Analyze this disaster scene. Report Hazard Type, Severity (1-10), and Recommended Action."},
                {"inline_data": {"mime_type": "image/jpeg", "data": b64_data}}
            ]
        }]
    }
    
    response = requests.post(url, headers={'Content-Type': 'application/json'}, json=payload)
    
    if response.status_code == 200:
        try:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        except:
            return "Error: Could not parse AI response."
    else:
        return f"API ERROR ({response.status_code}): {response.text}"

# --- MAIN UI ---
col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("📸 Site Analysis")
    uploaded_file = st.file_uploader("Upload Scene Photo", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, use_column_width=True)
        
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_bytes = img_byte_arr.getvalue()
        
        if st.button("Analyze Hazard", type="primary"):
            if not api_key and not demo_mode:
                st.error("Please enter an API Key or enable Demo Mode.")
            else:
                with st.spinner(f"Connecting to {model_choice}..."):
                    result = analyze_image_with_gemini(img_bytes, api_key, model_choice)
                    
                    if "API ERROR" in result:
                        st.error(result)
                        st.warning("👇 TRY THIS: Change the 'AI Model' in the sidebar dropdown!")
                    else:
                        st.success("Analysis Complete")
                        st.markdown(result)

with col2:
    st.subheader("📍 Info Institute Live Map")
    data = pd.DataFrame({
        'lat': [11.0830, 11.0850, 11.0810], 
        'lon': [77.0620, 77.0640, 77.0600],
        'severity': [8, 5, 2]
    })
    
    st.pydeck_chart(pdk.Deck(
        map_style=None,
        initial_view_state=pdk.ViewState(
            latitude=11.0830,
            longitude=77.0620,
            zoom=14,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                'HexagonLayer',
                data=data,
                get_position='[lon, lat]',
                radius=60,
                elevation_scale=100,
                elevation_range=[0, 1000],
                pickable=True,
                extruded=True,
                 get_fill_color="[255, (1-severity/10)*255, 0, 200]",
            ),
        ],
    ))
