import streamlit as st
import json
import urllib.request
from datetime import datetime
import pandas as pd # Optional, but helps for the clickable link config

# --- INITIALIZATION ---
if 'shortlist' not in st.session_state:
    st.session_state.shortlist = []
if 'api_key_saved' not in st.session_state:
    st.session_state.api_key_saved = st.secrets.get("YOUTUBE_API_KEY", "")

st.set_page_config(page_title="Niche Master Pro v2", layout="wide")

# --- SIDEBAR: SETTINGS & CRITERIA ---
with st.sidebar:
    st.title("⚙️ Global Settings")
    new_key = st.text_input("YouTube API Key", value=st.session_state.api_key_saved, type="password")
    if st.button("Save API Key"):
        st.session_state.api_key_saved = new_key
        st.success("Key saved!")
    
    st.divider()
    st.subheader("🛠️ Adjustable Criteria")
    max_subs_limit = st.number_input("Max Subscriber Limit", value=20000)
    new_channel_age = st.slider("New Channel Age (Days)", 30, 365, 90)
    min_new_channels = st.number_input("Target New Channels", value=2)

api_key = st.session_state.api_key_saved

# --- UTILITY: FETCH DATA ---
def fetch_yt(url):
    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode())
    except: return None

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["🔍 Analysis", "💡 AI & Micro-Niches", "⭐ Shortlist"])

with tab1:
    st.header("Niche Validation")
    query = st.text_input("Enter Niche Keyword", "Ancient History")
    
    if st.button("Validate Niche") and query:
        search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query.replace(' ', '%20')}&type=video&maxResults=10&key={api_key}"
        data = fetch_yt(search_url)
        
        if data:
            results_data = []
            new_count = 0
            for item in data.get('items', []):
                c_id = item['snippet']['channelId']
                c_data = fetch_yt(f"https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&id={c_id}&key={api_key}")
                
                if c_data and 'items' in c_data:
                    chan = c_data['items'][0]
                    subs = int(chan['statistics'].get('subscriberCount', 0))
                    date_str = chan['snippet']['publishedAt'][:10]
                    days_old = (datetime.now() - datetime.strptime(date_str, "%Y-%m-%d")).days
                    is_new = days_old <= new_channel_age
                    if is_new: new_count += 1
                    
                    # Create clickable URL
                    results_data.append({
                        "Channel Name": chan['snippet']['title'],
                        "Link": f"https://www.youtube.com/channel/{c_id}",
                        "Subscribers": subs,
                        "New?": "✅" if is_new else "❌"
                    })

            # Check for Saturation
            max_s = max([r['Subscribers'] for r in results_data]) if results_data else 0
            is_saturated = max_s > max_subs_limit or new_count < min_new_channels
            
            # --- DISPLAY RESULTS ---
            if is_saturated:
                st.error(f"⚠️ This niche is SATURATED based on your settings. (Max Subs: {max_s:,})")
                st.info(f"💡 Recommendation: Try a 'Micro-Niche' in the Ideas tab.")
            else:
                st.success("💎 GOLDMINE FOUND! This niche meets all criteria.")

            # Clickable Dataframe
            st.dataframe(
                results_data,
                column_config={
                    "Link": st.column_config.LinkColumn("Open Channel")
                },
                use_container_width=True
            )

with tab2:
    st.header("Sub-Niche & Micro-Niche Suggestions")
    
    if query:
        st.write(f"Refining **'{query}'** into unsaturated sub-niches:")
        
        # Logic to generate micro-niches based on user's query
        micro_niches = [
            f"{query} for Absolute Beginners",
            f"AI-Generated {query} Tales",
            f"Historical {query} Mysteries (Faceless)",
            f"{query} Restoration & Repairs",
            f"Budget-Friendly {query} Hacks"
        ]
        
        for mn in micro_niches:
            col1, col2 = st.columns([4, 1])
            col1.write(f"🔹 **{mn}**")
            if col2.button("Analyze This", key=mn):
                st.info(f"Rerunning analysis for {mn}... (Switch to Tab 1)")
                # This could be improved to auto-trigger the search
            if col1.button(f"Shortlist {mn}", key=f"sl_{mn}"):
                st.session_state.shortlist.append({"Niche": mn, "Date": datetime.now().strftime("%Y-%m-%d")})
                st.toast("Saved!")
    else:
        st.info("Perform an analysis in Tab 1 first to get related micro-niche suggestions.")

with tab3:
    st.header("Your Shortlist")
    for i, item in enumerate(st.session_state.shortlist):
        st.write(f"⭐ **{item['Niche']}** (Added: {item['Date']})")
