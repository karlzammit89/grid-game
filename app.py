import streamlit as st
import random
import re
import pandas as pd

# --- 1. DATA MAPPING ---
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
    "Croatian": "hr", "Swiss": "ch", "Danish": "dk", "Turkish": "tr",
    "Austrian": "at", "Ukrainian": "ua", "Scottish": "gb-sct", "Swedish": "se",
    "Welsh": "gb-wls", "Polish": "pl", "Norwegian": "no", "Argentinian": "ar",
    "Brazilian": "br", "Colombian": "co", "Uruguayan": "uy", "Ecuadorian": "ec",
    "Moroccan": "ma", "Senegalese": "sn", "Nigerian": "ng", "Egyptian": "eg",
    "Ivorian": "ci", "Algerian": "dz", "American": "us", "Mexican": "mx",
    "Canadian": "ca", "Japanese": "jp", "South Korean": "kr", "Australian": "au"
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

KIT_COLOR_MAP = {
    "Red": "🔴", "Blue": "🔵", "White": "⚪", "Yellow": "🟡", "Green": "🟢", "Black": "⚫"
}

# --- STATIC ANSWER FALLBACKS (For when APIs don't exist for specific trivia) ---
STATIC_ANSWERS = {
    "stadium": {
        "England": ["Wembley", "Old Trafford", "Anfield", "Emirates", "St James' Park"],
        "Spain": ["Santiago Bernabéu", "Camp Nou", "Metropolitano", "Mestalla"],
        "Germany": ["Allianz Arena", "Signal Iduna Park", "Olympiastadion"],
        "Italy": ["San Siro", "Stadio Olimpico", "Juventus Stadium"]
    },
    "kit": {
        "Red": ["Liverpool", "Man Utd", "Arsenal", "Bayern Munich", "Benfica"],
        "Blue": ["Chelsea", "Man City", "Napoli", "Inter Milan", "Everton"],
        "Yellow": ["Dortmund", "Villarreal", "Watford", "Al-Nassr"],
        "White": ["Real Madrid", "Tottenham", "Leeds", "Valencia"]
    }
}

STAT_THRESHOLDS = {
    "Goals": {"Global": [100, 200], "CL": [20, 30], "League": [50, 75]},
    "Assists": {"Global": [50, 100], "League": [25, 50]},
    "Clean Sheets": {"Global": [50, 100], "League": [30, 50]},
    "Bookings": {"Global": [40, 70, 100]}
}

TROPHY_WINNERS = {
    "Euros": ["French", "Spanish", "Portuguese", "German", "Italian", "Dutch", "Danish"],
    "Copa America": ["Argentinian", "Brazilian", "Uruguayan", "Colombian"],
    "World Cup": ["French", "Spanish", "German", "Italian", "Argentinian", "Brazilian", "English", "Uruguayan"]
}

EUROPEANS = [k for k, v in COUNTRY_DATA.items() if v in ["fr", "es", "gb-eng", "pt", "nl", "be", "de", "it", "hr", "ch", "dk", "tr", "at", "ua", "gb-sct", "se", "gb-wls", "pl", "no"]]
SOUTH_AMERICANS = ["Argentinian", "Brazilian", "Colombian", "Uruguayan", "Ecuadorian"]

# --- 2. ENGINES ---

@st.cache_data(show_spinner=False)
def fetch_shared_players(club1, club2):
    id1, id2 = CLUB_IDS.get(club1), CLUB_IDS.get(club2)
    if not id1 or not id2: return []
    try:
        url = f"https://fbref.com/en/friv/players-who-played-for-multiple-clubs-countries.fcgi?t1={id1}&t2={id2}"
        tables = pd.read_html(url, storage_options={'User-Agent': 'Mozilla/5.0'})
        if tables: return tables[0]['Player'].dropna().unique().tolist()
    except: return []
    return []

def get_answer_logic(task_text):
    """The central engine to find answers based on the task string."""
    t_lower = task_text.lower()
    
    # 1. Connection Logic (API - Web Scraping)
    if "both" in t_lower:
        match = re.search(r"both (.*?) & (.*)", task_text)
        if match:
            c1, c2 = match.group(1).strip(), match.group(2).strip()
            shared = fetch_shared_players(c1, c2)
            return f"**Examples:** {', '.join(shared[:12])}" if shared else "No quick data found."

    # 2. Stadium Logic
    if "stadium" in t_lower:
        for country, stadiums in STATIC_ANSWERS["stadium"].items():
            if country.lower() in t_lower:
                return f"**{country} Stadiums:** {', '.join(stadiums)}"

    # 3. Kit Color Logic
    if "kit color" in t_lower:
        for color, teams in STATIC_ANSWERS["kit"].items():
            if color.lower() in t_lower:
                return f"**{color} Teams:** {', '.join(teams)}"

    # 4. Trophy Winners
    if "won" in t_lower:
        # Dynamic check for trophies from dictionary
        for trophy, winner_nations in TROPHY_WINNERS.items():
            if trophy.lower() in t_lower:
                return f"**Winning Nations:** {', '.join(winner_nations[:8])}"

    return "Check the search link below for full details!"

def grid_text_formatter(text):
    text = text.replace("Name a football team whose", "Football teams whose")
    text = re.sub(r"Name a[n]? (\w+) player", r"\1 players", text)
    text = re.sub(r"Name a player", "Players", text)
    text = re.sub(r"Name a team", "Teams", text)
    text = re.sub(r"Name a stadium", "Stadiums", text)
    text = re.sub(r"Name a manager", "Managers", text)
    return text

def smart_pluralize(text, count):
    if count <= 1: return text
    text = text.replace("Name a football team whose", f"Name {count} football teams whose")
    text = re.sub(r"Name a[n]? (\w+) player", f"Name {count} \\1 players", text)
    text = re.sub(r"Name a player", f"Name {count} players", text)
    text = re.sub(r"Name a team", f"Name {count} teams", text)
    return text

def articulate_task(subject_type, target, action="played for"):
    clean_target = target.replace("Name a player who ", "").replace("won ", "").replace("has won ", "").replace("the ", "")
    article = "an" if subject_type[0].lower() in ['a', 'e', 'i', 'o', 'u'] else "a"
    needs_the = ["Premier League", "Champions League", "World Cup", "Euros", "La Liga", "Serie A"]
    final_target = f"the {clean_target}" if clean_target in needs_the else clean_target
    if subject_type == "player":
        return f"Name a player who {action} {final_target}"
    return f"Name {article} {subject_type} player who {action} {final_target}"

def get_assets(text):
    assets = {"logos": [], "flags": [], "emojis": []}
    clean_text = re.sub(r'[^\w\s]', '', text).lower()
    if "won" in clean_text: assets["emojis"].append("🏆")
    if "goals" in clean_text: assets["emojis"].append("🥅")
    for nation, iso in COUNTRY_DATA.items():
        if nation.lower() in clean_text:
            assets["flags"].append(f"https://flagcdn.com/w40/{iso}.png")
    for club, eid in ESPN_LOGOS.items():
        if club.lower() in clean_text:
            assets["logos"].append(f"https://a.espncdn.com/i/teamlogos/soccer/500/{eid}.png")
    return assets

def format_header_icons(assets, size_logos="24px", size_emojis="22px"):
    html = '<div style="display: flex; gap: 6px; justify-content: center; align-items: center; min-height: 25px; margin: 8px 0;">'
    for e in assets["emojis"]: html += f'<span style="font-size:{size_emojis};">{e}</span>'
    for f in assets["flags"][:2]: html += f'<img src="{f}" style="height:14px; border:1px solid #444;">'
    for l in assets["logos"][:2]: html += f'<img src="{l}" style="height:{size_logos};">'
    if not any(assets.values()): html += '⚽'
    return html + '</div>'

# --- 3. DYNAMIC LOGIC ---
def generate_random_task(categories):
    clubs_list = list(ESPN_LOGOS.keys())
    pool = []
    if "Club Connections" in categories: pool.extend([1, 2])
    if "Stadiums" in categories: pool.append(4)
    if "Kits" in categories: pool.append(5)
    if "Trophies" in categories: pool.extend([6, 7])
    
    if not pool: return "N/A"
    tt = random.choice(pool)
    
    if tt == 1: 
        pair = random.sample(clubs_list, 2)
        return f"Name a player who played for both {pair[0]} & {pair[1]}"
    elif tt == 2:
        return articulate_task(random.choice(['Brazilian', 'French', 'Spanish']), random.choice(clubs_list))
    elif tt == 4:
        return f"Name a stadium located in {random.choice(list(STADIUM_COUNTRIES.keys()))}"
    elif tt == 5:
        return f"Name a football team whose primary home kit color is {random.choice(list(KIT_COLOR_MAP.keys()))}"
    elif tt == 6:
        return f"Name a team that has won the {random.choice(['Champions League', 'World Cup', 'Premier League'])}"
    else:
        return f"Name a player who has won the World Cup"

# --- 4. STATE MANAGEMENT ---
def reset_all_data():
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()

if 'game_started' not in st.session_state:
    st.session_state.update({
        'game_started': False, 'grid_size': 4, 'num_players': 2, 'player_names': [], 
        'player_data': {}, 'turn': 0, 'rolled': False, 'current_roll': 0, 
        'grid_map': [], 'confirm_reset': False, 'winner': None, 'active_final_task': None,
        'selected_categories': ["Club Connections", "Trophies", "Stadiums", "Kits"]
    })

def start_game():
    total_sq = st.session_state.grid_size ** 2
    board = [{"task": "KICK OFF", "assets": {"flags":[], "logos":[], "emojis":["🏁"]}}]
    for _ in range(total_sq - 2):
        task_text = generate_random_task(st.session_state.selected_categories)
        board.append({"task": task_text, "assets": get_assets(task_text)})
    board.append({"task": "FINAL WHISTLE", "assets": {"flags":[], "logos":[], "emojis":["🥇"]}})
    st.session_state.grid_map = board
    st.session_state.player_data = {
        i: {"pos": 0, "prev": 0, "name": st.session_state.player_names[i] or f"Manager {i+1}",
            "initials": (st.session_state.player_names[i][:2] if st.session_state.player_names[i] else f"M{i+1}").upper(),
            "color": ["#FF4B4B", "#1C83E1", "#00C04A", "#FFD700"][i]} for i in range(st.session_state.num_players)
    }
    st.session_state.game_started = True

# --- 5. UI ---
st.set_page_config(page_title="Football Path Trivia", layout="wide")

if st.session_state.winner:
    st.balloons()
    st.title(f"🏆 {st.session_state.winner['name']} Wins!")
    if st.button("Return to Menu"): reset_all_data()

elif not st.session_state.game_started:
    st.title("⚽ Football Grid Setup")
    st.session_state.grid_size = st.slider("Grid Size", 3, 6, 4)
    st.session_state.num_players = st.slider("Players", 1, 4, 2)
    st.session_state.selected_categories = st.multiselect("Categories", ["Club Connections", "Trophies", "Stadiums", "Kits"], default=["Club Connections", "Trophies"])
    st.session_state.player_names = [st.text_input(f"Manager {i+1}", key=f"p{i}") for i in range(st.session_state.num_players)]
    if st.button("🚀 START MATCH"): 
        start_game()
        st.rerun()

else:
    player = st.session_state.player_data[st.session_state.turn]
    
    # Render Grid
    st.markdown(f"""<style>
        .grid-container {{ display: grid; gap: 10px; grid-template-columns: repeat({st.session_state.grid_size}, 1fr); }}
        .grid-item {{ background: #1e2129; border: 1px solid #333; border-radius: 12px; padding: 10px; text-align: center; min-height: 120px; }}
        .active-sq {{ border: 3px solid {player['color']}; box-shadow: 0 0 10px {player['color']}55; }}
    </style>""", unsafe_allow_html=True)

    grid_html = '<div class="grid-container">'
    for i, item in enumerate(st.session_state.grid_map):
        active = "active-sq" if i == player['pos'] else ""
        grid_html += f'<div class="grid-item {active}">{format_header_icons(item["assets"])}<div style="font-size:0.8rem; color:#eee;">{grid_text_formatter(item["task"])}</div></div>'
    st.markdown(grid_html + "</div>", unsafe_allow_html=True)

    with st.sidebar:
        st.header(f"Turn: {player['name']}")
        if not st.session_state.rolled:
            if st.button("🎲 ROLL DICE", use_container_width=True):
                st.session_state.current_roll = random.randint(1, 3)
                player['prev'], player['pos'] = player['pos'], min(player['pos'] + st.session_state.current_roll, len(st.session_state.grid_map)-1)
                st.session_state.rolled = True; st.rerun()
        else:
            task_text = st.session_state.grid_map[player['pos']]['task']
            st.info(f"Task: {smart_pluralize(task_text, st.session_state.current_roll)}")
            
            c1, c2 = st.columns(2)
            if c1.button("✅ Success"):
                if player['pos'] == len(st.session_state.grid_map)-1: st.session_state.winner = player
                else: st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players; st.session_state.rolled = False
                st.rerun()
            if c2.button("❌ Fail"):
                player['pos'] = player['prev']
                st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players; st.session_state.rolled = False
                st.rerun()

            # --- API & ANSWER LOGIC IN EXPANDER ---
            with st.expander("👁️ View Answers"):
                st.markdown(get_answer_logic(task_text))
                
                search_q = task_text.replace("Name a", "").strip()
                google_url = f"https://www.google.com/search?q=football+{search_q.replace(' ', '+')}"
                st.markdown(f"[🔍 Search for more answers]({google_url})")

        if st.button("🚩 Reset Game"): reset_all_data()
