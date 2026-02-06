import streamlit as st
import json
import urllib.request
from datetime import datetime

st.set_page_config(page_title="Niche Researcher (Lite)", layout="wide")
st.title("🔍 No-Dependency Niche Researcher")

# Authentication
api_key = st.sidebar.text_input("YouTube API Key", type="password")

if not api_key:
    st.info("Enter your API key to start. Since this uses no external libraries, it's highly stable!")
    st.stop()

query = st.text_input("Niche Keyword", "Handmade Soap DIY")

def fetch_youtube_data(url):
    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        st.error(f"API Error: {e}")
        return None

if st.button("Analyze Niche"):
    # 1. Search Request
    search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query.replace(' ', '%20')}&type=video&maxResults=10&key={api_key}"
    search_data = fetch_youtube_data(search_url)

    if search_data:
        results = []
        new_channels = 0
        
        for item in search_data.get('items', []):
            channel_id = item['snippet']['channelId']
            
            # 2. Get Channel Stats (Subs & Date)
            channel_url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&id={channel_id}&key={api_key}"
            c_data = fetch_youtube_data(channel_url)
            
            if c_data and 'items' in c_data:
                info = c_data['items'][0]
                subs = int(info['statistics'].get('subscriberCount', 0))
                pub_date_str = info['snippet']['publishedAt']
                
                # Manual date parsing (no external libs)
                pub_date = datetime.strptime(pub_date_str[:10], "%Y-%m-%d")
                age_days = (datetime.now() - pub_date).days
                is_new = age_days < 90

                if is_new: new_channels += 1
                
                results.append({
                    "Channel": info['snippet']['title'],
                    "Subs": subs,
                    "Age": f"{age_days} days",
                    "Status": "✅ NEW" if is_new else "Old"
                })

        # --- Display Logic ---
        st.subheader("Selection Criteria Results")
        col1, col2 = st.columns(2)

        # Requirement 1: Size Limit
        max_subs = max([r['Subs'] for r in results]) if results else 0
        if max_subs < 20000:
            col1.success(f"PASSED: Max subs is {max_subs:,} (Limit: 20k)")
        else:
            col1.error(f"FAILED: Large channel found ({max_subs:,} subs)")

        # Requirement 2: New Channels
        if new_channels >= 2:
            col2.success(f"PASSED: Found {new_channels} channels < 3 months old")
        else:
            col2.error(f"FAILED: Only found {new_channels} new channels")

        st.table(results)
