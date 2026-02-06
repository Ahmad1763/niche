import streamlit as st
import json
import urllib.request
from datetime import datetime

# --- INITIALIZATION ---
if 'shortlist' not in st.session_state:
    st.session_state.shortlist = []

st.set_page_config(page_title="Niche Master AI", layout="wide")

# Sidebar: API Key Handling
api_key = st.secrets.get("YOUTUBE_API_KEY") or st.sidebar.text_input("YouTube API Key", type="password")

if not api_key:
    st.warning("Please enter your API Key in the sidebar or Streamlit Secrets.")
    st.stop()

# --- UTILITY FUNCTION (Fixes the Tab 1 Issue) ---
def fetch_youtube_data(url):
    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        st.error(f"YouTube API Error: {e}")
        return None

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["🔍 Run Analysis", "💡 AI Niche Ideas", "⭐ Shortlist"])

with tab1:
    st.header("Deep Niche Analysis")
    query = st.text_input("Enter keyword to test against criteria", "")
    
    if st.button("Analyze Now") and query:
        search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query.replace(' ', '%20')}&type=video&maxResults=10&key={api_key}"
        data = fetch_youtube_data(search_url)
        
        if data:
            results = []
            new_channels = 0
            for item in data.get('items', []):
                c_id = item['snippet']['channelId']
                c_url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&id={c_id}&key={api_key}"
                c_data = fetch_youtube_data(c_url)
                
                if c_data and 'items' in c_data:
                    chan = c_data['items'][0]
                    subs = int(chan['statistics'].get('subscriberCount', 0))
                    date_str = chan['snippet']['publishedAt'][:10]
                    is_new = (datetime.now() - datetime.strptime(date_str, "%Y-%m-%d")).days < 90
                    if is_new: new_channels += 1
                    
                    results.append({"Channel": chan['snippet']['title'], "Subs": subs, "New": "✅" if is_new else "❌"})
            
            # Show Analysis Results
            st.write(f"### Results for: {query}")
            c1, c2 = st.columns(2)
            max_s = max([r['Subs'] for r in results]) if results else 0
            c1.metric("Max Subs", f"{max_s:,}", delta="Passed" if max_s < 20000 else "Failed", delta_color="normal" if max_s < 20000 else "inverse")
            c2.metric("New Channels (<3mo)", new_channels, delta="Target: 2+" if new_channels >= 2 else "Low Growth")
            st.table(results)

with tab2:
    st.header("AI-Friendly Faceless Niche Ideas")
    # Expanded Niche List based on your request
    ai_niches = [
        {"name": "AI Historical Tales", "desc": "Using AI images/video to tell 'Lost History' or 'Unsolved Mysteries'."},
        {"name": "Restoration Zen", "desc": "Satisfying AI-enhanced restoration of old phones, tools, or art."},
        {"name": "Finance Breakdown", "desc": "Faceless whiteboard-style AI videos explaining credit and stocks."},
        {"name": "Cosmic Analog Horror", "desc": "AI-generated creepy space footage and psychological stories."},
        {"name": "AI Side Hustle Logs", "desc": "Testing and showing results of automation systems."},
        {"name": "Philosophy Explained", "desc": "Daily Stoicism or mindset shifts using AI avatars/narrators."},
        {"name": "Geopolitical Deep Dives", "desc": "Animated maps and AI scripts explaining world conflicts."}
    ]

    for niche in ai_niches:
        with st.expander(f"📌 {niche['name']}"):
            st.write(niche['desc'])
            if st.button(f"Shortlist {niche['name']}", key=niche['name']):
                if niche['name'] not in [s['Niche'] for s in st.session_state.shortlist]:
                    st.session_state.shortlist.append({"Niche": niche['name'], "Date": datetime.now().strftime("%Y-%m-%d")})
                    st.toast(f"Saved {niche['name']}!")

with tab3:
    st.header("Your Shortlist")
    if not st.session_state.shortlist:
        st.info("Nothing here yet.")
    else:
        for i, item in enumerate(st.session_state.shortlist):
            cols = st.columns([3, 1])
            cols[0].write(f"**{item['Niche']}** (Added: {item['Date']})")
            if cols[1].button("Remove", key=f"del_{i}"):
                st.session_state.shortlist.pop(i)
                st.rerun()
