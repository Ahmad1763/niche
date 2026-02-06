import streamlit as st
import json
import urllib.request
from datetime import datetime

# --- INITIALIZATION ---
if 'shortlist' not in st.session_state:
    st.session_state.shortlist = []
if 'last_results' not in st.session_state:
    st.session_state.last_results = []

st.set_page_config(page_title="Niche Master", layout="wide")

# Sidebar: Secure API Key Handling
st.sidebar.title("Settings")
# Priority: 1. Secrets file, 2. Manual Input
api_key = st.secrets.get("YOUTUBE_API_KEY") or st.sidebar.text_input("YouTube API Key", type="password")

if not api_key:
    st.warning("Please add your API Key in Streamlit Secrets or enter it above.")
    st.stop()

# --- TABS INTERFACE ---
tab1, tab2, tab3 = st.tabs(["🔍 Research", "💡 Ideas", "⭐ Shortlist"])

# --- TAB 1: MANUAL RESEARCH ---
with tab1:
    st.header("Analyze a Specific Niche")
    query = st.text_input("Enter Niche Keyword", "Handmade Soap DIY")
    
    if st.button("Run Analysis"):
        search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query.replace(' ', '%20')}&type=video&maxResults=10&key={api_key}"
        # ... [Logic to fetch data as before] ...
        # (For space, let's assume the results are stored in st.session_state.last_results)
        st.success(f"Analysis for '{query}' complete! Check the status below.")

# --- TAB 2: NICHE IDEAS (The 'Add Button' Section) ---
with tab2:
    st.header("Niche Idea Generator")
    st.write("Based on your criteria, here are high-potential angles:")
    
    # You can expand this list or even use an AI API to generate it
    suggestions = ["Micro-SaaS for Florists", "Vintage Watch Restoration", "AI Voiceover Tutorials", "Indoor Hydroponics for Small Flats"]
    
    for idea in suggestions:
        col1, col2 = st.columns([3, 1])
        col1.write(f"**{idea}**")
        if col2.button(f"Shortlist", key=idea):
            if idea not in st.session_state.shortlist:
                st.session_state.shortlist.append({"Niche": idea, "Date": datetime.now().strftime("%Y-%m-%d")})
                st.toast(f"Added {idea} to shortlist!")

# --- TAB 3: SHORTLIST ---
with tab3:
    st.header("Your Saved Niches")
    if not st.session_state.shortlist:
        st.info("Your shortlist is empty. Go to the 'Ideas' or 'Research' tab to add some!")
    else:
        for i, item in enumerate(st.session_state.shortlist):
            c1, c2, c3 = st.columns([2, 2, 1])
            c1.write(item['Niche'])
            c2.write(f"Saved: {item['Date']}")
            if c3.button("🗑️", key=f"del_{i}"):
                st.session_state.shortlist.pop(i)
                st.rerun()
