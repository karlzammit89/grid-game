import streamlit as st
import random
import re

# --- 1. DATA MAPPING (Flags & Domains) ---
COUNTRY_DATA = {
    "Spanish": "es", "Spain": "es", "English": "gb-eng", "England": "gb-eng",
    "Italian": "it", "Italy": "it", "German": "de", "Germany": "de",
    "French": "fr", "France": "fr", "Portuguese": "pt", "Portugal": "pt",
    "Dutch": "nl", "Netherlands": "nl", "Brazilian": "br", "Brazil": "br",
    "Argentinian": "ar", "Argentina": "ar"
}

# Mapping club names to official domains for the Logo API
# This is more stable than internal IDs which often change
CLUB_DOMAINS = {
    "Real Madrid": "realmadrid.com", "Barcelona": "fcbarcelona.com",
    "Man Utd": "manutd.com", "Manchester United": "manutd.com",
    "Liverpool": "liverpoolfc.com", "Bayern Munich": "fcbayern.com",
    "AC Milan": "acmilan.com", "Juventus": "juventus.com",
    "Chelsea": "chelseafc.com", "Inter Milan": "inter.it",
    "PSG": "psg.fr", "Arsenal": "arsenal.com", "Man City": "mancity.com"
}

def get_club_logo(text):
    """Fetches high-res logos using Hunter.io (reliable 2026 alternative)."""
    logo_html = ""
    for club, domain in CLUB_DOMAINS.items():
        if club.lower() in text.lower():
            # Zero-signup API that works with direct embedding
            url = f"https://hunter.io/api/logo/{domain}"
            logo_html += f'<img src="{url}" style="height:22px; vertical-align:middle; margin-right:6px;">'
    return logo_html

def clean_text_and_add_assets(text):
    """Applies your UI logic with working assets."""
    clean_text = re.sub(r'[^\x00-\x7F]+', '', text).strip()
    
    # Flags logic (using FlagCDN)
    flag_html = ""
    for word, iso in COUNTRY_DATA.items():
        if word.lower() in clean_text.lower():
            flag_url = f"https://flagcdn.com/w40/{iso}.png"
            flag_html = f'<img src="{flag_url}" style="height:14px; vertical-align:middle; margin-left:6px; border-radius:2px; border:1px solid #444;">'
            break
            
    # Working Logo logic
    logo_html = get_club_logo(clean_text)
    
    return f"{logo_html}{clean_text}{flag_html}"

# --- 2. LOGIC GENERATORS ---
def generate_final_challenge():
    big_clubs = list(CLUB_DOMAINS.keys())
    nations = ["Brazil", "France", "Spain", "Germany", "Argentina", "Portugal", "Italy", "Netherlands", "England"]
    leagues = ["Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1"]
    
    templates = [
        lambda: f"Name 3 players who played for both {random.choice(big_clubs)} and {random.choice(big_clubs)}.",
        lambda: f"Name 4 {random.choice(nations)}n players who won the {random.choice(leagues)}.",
        lambda: f"Name 3 stadiums located in {random.choice(['London', 'Madrid', 'Manchester', 'Paris'])}.",
    ]
    return clean_text_and_add_assets(random.choice(templates)())

CRITERIA_POOL = [
    "Name a player who played for both Real Madrid & AC Milan",
    "Name a Brazilian player who has won the Premier League",
    "Name any player to have played for both Liverpool & Chelsea",
    "Name a French player currently playing in the Bundesliga",
    "Name a Spanish player who has played in the Premier League",
    "Name a player who played for both Manchester United & Arsenal",
    "Name a Dutch player who has played for Barcelona",
    "Name a Portuguese player who has played for Real Madrid"
]

# --- 3. STATE REFRESH LOGIC ---
def reset_all_data():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

if 'game_started' not in st.session_state:
    st.session_state.update({
        'game_started': False, 'grid_size': 3,
        'num_players': 2, 'player_names': [], 'player_data': {},
        'turn': 0, 'rolled': False, 'current_roll': 0, 
        'grid_map': [], 'confirm_reset': False, 'winner': None,
        'active_final_task': None
    })

def start_game():
    total_sq = st.session_state.grid_size ** 2
    board = [{"task": "KICK OFF"}]
    selected_tasks = random.sample(CRITERIA_POOL, min(len(CRITERIA_POOL), total_sq - 2))
    for task in selected_tasks:
        board.append({"task": clean_text_and_add_assets(task)})
    board.append({"task": "FINAL WHISTLE"})
    st.session_state.grid_map = board
    st.session_state.player_data = {
        i: {
            "pos": 0, "prev": 0, 
            "name": st.session_state.player_names[i] or f"Manager {i+1}",
            "initials": (st.session_state.player_names[i][:2] if st.session_state.player_names[i] else f"M{i+1}").upper(),
            "color": ["#FF4B4B", "#1C83E1", "#00C04A", "#FFD700"][i]
        } for i in range(st.session_state.num_players)
    }
    st.session_state.game_started = True

# --- 4. REVERTED UI (Matches image_9ee060.png) ---
st.set_page_config(page_title="Football Path Trivia", layout="wide")

if st.session_state.winner:
    st.balloons()
    st.markdown(f'<h2 style="text-align:center;">🏆 {st.session_state.winner["name"]} Wins!</h2>', unsafe_allow_html=True)
    if st.button("🏟️ New Match", use_container_width=True): reset_all_data()

elif not st.session_state.game_started:
    st.title("⚽ Match Setup")
    st.session_state.grid_size = st.number_input("Grid Size", 3, 6, 3)
    st.session_state.num_players = st.number_input("Players", 1, 4, 2)
    st.session_state.player_names = [st.text_input(f"Manager {i+1}", key=f"p{i}") for i in range(st.session_state.num_players)]
    if st.button("🚀 START", use_container_width=True, type="primary"): start_game(); st.rerun()

else:
    player = st.session_state.player_data[st.session_state.turn]
    st.markdown(f"""
        <style>
        .grid-container {{ display: grid; gap: 10px; }}
        .grid-item {{ background: #1e2129; border: 1px solid #333; border-radius: 12px; padding: 12px; text-align: center; min-height: 160px; display: flex; flex-direction: column; align-items: center; justify-content: space-between; }}
        .active-sq {{ border: 2px solid #FF4B4B; }}
        .p-tag {{ border-radius: 50%; width: 26px; height: 26px; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: 800; border: 2px solid #fff; margin: 2px; }}
        </style>
    """, unsafe_allow_html=True)

    grid_cols = f"repeat({st.session_state.grid_size}, 1fr)"
    grid_html = f'<div class="grid-container" style="grid-template-columns: {grid_cols};">'
    for i, item in enumerate(st.session_state.grid_map):
        active = "active-sq" if i == player['pos'] else ""
        marks = "".join([f'<span class="p-tag" style="background:{p["color"]}">{p["initials"]}</span>' for pid, p in st.session_state.player_data.items() if p['pos'] == i])
        icon = "🏁" if i == 0 else "🏆" if i == len(st.session_state.grid_map)-1 else "⚽"
        grid_html += f'<div class="grid-item {active}"><div style="color:#555; width:100%; text-align:left; font-size:0.7rem;">#{i:02}</div><div>{icon}</div><div style="color:#eee; font-size:0.85rem; font-weight:600;">{item["task"]}</div><div style="display:flex;">{marks}</div></div>'
    st.markdown(grid_html + "</div>", unsafe_allow_html=True)

    with st.sidebar:
        st.header(f"Turn: {player['name']}")
        if not st.session_state.rolled:
            if st.button("🎲 ROLL", use_container_width=True, type="primary"):
                st.session_state.current_roll = random.randint(1, 3)
                player['prev'], player['pos'] = player['pos'], min(player['pos'] + st.session_state.current_roll, len(st.session_state.grid_map)-1)
                st.session_state.rolled = True
                st.rerun()
        else:
            st.write(f"You rolled a {st.session_state.current_roll}")
            if st.button("✅ Next Player"): 
                st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players
                st.session_state.rolled = False
                st.rerun()
