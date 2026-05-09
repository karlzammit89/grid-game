import streamlit as st
import random
import re
import pandas as pd

# --- 1. DATA & ANSWER DATABASE ---
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
    task_lower = task_text.lower()
    if "both" in task_lower:
        match = re.search(r"both (.*?) & (.*)", task_text)
        if match:
            c1, c2 = match.group(1).strip(), match.group(2).strip()
            shared = fetch_shared_players(c1, c2)
            if shared: return f"Examples: {', '.join(shared[:12])}"
    
    if "stadium" in task_lower:
        for country, stadiums in ANSWER_BANK["stadium"].items():
            if country.lower() in task_lower: return f"Stadiums: {', '.join(stadiums)}"
            
    if "kit color" in task_lower:
        for color, teams in ANSWER_BANK["kit"].items():
            if color.lower() in task_lower: return f"Teams with {color} kits: {', '.join(teams)}"
            
    if "won" in task_lower:
        for trophy, winners in ANSWER_BANK["trophy_teams"].items():
            if trophy.lower() in task_lower: return f"Previous winners: {', '.join(winners)}"
            
    return "No instant data. Check the link below!"

# --- REST OF YOUR ORIGINAL FUNCTIONS (grid_text_formatter, etc.) ---
def grid_text_formatter(text):
    text = text.replace("Name a football team whose", "Football teams whose")
    text = re.sub(r"Name a[n]? (\w+) player", r"\1 players", text)
    text = re.sub(r"Name a player", "Players", text)
    text = re.sub(r"Name a team", "Teams", text)
    text = re.sub(r"Name a stadium", "Stadiums", text)
    return text

def smart_pluralize(text, count):
    if count <= 1: return text
    text = text.replace("Name a football team whose", f"Name {count} football teams whose")
    text = re.sub(r"Name a[n]? (\w+) player", f"Name {count} \\1 players", text)
    return text

def get_assets(text):
    assets = {"logos": [], "flags": [], "emojis": ["⚽"]}
    return assets

def format_header_icons(assets):
    return "⚽"

# --- 3. STATE MANAGEMENT ---
if 'game_started' not in st.session_state:
    st.session_state.update({
        'game_started': False, 'grid_size': 4, 'num_players': 2, 'player_names': [], 
        'player_data': {}, 'turn': 0, 'rolled': False, 'current_roll': 0, 'grid_map': []
    })

# --- 4. MAIN UI ---
if not st.session_state.game_started:
    st.title("Football Path Trivia")
    if st.button("Start Game"):
        # Setup logic...
        st.session_state.grid_map = [{"task": "KICK OFF", "assets":{}}] + [{"task": "Name a stadium in England", "assets":{}}] * 14 + [{"task": "FINAL WHISTLE", "assets":{}}]
        st.session_state.player_data = {0: {"name": "Manager 1", "pos": 0, "prev": 0, "color": "#FF4B4B", "initials": "M1"}}
        st.session_state.game_started = True
        st.rerun()
else:
    player = st.session_state.player_data[st.session_state.turn]
    
    with st.sidebar:
        st.header(f"Turn: {player['name']}")
        if not st.session_state.rolled:
            if st.button("🎲 ROLL"):
                st.session_state.current_roll = random.randint(1, 3)
                player['prev'] = player['pos']
                player['pos'] = min(player['pos'] + st.session_state.current_roll, len(st.session_state.grid_map)-1)
                st.session_state.rolled = True
                st.rerun()
        else:
            # THIS IS WHERE task_text IS DEFINED
            task_text = st.session_state.grid_map[player['pos']]['task']
            st.info(task_text)
            
            c1, c2 = st.columns(2)
            if c1.button("✅ Success"):
                st.session_state.rolled = False
                st.rerun()
            if c2.button("❌ Fail"):
                player['pos'] = player['prev']
                st.session_state.rolled = False
                st.rerun()

            # --- FIXED: VIEW ANSWERS DROPDOWN ---
            with st.expander("👁️ View Answers"):
                result = get_answer_logic(task_text)
                st.write(result)
                
                search_q = task_text.replace("Name a", "").strip()
                st.markdown(f"[🔍 Verify on Google](https://www.google.com/search?q=football+{search_q.replace(' ', '+')})")
