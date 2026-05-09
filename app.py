import streamlit as st
import pandas as pd
import random
import re

# --- 1. CLUB DATABASE ---
# FBRef IDs are required for direct URL scraping. 
# You can add more by finding the code in the FBRef club URL.
CLUB_IDS = {
    "inter milan": "d60ad303",
    "chelsea": "cff3d3bb",
    "man utd": "19538871",
    "liverpool": "822bd0ba",
    "arsenal": "18bb7c10",
    "real madrid": "5324c30a",
    "ac milan": "103",
    "juventus": "111",
    "man city": "b8fd03ef",
    "barcelona": "206d9d25",
    "bayern munich": "054fdde2",
    "psg": "e2d8892c"
}

# --- 2. STABLE SCRAPING ENGINE ---
@st.cache_data(show_spinner="Fetching data from FBRef...")
def get_online_answers(task_text):
    """
    Directly reads the HTML table from FBRef using Pandas.
    Bypasses the need for Selenium/Chromium.
    """
    t = task_text.lower()
    try:
        if "played for both" in t:
            match = re.search(r"both (.*?) & (.*)", t)
            if match:
                c1, c2 = match.group(1).strip().lower(), match.group(2).strip().lower()
                id1, id2 = CLUB_IDS.get(c1), CLUB_IDS.get(c2)
                
                if id1 and id2:
                    url = f"https://fbref.com/en/friv/players-who-played-for-multiple-clubs-countries.fcgi?t1={id1}&t2={id2}"
                    # Header required to avoid 403 Forbidden errors from some servers
                    storage_options = {'User-Agent': 'Mozilla/5.0'}
                    tables = pd.read_html(url, storage_options=storage_options)
                    if tables:
                        # Clean the list: remove NaN and get unique names
                        return tables[0]['Player'].dropna().unique().tolist()
        return []
    except Exception as e:
        return [f"Lookup Error: Ensure club names match the database."]

# --- 3. SESSION INITIALIZATION ---
# This ensures the app always has data to display, preventing blank pages.
if 'game_started' not in st.session_state:
    st.session_state.update({
        'game_started': False,
        'grid_size': 4,
        'num_players': 2,
        'turn': 0,
        'player_data': {},
        'grid_map': [],
        'rolled': False,
        'p_names': ["", "", "", ""]
    })

# --- 4. MAIN UI ---
st.set_page_config(page_title="Football Trivia Path", layout="wide")
st.title("⚽ Football Grid Trivia")

if not st.session_state.game_started:
    st.subheader("Match Setup")
    with st.container(border=True):
        st.session_state.grid_size = st.slider("Grid Dimensions", 3, 5, 4)
        st.session_state.num_players = st.number_input("Number of Managers", 1, 4, 2)
        
        for i in range(st.session_state.num_players):
            st.session_state.p_names[i] = st.text_input(f"Manager {i+1} Name", placeholder=f"Manager {i+1}")
    
    if st.button("🚀 KICK OFF", use_container_width=True):
        # Generate Grid
        grid = []
        total_sq = st.session_state.grid_size**2
        for i in range(total_sq):
            if i == 0: grid.append({"task": "START"})
            elif i == (total_sq - 1): grid.append({"task": "FINISH"})
            else:
                # Example Logic: Randomize some common pairs
                pairs = [("Inter Milan", "Chelsea"), ("Man Utd", "Real Madrid"), ("Liverpool", "Chelsea"), ("Arsenal", "Man City")]
                p1, p2 = random.choice(pairs)
                grid.append({"task": f"Name a player who played for both {p1} & {p2}"})
        
        st.session_state.grid_map = grid
        st.session_state.player_data = {
            i: {"pos": 0, "name": st.session_state.p_names[i] or f"Manager {i+1}", "color": ["#FF4B4B", "#1C83E1", "#00C04A", "#FFD700"][i]} 
            for i in range(st.session_state.num_players)
        }
        st.session_state.game_started = True
        st.rerun()

else:
    # --- GAMEPLAY SCREEN ---
    curr_idx = st.session_state.turn
    player = st.session_state.player_data[curr_idx]
    
    # Render Grid Visuals
    cols = st.columns(st.session_state.grid_size)
    for i, box in enumerate(st.session_state.grid_map):
        with cols[i % st.session_state.grid_size]:
            # Highlight active square
            border_style = f"3px solid {player['color']}" if i == player['pos'] else "1px solid #333"
            st.markdown(
                f"<div style='border:{border_style}; padding:10px; border-radius:8px; height:100px; background:#1e2129; overflow:hidden;'>"
                f"<small style='color:#555;'>#{i}</small><br>"
                f"<p style='font-size:0.8rem; line-height:1.2;'>{box['task']}</p></div>", 
                unsafe_allow_html=True
            )

    # Sidebar Dashboard
    with st.sidebar:
        st.markdown(f"### 🏟️ {player['name']}'s Turn")
        
        if not st.session_state.rolled:
            if st.button("🎲 Roll Dice", use_container_width=True, type="primary"):
                roll = random.randint(1, 3)
                st.toast(f"You rolled a {roll}!")
                player['pos'] = min(player['pos'] + roll, len(st.session_state.grid_map)-1)
                st.session_state.rolled = True
                st.rerun()
        else:
            task = st.session_state.grid_map[player['pos']]['task']
            st.info(f"**Task:** {task}")
            
            # Show Answers for Task Squares
            if "both" in task.lower():
                ans_list = get_online_answers(task)
                with st.expander(f"👁️ Show Solutions ({len(ans_list)} correct)"):
                    if ans_list:
                        st.write(", ".join(ans_list))
                    else:
                        st.write("No direct matches found in our quick-lookup database.")

            if st.button("✅ Confirm Success", use_container_width=True):
                st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players
                st.session_state.rolled = False
                st.rerun()
                
            if st.button("❌ Fail / Reset Turn", use_container_width=True):
                st.session_state.rolled = False
                st.rerun()

        if st.button("🔄 Reset Game"):
            st.session_state.clear()
            st.rerun()
