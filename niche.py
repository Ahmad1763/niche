import streamlit as st
import json
import urllib.request
from datetime import datetime

# --- INITIALIZATION ---
if 'shortlist' not in st.session_state:
    st.session_state.shortlist = []
if 'api_key_saved' not in st.session_state:
    st.session_state.api_key_saved = st.secrets.get("YOUTUBE_API_KEY", "")

st.set_page_config(page_title="Niche Master Pro", layout="wide")

# --- SIDEBAR: SETTINGS & ADJUSTABLE CRITERIA ---
with st.sidebar:
    st.title("⚙️ Global Settings")
    
    # 1. API Key Section
    new_key = st.text_input("YouTube API Key", value=st.session_state.api_key_saved, type="password")
    if st.button("Save API Key"):
        st.session_state.api_key_saved = new_key
        st.success("Key saved for this session!")
    
    st.divider()
    st.subheader("🛠️ Adjustable Criteria")
    
    # Adjustable thresholds based on your original image
    max_subs_limit = st.number_input("Max Subscriber Limit", value=20000, step=1000)
    new_channel_age = st.slider("New Channel Age (Days)", 30, 365, 90)
    min_new_channels = st.number_input("Target New Channels found", value=2)
    view_threshold = st.number_input("Min Views/Month (Reference Only)", value=100000)

# Validate API Key before proceeding
api_key = st.session_state.api_key_saved
if not api_key:
    st.warning("Please enter and save your API Key in the sidebar.")
    st.stop()

# --- UTILITY FUNCTION ---
def fetch_youtube_data(url):
    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        st.error(f"YouTube API Error: {e}")
        return None

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["🔍 Analysis", "💡 AI Ideas", "⭐ Shortlist"])

with tab1:
    st.header("Deep Niche Research")
    query = st.text_input("Enter keyword", "History Documentary AI")
    
    if st.button("Analyze Now") and query:
        search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query.replace(' ', '%20')}&type=video&maxResults=10&key={api_key}"
        data = fetch_youtube_data(search_url)
        
        if data:
            results = []
            new_channels_found = 0
            for item in data.get('items', []):
                c_id = item['snippet']['channelId']
                c_url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&id={c_id}&key={api_key}"
                c_data = fetch_youtube_data(c_url)
                
                if c_data and 'items' in c_data:
                    chan = c_data['items'][0]
                    subs = int(chan['statistics'].get('subscriberCount', 0))
                    date_str = chan['snippet']['publishedAt'][:10]
                    days_old = (datetime.now() - datetime.strptime(date_str, "%Y-%m-%d")).days
                    
                    is_new = days_old <= new_channel_age
                    if is_new: new_channels_found += 1
                    
                    results.append({"Channel": chan['snippet']['title'], "Subs": subs, "Age (Days)": days_old, "New?": "✅" if is_new else "❌"})
            
            # Show Metrics based on ADJUSTABLE criteria
            st.write(f"### Results for: {query}")
            m1, m2 = st.columns(2)
            max_found_subs = max([r['Subs'] for r in results]) if results else 0
            
            m1.metric("Max Subs Found", f"{max_found_subs:,}", 
                      delta="PASSED" if max_found_subs <= max_subs_limit else "FAILED",
                      delta_color="normal" if max_found_subs <= max_subs_limit else "inverse")
            
            m2.metric(f"New Channels (<{new_channel_age}d)", new_channels_found, 
                      delta="PASSED" if new_channels_found >= min_new_channels else "FAILED")
            
            st.table(results)

with tab2:
    st.header("AI-Specific Niche Ideas")
    ai_niches = [
        {"name": "AI Historical Tales", "desc": "Tales and history content using AI imagery."},
        {"name": "Phone Restoration", "desc": "Restoration content, highly viral for tech niches."},
        {"name": "Finance Breakdown", "desc": "Faceless finance content for building authority."},
        {"name": "Cosmic Analog Horror", "desc": "AI-generated sci-fi/horror stories."}
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
        st.info("Your shortlist is empty.")
    else:
        for i, item in enumerate(st.session_state.shortlist):
            c = st.columns([3, 1])
            c[0].write(f"**{item['Niche']}** (Added: {item['Date']})")
            if c[1].button("Remove", key=f"del_{i}"):
                st.session_state.shortlist.pop(i)
                st.rerun()
