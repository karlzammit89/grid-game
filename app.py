import streamlit as st
import random

# ==========================================
# 1. CORE ENGINE: HARDCODED DATA & LOGIC
# ==========================================

def get_answer_logic(task_text):
    """Matches the current task text to hardcoded football datasets."""
    t_lower = task_text.lower()
    ans_list = []

    # --- TROPHY DATA (Historical Winners) ---
    TROPHY_DATA = {
        "bundesliga": ["Bayern Munich", "Borussia Dortmund", "Borussia Mönchengladbach", "Werder Bremen", "Hamburger SV", "VfB Stuttgart", "FC Köln", "Kaiserslautern", "1860 Munich", "Wolfsburg", "Nuremberg", "Bayer Leverkusen", "Schalke 04", "Hertha BSC", "Rapid Vienna", "Hannover 96", "Fortuna Düsseldorf", "Union Berlin"],
        "premier league": ["Manchester United", "Liverpool", "Arsenal", "Manchester City", "Everton", "Aston Villa", "Sunderland", "Chelsea", "Newcastle United", "Blackburn Rovers", "Huddersfield Town", "Leeds United", "Wolverhampton Wanderers", "Leicester City", "Nottingham Forest", "Tottenham Hotspur"],
        "la liga": ["Real Madrid", "Barcelona", "Atletico Madrid", "Athletic Bilbao", "Valencia", "Real Sociedad", "Deportivo La Coruña", "Sevilla", "Real Betis"],
        "serie a": ["Juventus", "Inter Milan", "AC Milan", "Genoa", "Torino", "Bologna", "AS Roma", "Napoli", "Lazio", "Fiorentina", "Sampdoria", "Hellas Verona"],
        "champions league": ["Real Madrid", "AC Milan", "Liverpool", "Bayern Munich", "Barcelona", "Ajax", "Inter Milan", "Manchester United", "Juventus", "Benfica", "Nottingham Forest", "Chelsea", "Celtic", "Borussia Dortmund", "Manchester City"]
    }

    # --- STADIUM DATA (Top 25 per country) ---
    STADIUM_DATA = {
        "england": ["Wembley", "Old Trafford", "Tottenham Hotspur Stadium", "London Stadium", "Anfield", "Emirates Stadium", "Etihad Stadium", "St James' Park", "Stadium of Light", "Villa Park", "Stamford Bridge", "Goodison Park", "Hillsborough", "Elland Road"],
        "spain": ["Camp Nou", "Santiago Bernabéu", "Metropolitano", "Benito Villamarín", "San Mamés", "Mestalla", "Ramón Sánchez Pizjuán", "La Cartuja", "Reale Arena", "RCDE Stadium"],
        "germany": ["Signal Iduna Park", "Allianz Arena", "Olympiastadion Berlin", "Veltins-Arena", "Deutsche Bank Park", "Stuttgart Arena", "Volksparkstadion", "RheinEnergieStadion", "Borussia-Park", "Red Bull Arena"]
    }

    # --- KIT COLORS ---
    KIT_DATA = {
        "red": ["Liverpool", "Man United", "Arsenal", "Bayern Munich", "Benfica", "Ajax", "AC Milan", "Sevilla", "Bayer Leverkusen"],
        "blue": ["Chelsea", "Man City", "Everton", "Napoli", "Inter Milan", "PSG", "Porto", "Lazio", "Schalke 04", "Rangers", "Leicester City"],
        "white": ["Real Madrid", "Tottenham Hotspur", "Valencia", "Leeds United", "Lyon", "Santos", "Fulham"],
        "yellow": ["Borussia Dortmund", "Villarreal", "Watford", "Norwich City", "Al-Nassr"],
        "green": ["Celtic", "Sporting CP", "Real Betis", "Palmeiras", "Werder Bremen", "Wolfsburg"]
    }

    # Logic: Find matches within the task string
    for league, winners in TROPHY_DATA.items():
        if league in t_lower: ans_list = winners
    if not ans_list:
        for country, stadiums in STADIUM_DATA.items():
            if country in t_lower: ans_list = stadiums
    if not ans_list:
        for color, teams in KIT_DATA.items():
            if color in t_lower: ans_list = teams

    return ans_list

def reset_all_data():
    """Wipes session state to restart the game."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# ==========================================
# 2. SESSION STATE INITIALIZATION
# ==========================================

if 'grid_map' not in st.session_state:
    # Example 5x5 grid generation
    tasks = ["Win the Premier League", "Win the Bundesliga", "Stadium in England", 
             "Team with Red Kit", "Win Champions League", "Stadium in Spain"]
    st.session_state.grid_map = {i: {"task": random.choice(tasks)} for i in range(25)}
    st.session_state.player = {"pos": 0, "name": "Player 1"}
    st.session_state.rolled = False
    st.session_state.current_roll = 0
    st.session_state.confirm_reset = False

player = st.session_state.player

# ==========================================
# 3. UI LAYOUT (SIDEBAR & MAIN)
# ==========================================

st.title("⚽ Football Grid Master")

# --- MAIN GAME BOARD ---
cols = st.columns(5)
for i in range(25):
    with cols[i % 5]:
        if player['pos'] == i:
            st.button(f"📍 P1", key=f"btn{i}", use_container_width=True, type="primary")
        else:
            st.button(f"{i}", key=f"btn{i}", use_container_width=True)

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Game Controls")

# Dice Roll Logic
if st.sidebar.button("🎲 Roll Dice", disabled=st.session_state.rolled):
    st.session_state.current_roll = random.randint(1, 6)
    new_pos = (player['pos'] + st.session_state.current_roll) % 25
    player['pos'] = new_pos
    st.session_state.rolled = True
    st.rerun()

st.sidebar.markdown("---")

# TASK & ANSWERS SECTION
if not st.session_state.rolled:
    st.sidebar.write("Roll the dice to move to a new square!")
else:
    # 1. Define task first
    task_text = st.session_state.grid_map[player['pos']]['task']
    st.sidebar.info(f"**Current Task:** {task_text}")
    st.sidebar.write(f"You rolled a **{st.session_state.current_roll}**")

    # 2. Fetch Answers
    all_answers = get_answer_logic(task_text)
    n = len(all_answers)

    # 3. Display Answers
    with st.sidebar.expander(f"👁️ View Answers ({n})"):
        if n > 0:
            formatted_rows = "\n".join([f"* {item}" for item in all_answers])
            st.markdown(formatted_rows)
        else:
            st.write("No answers found in local database.")

    if st.sidebar.button("✅ Task Complete / Next Turn"):
        st.session_state.rolled = False
        st.rerun()

st.sidebar.markdown("---")

# RESET LOGIC
if not st.session_state.confirm_reset:
    if st.sidebar.button("🚩 End Game", use_container_width=True):
        st.session_state.confirm_reset = True
        st.rerun()
else:
    st.sidebar.warning("Are you sure?")
    r1, r2 = st.sidebar.columns(2)
    if r1.button("Confirm", type="primary"): reset_all_data()
    if r2.button("Cancel"): 
        st.session_state.confirm_reset = False
        st.rerun()
