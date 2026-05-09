import streamlit as st
import random
import re

# --- 1. SMART DATA MAPPING ---
# Expanded Nations (14px Flags)
COUNTRY_DATA = {
    "Spanish": "es", "Spain": "es", "English": "gb-eng", "England": "gb-eng",
    "Italian": "it", "Italy": "it", "German": "de", "Germany": "de",
    "French": "fr", "France": "fr", "Portuguese": "pt", "Portugal": "pt",
    "Dutch": "nl", "Netherlands": "nl", "Brazilian": "br", "Brazil": "br",
    "Argentinian": "ar", "Argentina": "ar", "Belgian": "be", "Belgium": "be",
    "Uruguayan": "uy", "Uruguay": "uy", "Egyptian": "eg", "Egypt": "eg",
    "Norwegian": "no", "Norway": "no", "Scottish": "gb-sct", "Scotland": "gb-sct",
    "Moroccan": "ma", "Morocco": "ma", "Colombian": "co", "Colombia": "co",
    "Mexican": "mx", "Mexico": "mx", "Japanese": "jp", "Japan": "jp"
}

# Expanded ESPN IDs (18px Logos)
ESPN_LOGOS = {
    "Man Utd": "360", "Manchester United": "360", "Liverpool": "364", "Arsenal": "359", 
    "Chelsea": "363", "Man City": "382", "Spurs": "367", "Aston Villa": "362", 
    "Newcastle": "361", "Everton": "368", "Real Madrid": "86", "Barcelona": "83", 
    "Atletico Madrid": "1068", "Sevilla": "243", "Villarreal": "102", "Valencia": "95",
    "AC Milan": "103", "Juventus": "111", "Inter Milan": "110", "AS Roma": "104", 
    "Napoli": "114", "Lazio": "112", "Atalanta": "2685", "Bayern Munich": "132", 
    "Dortmund": "124", "Leverkusen": "131", "RB Leipzig": "11420", "PSG": "160", 
    "Marseille": "176", "Monaco": "174", "Lyon": "167", "Ajax": "148", 
    "PSV": "149", "Benfica": "190", "Porto": "192", "Sporting CP": "193"
}

# Smart Pairs: Guaranteed valid "Played for both" answers
VALID_CLUB_PAIRS = [
    ("Real Madrid", "AC Milan"), ("Barcelona", "PSG"), ("Man Utd", "Real Madrid"),
    ("Liverpool", "Chelsea"), ("Inter Milan", "AC Milan"), ("Bayern Munich", "Real Madrid"),
    ("Arsenal", "Barcelona"), ("Juventus", "Bayern Munich"), ("Man City", "Barcelona"),
    ("Chelsea", "Real Madrid"), ("PSG", "AC Milan"), ("Man Utd", "Juventus")
]

def get_assets_html(text):
    """Generates 18px logos and 14px flags based on text content."""
    asset_html = ""
    # Logos (18px)
    for club, eid in ESPN_LOGOS.items():
        if club.lower() in text.lower():
            url = f"https://a.espncdn.com/i/teamlogos/soccer/500/{eid}.png"
            asset_html += f'<img src="{url}" style="height:18px; vertical-align:middle; margin-left:5px;">'
    # Flags (14px)
    for country, iso in COUNTRY_DATA.items():
        if country.lower() in text.lower():
            f_url = f"https://flagcdn.com/w40/{iso}.png"
            asset_html += f'<img src="{f_url}" style="height:14px; vertical-align:middle; margin-left:6px; border-radius:2px; border:1px solid #444;">'
            break
    return asset_html

def clean_and_format(text):
    """Removes non-ascii and appends sized assets."""
    clean_text = re.sub(r'[^\x00-\x7F]+', '', text).strip()
    return f"{clean_text} {get_assets_html(clean_text)}"

# --- 2. DYNAMIC CRITERIA GENERATOR ---
def generate_random_task():
    """Smartly combines teams and nations to ensure valid trivia."""
    templates = [
        lambda: f"Name a player who played for both {random.choice(VALID_CLUB_PAIRS)[0]} & {random.choice(VALID_CLUB_PAIRS)[1]}",
        lambda: f"Name a {random.choice(['Brazilian', 'French', 'Spanish', 'Dutch', 'Argentinian'])} player who played for {random.choice(list(ESPN_LOGOS.keys()))}",
        lambda: f"Name a player who won the Champions League with both {random.choice(['Real Madrid', 'AC Milan', 'Liverpool', 'Bayern Munich', 'Barcelona'])} and another club",
        lambda: f"Name a {random.choice(['German', 'Italian', 'Portuguese', 'Belgian'])} player from the {random.choice(['Premier League', 'La Liga', 'Serie A'])}",
        lambda: f"Name a manager who coached {random.choice(['Real Madrid', 'Chelsea', 'Bayern Munich', 'PSG', 'Juventus', 'Barcelona'])}",
        lambda: f"Name a club in {random.choice(['London', 'Madrid', 'Milan', 'Lisbon', 'Paris'])} that has won a European trophy",
        lambda: f"Name a player who moved directly between {random.choice(['Arsenal', 'Man Utd', 'Liverpool', 'Barcelona', 'Real Madrid'])} and a rival",
        lambda: f"Name a {random.choice(list(COUNTRY_DATA.keys()))} player who has over 50 international goals"
    ]
    return clean_and_format(random.choice(templates)())

# --- 3. STREAMLIT GAME ENGINE ---
def reset_game():
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()

if 'game_started' not in st.session_state:
    st.session_state.update({
        'game_started': False, 'grid_size': 4, 'num_players': 2, 'player_names': [], 
        'player_data': {}, 'turn': 0, 'rolled': False, 'current_roll': 0, 
        'grid_map': [], 'confirm_reset': False, 'winner': None
    })

def start_match():
    total = st.session_state.grid_size ** 2
    board = [{"task": "KICK OFF"}]
    for _ in range(total - 2):
        board.append({"task": generate_random_task()})
    board.append({"task": "FINAL WHISTLE"})
    st.session_state.grid_map = board
    st.session_state.player_data = {
        i: {
            "pos": 0, "prev": 0, "name": st.session_state.player_names[i] or f"Manager {i+1}",
            "initials": (st.session_state.player_names[i][:2] if st.session_state.player_names[i] else f"M{i+1}").upper(),
            "color": ["#FF4B4B", "#1C83E1", "#00C04A", "#FFD700"][i]
        } for i in range(st.session_state.num_players)
    }
    st.session_state.game_started = True

# UI Logic
st.set_page_config(page_title="Ultimate Football Path", layout="wide")

if not st.session_state.game_started:
    st.title("🏟️ Ultimate Football Path Trivia")
    c1, c2 = st.columns(2)
    st.session_state.grid_size = c1.slider("Pitch Size", 3, 6, 4)
    st.session_state.num_players = c2.number_input("Managers", 1, 4, 2)
    st.session_state.player_names = [st.text_input(f"Manager {i+1} Name", key=f"n{i}") for i in range(st.session_state.num_players)]
    if st.button("KICK OFF", use_container_width=True, type="primary"): start_match(); st.rerun()

elif st.session_state.winner:
    st.balloons(); st.success(f"🏆 {st.session_state.winner['name']} WINS THE CUP!")
    if st.button("New Tournament"): reset_game()

else:
    # Game Board Display
    player = st.session_state.player_data[st.session_state.turn]
    st.markdown(f"<style>.grid-container {{ display: grid; gap: 10px; grid-template-columns: repeat({st.session_state.grid_size}, 1fr); }} .grid-item {{ background: #1e1e1e; border: 1px solid #333; padding: 10px; text-align: center; min-height: 120px; border-radius: 8px; }} .active {{ border: 2px solid {player['color']}; box-shadow: 0 0 10px {player['color']}; }}</style>", unsafe_allow_html=True)
    
    board_html = '<div class="grid-container">'
    for i, item in enumerate(st.session_state.grid_map):
        active_css = "active" if i == player['pos'] else ""
        marks = "".join([f'<span style="background:{p["color"]}; padding:2px 5px; border-radius:4px; margin:2px; font-size:10px;">{p["initials"]}</span>' for pid, p in st.session_state.player_data.items() if p['pos'] == i])
        board_html += f'<div class="grid-item {active_css}"><div style="font-size:10px; color:#666;">{i}</div><div style="font-size:13px; color:white;">{item["task"]}</div><div>{marks}</div></div>'
    st.markdown(board_html + "</div>", unsafe_allow_html=True)

    with st.sidebar:
        st.header(f"Turn: {player['name']}")
        if not st.session_state.rolled:
            if st.button("🎲 ROLL", use_container_width=True):
                st.session_state.current_roll = random.randint(1, 3)
                player['prev'] = player['pos']
                player['pos'] = min(player['pos'] + st.session_state.current_roll, len(st.session_state.grid_map)-1)
                st.session_state.rolled = True; st.rerun()
        else:
            st.metric("Move", st.session_state.current_roll)
            st.info(st.session_state.grid_map[player['pos']]['task'])
            if st.button("✅ Goal / Correct"):
                if player['pos'] == len(st.session_state.grid_map)-1: st.session_state.winner = player
                st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players
                st.session_state.rolled = False; st.rerun()
            if st.button("❌ Miss / Incorrect"):
                player['pos'] = player['prev']
                st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players
                st.session_state.rolled = False; st.rerun()
