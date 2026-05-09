import streamlit as st
import random
import re
import pandas as pd

# --- 1. DATA & ANSWER DATABASE ---
# This provides instant answers for categories that don't change often.
ANSWER_BANK = {
    "stadium": {
        "England": ["Old Trafford", "Anfield", "Wembley", "Emirates", "St James' Park", "Etihad", "Villa Park"],
        "Spain": ["Santiago Bernabéu", "Camp Nou", "Metropolitano", "Mestalla", "San Mamés"],
        "Germany": ["Allianz Arena", "Signal Iduna Park", "Veltins-Arena", "Olympiastadion"],
        "Italy": ["San Siro", "Stadio Olimpico", "Juventus Stadium", "Stadio Diego Armando Maradona"],
        "France": ["Parc des Princes", "Stade Vélodrome", "Stade de France", "Groupama Stadium"],
        "Portugal": ["Estádio da Luz", "Estádio do Dragão", "Estádio José Alvalade"],
        "Brazil": ["Maracanã", "Allianz Parque", "Mineirão", "Morumbi"],
        "Argentina": ["La Bombonera", "El Monumental", "Cilindro de Avellaneda"],
        "Mexico": ["Estadio Azteca", "Estadio BBVA", "Estadio Akron"]
    },
    "kit": {
        "Red": ["Man Utd", "Liverpool", "Arsenal", "Bayern Munich", "AC Milan", "Benfica", "Ajax", "Sevilla"],
        "Blue": ["Chelsea", "Man City", "Everton", "Leicester", "Napoli", "Inter Milan", "PSG", "Porto", "Schalke"],
        "White": ["Real Madrid", "Tottenham", "Leeds", "Valencia", "Lyon", "Marseille", "Fulham"],
        "Yellow": ["Dortmund", "Villarreal", "Fenerbahce", "Watford", "Cadiz", "Al-Nassr"],
        "Green": ["Sporting CP", "Celtic", "Real Betis", "Sassuolo", "Palmeiras", "Wolfsburg"],
        "Black": ["Newcastle (Away)", "Juventus (Away)", "Frankfurt", "PAOK"]
    },
    "trophy_teams": {
        "Champions League": ["Real Madrid", "AC Milan", "Liverpool", "Bayern Munich", "Barcelona", "Man City", "Inter Milan"],
        "Premier League": ["Man Utd", "Man City", "Chelsea", "Arsenal", "Liverpool", "Leicester", "Blackburn"],
        "World Cup": ["Argentina", "France", "Germany", "Brazil", "Italy", "Spain", "England", "Uruguay"],
        "La Liga": ["Real Madrid", "Barcelona", "Atletico Madrid", "Valencia", "Sevilla", "Real Sociedad"],
        "Serie A": ["Juventus", "Inter Milan", "AC Milan", "Napoli", "AS Roma", "Lazio"]
    }
}

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
    "Argentinian": "ar", "Brazilian": "br"
}

# --- 2. ENGINES & LOGIC ---

@st.cache_data(show_spinner=False)
def fetch_shared_players(club1, club2):
    """Scrapes FBref for players shared between two clubs."""
    id1, id2 = CLUB_IDS.get(club1), CLUB_IDS.get(club2)
    if not id1 or not id2: return []
    try:
        url = f"https://fbref.com/en/friv/players-who-played-for-multiple-clubs-countries.fcgi?t1={id1}&t2={id2}"
        tables = pd.read_html(url, storage_options={'User-Agent': 'Mozilla/5.0'})
        if tables: return tables[0]['Player'].dropna().unique().tolist()
    except: return []
    return []

def get_answer_logic(task_text):
    """Determines which answer to show in the dropdown."""
    task_lower = task_text.lower()
    
    # 1. Check Club Connections
    if "both" in task_lower:
        match = re.search(r"both (.*?) & (.*)", task_text)
        if match:
            c1, c2 = match.group(1).strip(), match.group(2).strip()
            shared = fetch_shared_players(c1, c2)
            if shared: return f"**Common Players:** {', '.join(shared[:12])}"
    
    # 2. Check Stadiums
    if "stadium" in task_lower:
        for country, stadiums in ANSWER_BANK["stadium"].items():
            if country.lower() in task_lower:
                return f"**Stadiums in {country}:** {', '.join(stadiums)}"
                
    # 3. Check Kit Colors
    if "kit color" in task_lower:
        for color, teams in ANSWER_BANK["kit"].items():
            if color.lower() in task_lower:
                return f"**Teams with {color} Kits:** {', '.join(teams)}"
                
    # 4. Check Trophy Winners
    if "won" in task_lower:
        for trophy, winners in ANSWER_BANK["trophy_teams"].items():
            if trophy.lower() in task_lower:
                return f"**Previous {trophy} Winners:** {', '.join(winners)}"
            
    return "No instant list available. Verify using the Google link below."

def generate_random_task():
    """Generates tasks for the grid."""
    clubs = list(CLUB_IDS.keys())
    types = ["connection", "stadium", "kit", "trophy"]
    choice = random.choice(types)
    
    if choice == "connection":
        pair = random.sample(clubs, 2)
        return f"Name a player who played for both {pair[0]} & {pair[1]}"
    elif choice == "stadium":
        country = random.choice(list(ANSWER_BANK["stadium"].keys()))
        return f"Name a stadium located in {country}"
    elif choice == "kit":
        color = random.choice(list(ANSWER_BANK["kit"].keys()))
        return f"Name a football team whose primary home kit color is {color}"
    else:
        trophy = random.choice(list(ANSWER_BANK["trophy_teams"].keys()))
        return f"Name a team that has won the {trophy}"

# --- 3. STATE MANAGEMENT ---

if 'game_started' not in st.session_state:
    st.session_state.update({
        'game_started': False, 'grid_size': 4, 'num_players': 2,
        'player_names': [], 'player_data': {}, 'turn': 0,
        'rolled': False, 'current_roll': 0, 'grid_map': [],
        'winner': None
    })

def reset_game():
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()

# --- 4. MAIN UI ---

st.set_page_config(page_title="Football Path Trivia", layout="wide")

if not st.session_state.game_started:
    st.title("⚽ Football Path Setup")
    c1, c2 = st.columns(2)
    st.session_state.grid_size = c1.number_input("Grid Size (3-6)", 3, 6, 4)
    st.session_state.num_players = c2.number_input("Players (1-4)", 1, 4, 2)
    
    if st.button("🚀 Start Match", use_container_width=True):
        # Build Grid
        total_sq = st.session_state.grid_size ** 2
        board = [{"task": "KICK OFF"}]
        for _ in range(total_sq - 2):
            board.append({"task": generate_random_task()})
        board.append({"task": "FINAL WHISTLE"})
        
        st.session_state.grid_map = board
        st.session_state.player_data = {
            i: {"name": f"Manager {i+1}", "pos": 0, "prev": 0, "color": ["#FF4B4B", "#1C83E1", "#00C04A", "#FFD700"][i]}
            for i in range(st.session_state.num_players)
        }
        st.session_state.game_started = True
        st.rerun()

elif st.session_state.winner:
    st.balloons()
    st.success(f"🏆 {st.session_state.winner['name']} Wins!")
    if st.button("Restart"): reset_game()

else:
    # --- GAME BOARD ---
    player = st.session_state.player_data[st.session_state.turn]
    
    # CSS for Grid
    st.markdown(f"""<style>
        .grid-container {{ display: grid; gap: 10px; grid-template-columns: repeat({st.session_state.grid_size}, 1fr); }}
        .grid-item {{ background: #262730; border: 1px solid #444; border-radius: 8px; padding: 15px; text-align: center; min-height: 100px; color: white; }}
        .active-sq {{ border: 3px solid {player['color']}; box-shadow: 0 0 10px {player['color']}; }}
    </style>""", unsafe_allow_html=True)

    grid_html = '<div class="grid-container">'
    for i, sq in enumerate(st.session_state.grid_map):
        is_active = "active-sq" if i == player['pos'] else ""
        grid_html += f'<div class="grid-item {is_active}">{sq["task"]}</div>'
    st.markdown(grid_html + "</div>", unsafe_allow_html=True)

    # --- SIDEBAR CONTROLS ---
    with st.sidebar:
        st.title(f"Turn: {player['name']}")
        
        if not st.session_state.rolled:
            if st.button("🎲 Roll Dice", use_container_width=True):
                st.session_state.current_roll = random.randint(1, 3)
                player['prev'] = player['pos']
                player['pos'] = min(player['pos'] + st.session_state.current_roll, len(st.session_state.grid_map)-1)
                st.session_state.rolled = True
                st.rerun()
        else:
            # Current Task Definition
            task_text = st.session_state.grid_map[player['pos']]['task']
            
            st.markdown(f"### 📍 Square #{player['pos']}")
            st.info(f"**{task_text}**")
            
            c1, c2 = st.columns(2)
            if c1.button("✅ Success", use_container_width=True):
                if player['pos'] == len(st.session_state.grid_map) - 1:
                    st.session_state.winner = player
                else:
                    st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players
                    st.session_state.rolled = False
                st.rerun()
                
            if c2.button("❌ Fail", use_container_width=True):
                player['pos'] = player['prev']
                st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players
                st.session_state.rolled = False
                st.rerun()

            st.write("---")
            
            # --- VIEW ANSWERS SECTION ---
            with st.expander("👁️ View Answers"):
                # Run the answer engine
                ans_result = get_answer_logic(task_text)
                st.markdown(ans_result)
                
                # Verification Link
                clean_q = task_text.replace("Name a", "").strip()
                google_url = f"https://www.google.com/search?q=football+{clean_q.replace(' ', '+')}"
                st.markdown(f"""
                <a href="{google_url}" target="_blank" style="text-decoration:none;">
                    <div style="background:#444; color:white; padding:10px; border-radius:5px; text-align:center; font-size:0.9rem;">
                        🔍 Verify on Google
                    </div>
                </a>
                """, unsafe_allow_html=True)

        if st.button("🚩 Reset Game", use_container_width=True): reset_game()
