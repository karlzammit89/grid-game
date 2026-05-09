import streamlit as st
import random
import re

# --- 1. DATA MAPPING ---
# (Keep your existing COUNTRY_DATA, ESPN_LOGOS, etc., here)
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

KIT_COLOR_MAP = {"Red": "🔴", "Blue": "🔵", "White": "⚪", "Yellow": "🟡", "Green": "🟢", "Black": "⚫"}
STADIUM_COUNTRIES = {"England": "gb-eng", "Spain": "es", "Germany": "de", "Italy": "it", "France": "fr", "Portugal": "pt", "Brazil": "br", "Argentina": "ar", "Mexico": "mx"}

# --- 2. ANSWER ENGINE ---

def get_correct_answers(text):
    """
    Returns a list of correct answers based on the task text.
    """
    t = text.lower()
    
    # 1. Specific Club Connections (Inter & Chelsea Example)
    if "inter milan" in t and "chelsea" in t:
        return [
            "Hernán Crespo", "Samuel Eto'o", "Romelu Lukaku", "Ricardo Quaresma", 
            "Juan Sebastián Verón", "Lassana Diarra", "Mateo Kovačić", "Victor Moses", 
            "Cesc Fàbregas", "Mohamed Salah", "Tiemoué Bakayoko", "Olivier Giroud"
        ]
    
    # 2. Kit Color Logic
    if "kit color is red" in t:
        return ["Liverpool", "Arsenal", "Manchester United", "Bayern Munich", "AC Milan", "Benfica", "Ajax", "AS Roma"]
    if "kit color is blue" in t:
        return ["Chelsea", "Manchester City", "Everton", "Leicester City", "Napoli", "Lazio", "FC Porto", "Schalke 04"]
    
    # 3. Trophies Logic (Mock example for Champions League)
    if "won the champions league" in t and "team" in t:
        return ["Real Madrid", "AC Milan", "Bayern Munich", "Liverpool", "Barcelona", "Ajax", "Man Utd", "Inter Milan", "Juventus", "Chelsea", "Nottingham Forest", "Porto", "Celtic", "Hamburg", "Steaua București", "Marseille", "Dortmund", "Feyenoord", "Aston Villa", "PSV Eindhoven", "Red Star Belgrade", "Man City"]

    # 4. Nation + Club Logic
    if "brazilian" in t and "real madrid" in t:
        return ["Vinícius Júnior", "Rodrygo", "Éder Militão", "Casemiro", "Marcelo", "Ronaldo Nazário", "Roberto Carlos", "Kaká", "Robinho", "Emerson"]

    # Fallback for other tasks
    return ["Answer lookup requires API integration", "See fbref.com for full lists"]

# --- 3. GRAMMAR & UI HELPERS ---

def grid_text_formatter(text):
    text = text.replace("Name a football team whose", "Football teams whose")
    text = re.sub(r"Name a[n]? (\w+) player", r"\1 players", text)
    text = re.sub(r"Name a player", "Players", text)
    text = re.sub(r"Name a team", "Teams", text)
    text = re.sub(r"Name a stadium", "Stadiums", text)
    text = re.sub(r"Name a manager", "Managers", text)
    # Grammar fixes
    for word in ["players", "teams", "Managers", "Stadiums", "Players", "Teams"]:
        text = text.replace(f"{word} who has", f"{word} who have")
        text = text.replace(f"{word} that has", f"{word} that have")
    return text

def smart_pluralize(text, count):
    if count <= 1: return text
    text = text.replace("Name a football team whose", f"Name {count} football teams whose")
    text = re.sub(r"Name a[n]? (\w+) player", f"Name {count} \\1 players", text)
    text = re.sub(r"Name a player", f"Name {count} players", text)
    text = re.sub(r"Name a team", f"Name {count} teams", text)
    text = re.sub(r"Name a stadium", f"Name {count} stadiums", text)
    text = re.sub(r"Name a manager", f"Name {count} managers", text)
    # Grammar fixes
    text = text.replace("players who has", "players who have")
    text = text.replace("teams that has", "teams that have")
    return text

# (Keep your existing articulate_task, get_assets, format_header_icons, generate_random_task, start_game functions)

# --- 4. DYNAMIC LOGIC ---
def generate_random_task(categories):
    all_nations = list(COUNTRY_DATA.keys())
    clubs_list = list(ESPN_LOGOS.keys())
    leagues_comps = ["Champions League", "Europa League", "World Cup", "FA Cup", "Premier League", "Championship", "La Liga", "Serie A", "Bundesliga", "Ligue 1"]
    pool = []
    if "Club Connections" in categories: pool.extend([1, 2, 3])
    if "Stadiums" in categories: pool.append(4)
    if "Kits" in categories: pool.append(5)
    if "Trophies" in categories: pool.extend([6, 7, 8, 9])
    if not pool: return "N/A"
    
    template_type = random.choice(pool)
    if template_type == 1: 
        # For testing, you can force Inter Milan & Chelsea here if you want to see the answers immediately
        pair = random.sample(clubs_list, 2)
        return f"Name a player who played for both {pair[0]} & {pair[1]}"
    elif template_type == 5:
        return f"Name a football team whose primary home kit color is {random.choice(list(KIT_COLOR_MAP.keys()))}"
    elif template_type == 6:
        comp = random.choice(leagues_comps)
        return f"Name a team that has won the {comp}"
    # ... (other template types)
    return f"Name a player who played for {random.choice(clubs_list)}"

# --- 5. MAIN UI LOOP ---
st.set_page_config(page_title="Football Path Trivia", layout="wide")

if 'game_started' not in st.session_state:
    st.session_state.update({
        'game_started': False, 'grid_size': 4, 'num_players': 2, 'player_names': [], 
        'player_data': {}, 'turn': 0, 'rolled': False, 'current_roll': 0, 
        'grid_map': [], 'confirm_reset': False, 'winner': None, 'active_final_task': None,
        'selected_categories': ["Club Connections", "Trophies", "Stadiums", "Kits"]
    })

def reset_all_data():
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()

def start_game():
    total_sq = st.session_state.grid_size ** 2
    board = [{"task": "KICK OFF", "assets": {"flags":[], "logos":[], "emojis":["🏁"]}}]
    unique_tasks = set()
    while len(unique_tasks) < (total_sq - 2):
        new_task = generate_random_task(st.session_state.selected_categories)
        unique_tasks.add(new_task)
    for t_text in list(unique_tasks):
        # board.append(...) setup
        pass
    # (Board generation logic here)
    st.session_state.game_started = True

# UI RENDER LOGIC
if not st.session_state.game_started:
    # (Setup Screen)
    if st.button("🚀 START MATCH"):
        # Temporary logic for the demo:
        st.session_state.grid_map = [
            {"task": "KICK OFF", "assets": {"flags":[], "logos":[], "emojis":["🏁"]}},
            {"task": "Name a player who played for both Inter Milan & Chelsea", "assets": {"flags":[], "logos":["363", "110"], "emojis":[]}},
            {"task": "Name a team that has won the Champions League", "assets": {"flags":[], "logos":[], "emojis":["🏆"]}},
            {"task": "FINAL WHISTLE", "assets": {"flags":[], "logos":[], "emojis":["🥇"]}}
        ]
        st.session_state.player_data = {0: {"pos": 0, "prev": 0, "name": "Manager 1", "color": "#FF4B4B", "initials": "M1"}}
        st.session_state.num_players = 1
        st.session_state.game_started = True
        st.rerun()

else:
    player = st.session_state.player_data[st.session_state.turn]
    # (Grid Display Code)

    with st.sidebar:
        st.markdown(f"### {player['name']}")
        if not st.session_state.rolled:
            if st.button("🎲 ROLL DICE"):
                st.session_state.current_roll = random.randint(1, 3)
                player['prev'] = player['pos']
                player['pos'] = min(player['pos'] + st.session_state.current_roll, len(st.session_state.grid_map)-1)
                st.session_state.rolled = True
                st.rerun()
        else:
            task_text = st.session_state.grid_map[player['pos']]['task']
            display_text = smart_pluralize(task_text, st.session_state.current_roll)
            
            st.info(display_text)

            # --- DYNAMIC ANSWERS SECTION ---
            if player['pos'] > 0 and player['pos'] < len(st.session_state.grid_map)-1:
                ans_list = get_correct_answers(task_text)
                with st.expander(f"👁️ View {len(ans_list)} Correct Answers"):
                    # Displaying names in a clean list
                    st.markdown("\n".join([f"- {name}" for name in ans_list]))

            c1, c2 = st.columns(2)
            if c1.button("✅ Correct"):
                st.session_state.rolled = False
                st.rerun()
            if c2.button("❌ Wrong"):
                player['pos'] = player['prev']
                st.session_state.rolled = False
                st.rerun()
