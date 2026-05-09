import streamlit as st
import random
import re
import pandas as pd

# --- 1. DATA MAPPING (IDs added for lookup) ---
# Added IDs for FBref lookup to ensure the search works
CLUB_IDS = {
    "Man Utd": "19538871", "Liverpool": "822bd0ba", "Arsenal": "18bb7c10", 
    "Chelsea": "cff3d3bb", "Man City": "b8fd03ef", "Tottenham": "3ad23a75",
    "Aston Villa": "860223d1", "Newcastle": "b1b71fcb", "Real Madrid": "5324c30a", 
    "Barcelona": "206d9d25", "Atletico Madrid": "db3b5483", "Sevilla": "ad2be748",
    "AC Milan": "e2d42690", "Juventus": "e2d42690", "Inter Milan": "d60ad303",
    "Bayern Munich": "054fdde2", "PSG": "e2d8892c"
}

COUNTRY_DATA = {
    "French": "fr", "Spanish": "es", "English": "gb-eng", "Portuguese": "pt",
    "Dutch": "nl", "Belgian": "be", "German": "de", "Italian": "it",
    "Brazilian": "br", "Argentinian": "ar"
}

ESPN_LOGOS = {
    "Man Utd": "360", "Liverpool": "364", "Arsenal": "359", 
    "Chelsea": "363", "Man City": "382", "Tottenham": "367",
    "Aston Villa": "362", "Newcastle": "361", "Real Madrid": "86", "Barcelona": "83", 
    "Atletico Madrid": "1068", "Sevilla": "243", "Villarreal": "102", "AC Milan": "103", 
    "Juventus": "111", "Inter Milan": "110", "AS Roma": "104", "Napoli": "114", 
    "Bayern Munich": "132", "Dortmund": "124", "Leverkusen": "131", "PSG": "160", 
    "Marseille": "176", "Monaco": "174", "Ajax": "139", "PSV Eindhoven": "148", 
    "Feyenoord": "142", "Benfica": "1929", "Porto": "437", "Sporting CP": "2250"
}

STADIUM_COUNTRIES = {"England": "gb-eng", "Spain": "es", "Germany": "de", "Italy": "it", "France": "fr", "Portugal": "pt", "Brazil": "br", "Argentina": "ar", "Mexico": "mx"}
KIT_COLOR_MAP = {"Red": "🔴", "Blue": "🔵", "White": "⚪", "Yellow": "🟡", "Green": "🟢", "Black": "⚫"}

# --- 2. LIVE ANSWER ENGINE ---
@st.cache_data(show_spinner=False)
def fetch_shared_players(club1, club2):
    id1, id2 = CLUB_IDS.get(club1), CLUB_IDS.get(club2)
    if not id1 or not id2: return []
    try:
        url = f"https://fbref.com/en/friv/players-who-played-for-multiple-clubs-countries.fcgi?t1={id1}&t2={id2}"
        storage_options = {'User-Agent': 'Mozilla/5.0'}
        tables = pd.read_html(url, storage_options=storage_options)
        if tables:
            return tables[0]['Player'].dropna().unique().tolist()
    except: return []
    return []

# --- 3. GRAMMAR & ASSET ENGINES ---
def grid_text_formatter(text):
    text = text.replace("Name a football team whose", "Football teams whose")
    text = re.sub(r"Name a[n]? (\w+) player", r"\1 players", text)
    text = re.sub(r"Name a player", "Players", text)
    text = re.sub(r"Name a team", "Teams", text)
    text = re.sub(r"Name a stadium", "Stadiums", text)
    text = re.sub(r"Name a manager", "Managers", text)
    text = text.replace("players who has", "players who have").replace("Players who has", "Players who have")
    return text

def smart_pluralize(text, count):
    if count <= 1: return text
    text = text.replace("Name a football team whose", f"Name {count} football teams whose")
    text = re.sub(r"Name a[n]? (\w+) player", f"Name {count} \\1 players", text)
    text = re.sub(r"Name a player", f"Name {count} players", text)
    text = re.sub(r"Name a team", f"Name {count} teams", text)
    return text

def get_assets(text):
    assets = {"logos": [], "flags": [], "emojis": []}
    clean_text = re.sub(r'[^\w\s]', '', text).lower()
    if "won" in clean_text: assets["emojis"].append("🏆")
    for nation, iso in COUNTRY_DATA.items():
        if nation.lower() in clean_text:
            assets["flags"].append(f"https://flagcdn.com/w40/{iso}.png")
    for club, eid in ESPN_LOGOS.items():
        if club.lower() in clean_text:
            assets["logos"].append(f"https://a.espncdn.com/i/teamlogos/soccer/500/{eid}.png")
    return assets

def format_header_icons(assets, size_logos="24px", size_emojis="22px"):
    html = '<div style="display: flex; gap: 6px; justify-content: center; align-items: center; min-height: 25px; margin: 8px 0;">'
    for e in list(dict.fromkeys(assets["emojis"])): html += f'<span style="font-size:{size_emojis};">{e}</span>'
    for f in assets["flags"]: html += f'<img src="{f}" style="height:14px; border-radius:2px;">'
    for l in assets["logos"]: html += f'<img src="{l}" style="height:{size_logos};">'
    return html + '</div>'

# --- 4. DYNAMIC LOGIC ---
def generate_random_task(categories):
    clubs_list = list(CLUB_IDS.keys()) # Use keys from CLUB_IDS for better lookup compatibility
    pool = [1, 1, 1, 2, 5, 6] # Weighted toward club connections
    template_type = random.choice(pool)
    if template_type == 1: 
        pair = random.sample(clubs_list, 2)
        return f"Name a player who played for both {pair[0]} & {pair[1]}"
    elif template_type == 2:
        n = random.choice(['Brazilian', 'French', 'Spanish'])
        return f"Name a {n} player who played for {random.choice(clubs_list)}"
    elif template_type == 5:
        return f"Name a football team whose primary home kit color is {random.choice(list(KIT_COLOR_MAP.keys()))}"
    else:
        return f"Name a team that has won the {random.choice(['Champions League', 'Premier League', 'World Cup'])}"

# --- 5. STATE MANAGEMENT ---
def reset_all_data():
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()

if 'game_started' not in st.session_state:
    st.session_state.update({
        'game_started': False, 'grid_size': 4, 'num_players': 2, 'player_names': [], 
        'player_data': {}, 'turn': 0, 'rolled': False, 'current_roll': 0, 
        'grid_map': [], 'confirm_reset': False, 'winner': None,
        'selected_categories': ["Club Connections", "Trophies", "Kits"]
    })

def start_game():
    total_sq = st.session_state.grid_size ** 2
    board = [{"task": "KICK OFF", "assets": {"flags":[], "logos":[], "emojis":["🏁"]}}]
    for _ in range(total_sq - 2):
        t = generate_random_task(st.session_state.selected_categories)
        board.append({"task": t, "assets": get_assets(t)})
    board.append({"task": "FINAL WHISTLE", "assets": {"flags":[], "logos":[], "emojis":["🥇"]}})
    st.session_state.grid_map = board
    st.session_state.player_data = {
        i: {"pos": 0, "prev": 0, "name": st.session_state.player_names[i] or f"Manager {i+1}",
            "initials": (st.session_state.player_names[i][:2] if st.session_state.player_names[i] else f"M{i+1}").upper(),
            "color": ["#FF4B4B", "#1C83E1", "#00C04A", "#FFD700"][i]} for i in range(st.session_state.num_players)
    }
    st.session_state.game_started = True

# --- 6. UI ---
st.set_page_config(page_title="Football Path Trivia", layout="wide")

if st.session_state.winner:
    st.balloons()
    st.title(f"🎉 {st.session_state.winner['name']} Wins!")
    if st.button("Return to Menu"): reset_all_data()

elif not st.session_state.game_started:
    st.title("⚽ Football Grid Setup")
    st.session_state.grid_size = st.number_input("Grid Size", 3, 6, 4)
    st.session_state.num_players = st.number_input("Players", 1, 4, 2)
    st.session_state.player_names = [st.text_input(f"Manager {i+1}", key=f"p{i}") for i in range(st.session_state.num_players)]
    if st.button("🚀 START MATCH"): start_game(); st.rerun()

else:
    player = st.session_state.player_data[st.session_state.turn]
    
    # CSS
    st.markdown(f"""<style>
        .grid-container {{ display: grid; gap: 10px; grid-template-columns: repeat({st.session_state.grid_size}, 1fr); }}
        .grid-item {{ background: #1e2129; border: 1px solid #333; border-radius: 8px; padding: 10px; text-align: center; min-height: 120px; }}
        .active-sq {{ border: 2px solid {player['color']}; box-shadow: 0 0 10px {player['color']}55; }}
        .p-tag {{ border-radius: 50%; width: 22px; height: 22px; display: inline-flex; align-items: center; justify-content: center; font-size: 0.6rem; font-weight: bold; margin: 1px; color: white; }}
        </style>""", unsafe_allow_html=True)

    # Render Grid
    grid_html = '<div class="grid-container">'
    for i, item in enumerate(st.session_state.grid_map):
        active = "active-sq" if i == player['pos'] else ""
        marks = "".join([f'<span class="p-tag" style="background:{p["color"]}">{p["initials"]}</span>' for pid, p in st.session_state.player_data.items() if p['pos'] == i])
        grid_html += f'<div class="grid-item {active}">{format_header_icons(item["assets"])}<div style="font-size:0.8rem;">{grid_text_formatter(item["task"])}</div><div>{marks}</div></div>'
    st.markdown(grid_html + "</div>", unsafe_allow_html=True)

    # Sidebar turn control
    with st.sidebar:
        st.header(f"Turn: {player['name']}")
        if not st.session_state.rolled:
            if st.button("🎲 ROLL DICE", use_container_width=True, type="primary"):
                st.session_state.current_roll = random.randint(1, 3)
                player['prev'], player['pos'] = player['pos'], min(player['pos'] + st.session_state.current_roll, len(st.session_state.grid_map)-1)
                st.session_state.rolled = True; st.rerun()
        else:
            task = st.session_state.grid_map[player['pos']]['task']
            st.info(smart_pluralize(task, st.session_state.current_roll))
            
            # --- LIVE ANSWERS DROPDOWN ---
            if "both" in task.lower():
                match = re.search(r"both (.*?) & (.*)", task)
                if match:
                    c1, c2 = match.group(1), match.group(2)
                    answers = fetch_shared_players(c1, c2)
                    with st.expander(f"👁️ Possible Answers ({len(answers)})"):
                        if answers: st.write(", ".join(answers))
                        else: st.write("No players found in database.")
            
            c1, c2 = st.columns(2)
            if c1.button("✅ Success", use_container_width=True):
                if player['pos'] == len(st.session_state.grid_map)-1: st.session_state.winner = player
                else: 
                    st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players
                    st.session_state.rolled = False
                st.rerun()
            if c2.button("❌ Fail", use_container_width=True):
                player['pos'] = player['prev']
                st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players
                st.session_state.rolled = False
                st.rerun()
