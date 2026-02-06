import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from datetime import datetime, timedelta

# --- SETTINGS & AUTH ---
st.set_page_config(page_title="YouTube Niche Researcher", layout="wide")
st.title("🔍 YouTube Niche Research Tool")

# Input for API Key (Keep it safe in Streamlit Secrets on GitHub)
API_KEY = st.sidebar.text_input("Enter YouTube API Key", type="password")

if not API_KEY:
    st.warning("Please enter your YouTube API Key in the sidebar to begin.")
    st.stop()

youtube = build('youtube', 'v3', developerKey=API_KEY)

# --- HELPER FUNCTIONS ---
def get_channel_data(channel_id):
    request = youtube.channels().list(
        part="snippet,statistics",
        id=channel_id
    )
    response = request.execute()
    if response['items']:
        item = response['items'][0]
        return {
            "title": item['snippet']['title'],
            "subs": int(item['statistics']['subscriberCount']),
            "publishedAt": item['snippet']['publishedAt']
        }
    return None

# --- SEARCH LOGIC ---
query = st.text_input("Enter Niche Keyword (e.g., 'AI Automations')", "ASMR for Squirrels")

if st.button("Analyze Niche"):
    with st.spinner("Scraping YouTube data..."):
        # 1. Search for videos
        search_request = youtube.search().list(
            q=query,
            part="snippet",
            maxResults=15,
            type="video"
        )
        search_response = search_request.execute()
        
        results = []
        new_channels_count = 0
        total_videos_found = len(search_response['items'])
        
        for item in search_response['items']:
            channel_id = item['snippet']['channelId']
            channel_info = get_channel_data(channel_id)
            
            if channel_info:
                # Calculate Age
                pub_date = datetime.strptime(channel_info['publishedAt'], "%Y-%m-%dT%H:%M:%SZ")
                age_days = (datetime.now() - pub_date).days
                is_new = age_days < 90  # 3 Months check
                
                if is_new: new_channels_count += 1
                
                results.append({
                    "Channel": channel_info['title'],
                    "Subscribers": channel_info['subs'],
                    "Age (Days)": age_days,
                    "New Channel?": "✅" if is_new else "❌"
                })

        df = pd.DataFrame(results)

        # --- CRITERIA EVALUATION ---
        st.subheader("📊 Niche Selection Criteria Results")
        
        c1, c2, c3 = st.columns(3)
        
        # Criterion 1: Channel Size Limit (<20k)
        max_subs = df['Subscribers'].max()
        c1.metric("Max Subs Found", f"{max_subs:,}")
        if max_subs < 20000:
            c1.success("Requirement 1: PASSED (<20k subs)")
        else:
            c1.error("Requirement 1: FAILED (>20k subs)")

        # Criterion 2: Channel Age (2-3 channels < 3 months old)
        c2.metric("New Channels Found", new_channels_count)
        if new_channels_count >= 2:
            c2.success("Requirement 2: PASSED (New channels active)")
        else:
            c2.error("Requirement 2: FAILED (No new players)")

        # Criterion 6: Competition Count
        unique_competitors = df['Channel'].nunique()
        c3.metric("Total Competitors", unique_competitors)
        if unique_competitors <= 10:
            c3.success("Requirement 6: PASSED (Low competition)")
        else:
            c3.warning("Requirement 6: FAILED (Crowded niche)")

        # --- DATA TABLE ---
        st.divider()
        st.write("### Raw Competitor Data")
        st.dataframe(df.style.highlight_max(axis=0, subset=['Subscribers'], color='#ff4b4b'))
