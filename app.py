import streamlit as st
import random
import re
import pandas as pd

# --- 1. THE BRAIN: LOCAL DATASET ---
# This ensures instant answers for common categories
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

# --- 2. THE UTILITIES ---
@st.cache_data(show_spinner=False)
def fetch_shared_players(club1, club2):
    """Scrapes FBref for players who played for both clubs."""
    # Mapping simple names to FBref IDs
    CLUB_IDS = {"Man Utd": "19538871", "Liverpool": "822bd0ba", "Arsenal": "18bb7c10", "Chelsea": "cff3d3bb", "Man City": "b8fd03ef", "Real Madrid": "5324c30a", "Barcelona": "206d9d25", "Bayern Munich": "054fdde2", "PSG": "e2d8892c", "Juventus": "e2d42690", "Inter Milan": "d60ad303", "AC Milan": "e2d42690"}
    id1, id2 = CLUB_IDS.get(club1), CLUB_IDS.get(club2)
    if not id1 or not id2: return []
    try:
        url = f"https://fbref.com/en/friv/players-who-played-for-multiple-clubs-countries.fcgi?t1={id1}&t2={id2}"
        tables = pd.read_html(url, storage_options={'User-Agent': 'Mozilla/5.0'})
        if tables: return tables[0]['Player'].dropna().unique().tolist()
    except: return []
    return []

def get_answer_logic(task_text):
    """Route the task to the correct answer source."""
    task_lower = task_text.lower()
    
    # 1. Shared Players (Club Connections)
    if "both" in task_lower:
        match = re.search(r"both (.*?) & (.*)", task_text)
        if match:
            c1, c2 = match.group(1).strip(), match.group(2).strip()
            shared = fetch_shared_players(c1, c2)
            return f"Players: {', '.join(shared[:10])}" if shared else "Check the Google link below for shared players."

    # 2. Stadiums
    if "stadium" in task_lower:
        for country, stadiums in ANSWER_BANK["stadium"].items():
            if country.lower() in task_lower:
                return f"Stadiums in {country}: {', '.join(stadiums)}"

    # 3. Kits
    if "kit color" in task_lower:
        for color, teams in ANSWER_BANK["kit"].items():
            if color.lower() in task_lower:
                return f"{color} kit teams: {', '.join(teams)}"

    # 4. Trophy Winners
    if "won" in task_lower:
        for trophy, winners in ANSWER_BANK["trophy_teams"].items():
            if trophy.lower() in task_lower:
                return f"Previous winners: {', '.join(winners)}"

    return "No instant data found. Use the verification link below!"

# --- 3. UI INTEGRATION (In your Sidebar or Main Loop) ---
# Assuming 'task_text' is the current square's task:
with st.expander("👁️ View Answers"):
    # Get structured answers
    result = get_answer_logic(task_text)
    if "Check" in result or "No instant" in result:
        st.info(result)
    else:
        st.success(result)
    
    # Verification Link
    search_q = task_text.replace("Name a", "").strip()
    st.markdown(f"""
    <a href="https://www.google.com/search?q=football+{search_q.replace(' ', '+')}" target="_blank" style="text-decoration:none;">
        <div style="background:#333; color:white; padding:8px; border-radius:5px; text-align:center; font-size:0.8rem; border:1px solid #555; margin-top:10px;">
            🔍 Open Google Verification
        </div>
    </a>
    """, unsafe_allow_html=True)
