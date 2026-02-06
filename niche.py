import streamlit as st
import json
import urllib.request
from datetime import datetime

# --- INITIALIZATION ---
if 'shortlist' not in st.session_state:
    st.session_state.shortlist = []
if 'api_key_saved' not in st.session_state:
    st.session_state.api_key_saved = st.secrets.get("YOUTUBE_API_KEY", "")

st.set_page_config(page_title="Niche Master Pro v3", layout="wide")

# --- SIDEBAR: SETTINGS & ADJUSTABLE CRITERIA ---
with st.sidebar:
    st.title("⚙️ Control Panel")
    
    # API Key Handling
    new_key = st.text_input("YouTube API Key", value=st.session_state.api_key_saved, type="password")
    if st.button("Save API Key"):
        st.session_state.api_key_saved = new_key
        st.success("Key saved!")

    st.divider()
    st.subheader("🛠️ Adjustable Criteria")
    # All 8 criteria from your original image
    max_subs = st.number_input("1. Max Sub Limit (Channel Size)", value=20000)
    age_limit = st.slider("2. New Channel Age (Days)", 30, 365, 90)
    view_threshold = st.number_input("3. View Threshold (Monthly)", value=100000)
    # Budget and Skill are qualitative, so we use checkboxes/selects
    budget_match = st.selectbox("4. Budget Match", ["Low Budget", "Mid Budget", "High Budget"])
    skill_match = st.selectbox("5. Skill Match", ["Easy/AI", "Intermediate", "Expert"])
    comp_limit = st.number_input("6. Competition Count (Max Channels)", value=10)
    pool_size = st.number_input("7. Niche Pool (Max Videos)", value=500)
    min_similar = st.number_input("8. Similar Channels Required", value=3)

# --- UTILITY: DYNAMIC NICHE LOGIC ---
def get_micro_niches(query):
    query_l = query.lower()
    # Define smart modifiers based on context
    logic = {
        "finance": [f"Passive income with {query}", f"{query} for students", f"The dark side of {query}", f"AI-Automated {query} news"],
        "history": [f"Daily life in {query}", f"Forgotten heroes of {query}", f"The economics of {query}", f"Unsolved {query} mysteries"],
        "tech": [f"{query} vs Competitors", f"Hidden features of {query}", f"{query} for non-techies", f"Future of {query} (2026)"],
        "gaming": [f"Speedrunning {query}", f"The lore of {query} explained", f"Hidden secrets in {query}", f"Best {query} mods"],
        "default": [f"Beginner's guide to {query}", f"The truth about {query}", f"How to master {query} with AI", f"Common {query} mistakes"]
    }
    
    for key in logic:
        if key in query_l:
            return logic[key]
    return logic["default"]

# --- CORE FUNCTION: FETCH DATA ---
def fetch_yt(url):
    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# --- UI TABS ---
tab1, tab2, tab3 = st.tabs(["🔍 Analysis", "💡 Contextual Micro-Niches", "⭐ Shortlist"])

with tab1:
    st.header("Niche Validation")
    search_q = st.text_input("Enter Niche Keyword", "AI Finance Tools")
    
    if st.button("Validate Now") and search_q:
        api_key = st.session_state.api_key_saved
        search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={search_q.replace(' ', '%20')}&type=video&maxResults=10&key={api_key}"
        data = fetch_yt(search_url)
        
        if data:
            results = []
            new_found = 0
            for item in data.get('items', []):
                cid = item['snippet']['channelId']
                c_data = fetch_yt(f"https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&id={cid}&key={api_key}")
                if c_data and 'items' in c_data:
                    c = c_data['items'][0]
                    s_count = int(c['statistics'].get('subscriberCount', 0))
                    p_date = datetime.strptime(c['snippet']['publishedAt'][:10], "%Y-%m-%d")
                    days = (datetime.now() - p_date).days
                    is_new = days <= age_limit
                    if is_new: new_found += 1
                    results.append({"Channel": c['snippet']['title'], "Link": f"https://youtube.com/channel/{cid}", "Subs": s_count, "New": "✅" if is_new else "❌"})

            # Analysis Summary
            max_s = max([r['Subs'] for r in results]) if results else 0
            if max_s > max_subs or new_found < 2:
                st.error(f"⚠️ Saturated Niche. Max Subs: {max_s:,}. Recommendation: Check the 'Micro-Niches' tab.")
            else:
                st.success("💎 Goldmine! This meets your subscriber and growth criteria.")
            
            st.dataframe(results, column_config={"Link": st.column_config.LinkColumn("Open Channel")}, use_container_width=True)

with tab2:
    st.header("Context-Aware Suggestions")
    if search_q:
        suggestions = get_micro_niches(search_q)
        st.write(f"Based on your search for **'{search_q}'**, try these specific angles:")
        for sn in suggestions:
            c1, c2 = st.columns([4, 1])
            c1.info(f"🔹 {sn}")
            if c2.button("Shortlist", key=sn):
                st.session_state.shortlist.append({"Niche": sn, "Date": datetime.now().strftime("%Y-%m-%d")})
                st.toast(f"Saved {sn}")
    else:
        st.write("Perform an analysis first to see relevant sub-niches.")

with tab3:
    st.header("Saved Shortlist")
    for i, item in enumerate(st.session_state.shortlist):
        cols = st.columns([3, 1])
        cols[0].write(f"⭐ **{item['Niche']}**")
        if cols[1].button("Remove", key=f"del_{i}"):
            st.session_state.shortlist.pop(i)
            st.rerun()
