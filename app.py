import streamlit as st
import random
import re

# --- 1. DATA MAPPING (Flags & Clubs) ---
COUNTRY_DATA = {
    "Spanish": "es", "Spain": "es", "English": "gb-eng", "England": "gb-eng",
    "Italian": "it", "Italy": "it", "German": "de", "Germany": "de",
    "French": "fr", "France": "fr", "Portuguese": "pt", "Portugal": "pt",
    "Dutch": "nl", "Netherlands": "nl", "Brazilian": "br", "Brazil": "br",
    "Argentinian": "ar", "Argentina": "ar"
}

# Mapping names to domains for the Hunter.io Logo API
CLUB_DOMAINS = {
    "Real Madrid": "realmadrid.com", "Barcelona": "fcbarcelona.com",
    "Man Utd": "manutd.com", "Manchester United": "manutd.com",
    "Liverpool": "liverpoolfc.com", "Bayern Munich": "fcbayern.com",
    "AC Milan": "acmilan.com", "Juventus": "juventus.com",
    "Chelsea": "chelseafc.com", "Inter Milan": "inter.it",
    "PSG": "psg.fr", "Arsenal": "arsenal.com", "Man City": "mancity.com"
}

def get_club_logo(text):
    """Fetches logos using the Hunter.io API (reliable 2026 alternative)."""
    logo_html = ""
    for club, domain in CLUB_DOMAINS.items():
        if club.lower() in text.lower():
            # Using Hunter.io API: zero signup, high-res logos
            url = f"https://hunter.io/api/logo/{domain}"
            logo_html += f'<img src="{url}" style="height:20px; vertical-align:middle; margin-right:6px; border-radius:3px;">'
    return logo_html

def clean_text_and_add_assets(text):
    clean_text = re.sub(r'[^\x00-\x7F]+', '', text).strip()
    
    # Flags logic
    flag_html = ""
    for word, iso in COUNTRY_DATA.items():
        if word.lower() in clean_text.lower():
            flag_url = f"https://flagcdn.com/w40/{iso}.png"
            flag_html = f'<img src="{flag_url}" style="height:14px; vertical-align:middle; margin-left:6px; border-radius:2px; border:1px solid #444;">'
            break
            
    # Club Logo logic (Updated Service)
    logo_html = get_club_logo(clean_text)
    
    return f"{logo_html}{clean_text}{flag_html}"

# --- 2. STRUCTURED LOGIC GENERATOR ---
def generate_final_challenge():
    big_clubs = ["Real Madrid", "Barcelona", "Man Utd", "Liverpool", "Bayern Munich", "AC Milan", "Juventus", "Chelsea", "Inter Milan", "PSG", "Arsenal", "Man City"]
    nations = ["Brazil", "France", "Spain", "Germany", "Argentina", "Portugal", "Italy", "Netherlands", "England", "Belgium"]
    leagues = ["Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1"]
    
    templates = [
        lambda: f"Name 3 players who have played for both {random.choice(big_clubs)} and {random.choice([c for c in big_clubs if c != 'Real Madrid'])}.",
        lambda: f"Name 4 {random.choice(nations)}n players who have won the {random.choice(leagues)}.",
        lambda: f"Name 3 nations that have won the World Cup at least twice.",
        lambda: f"Name 3 managers who have won the {random.choice(['Champions League', 'Premier League', 'World Cup', 'La Liga'])}.",
        lambda: f"Name 4 clubs that have won the {random.choice(['Champions League', 'Europa League', 'Cup Winners Cup'])} at least once.",
        lambda: f"Name 3 stadiums located in {random.choice(['London', 'Madrid', 'Paris', 'Manchester', 'Lisbon', 'Rio de Janeiro'])}.",
        lambda: f"Name 4 players who have scored over 150 Premier League goals.",
        lambda: f"Name 3 players who have won the World Cup with two different clubs."
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
    "Name a Portuguese player who has played for Real Madrid",
    "Name a German player who has played for Arsenal",
    "Name a Belgian player who has played in the Premier League"
]

# --- 3. STATE REFRESH LOGIC ---
def reset_all_data():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

if 'game_started' not in st.session_state:
    st.session_state.update({
        'game_started': False, 'grid_size': 4,
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

# --- 4. UI ---
st.set_page_config(page_title="Football Path Trivia", layout="wide")

if st.session_state.winner:
    st.balloons()
    st.markdown(f'<div style="text-align:center; padding:100px;"><h1>🏆 FULL TIME!</h1><h2 style="color:{st.session_state.winner["color"]};">Congratulations {st.session_state.winner["name"]}!</h2></div>', unsafe_allow_html=True)
    if st.button("🏟️ Return to Menu", use_container_width=True, type="primary"):
        reset_all_data()

elif not st.session_state.game_started:
    st.title("⚽ Football Path Setup")
    with st.container(border=True):
        c1, c2 = st.columns(2)
        st.session_state.grid_size = c1.number_input("Grid Size", 3, 6, 4)
        st.session_state.num_players = c2.number_input("Players", 1, 4, 2)
    cols = st.columns(st.session_state.num_players)
    st.session_state.player_names = [cols[i].text_input(f"Manager {i+1}", key=f"p{i}") for i in range(st.session_state.num_players)]
    if st.button("🚀 START MATCH", use_container_width=True, type="primary"):
        start_game()
        st.rerun()

else:
    player = st.session_state.player_data[st.session_state.turn]
    st.markdown("""
        <style>
        .grid-container { display: grid; gap: 10px; }
        .grid-item { background: #1e2129; border: 1px solid #333; border-radius: 12px; padding: 12px; text-align: center; min-height: 140px; display: flex; flex-direction: column; align-items: center; justify-content: space-between; }
        .active-sq { border: 3px solid #FFF; box-shadow: 0 0 15px rgba(255,255,255,0.2); }
        .p-tag { border-radius: 50%; width: 28px; height: 28px; display: inline-flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: 800; border: 2px solid #fff; margin: 1px; }
        </style>
    """, unsafe_allow_html=True)

    grid_html = f'<div class="grid-container" style="grid-template-columns: repeat({st.session_state.grid_size}, 1fr);">'
    for i, item in enumerate(st.session_state.grid_map):
        active = "active-sq" if i == player['pos'] else ""
        marks = "".join([f'<span class="p-tag" style="background:{p["color"]}">{p["initials"]}</span>' for pid, p in st.session_state.player_data.items() if p['pos'] == i])
        grid_html += f'<div class="grid-item {active}"><div style="color:#eee; font-size:0.85rem;">{item["task"]}</div><div style="min-height:30px;">{marks}</div></div>'
    st.markdown(grid_html + "</div>", unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(f"<h2 style='text-align:center; color:{player['color']};'>{player['name']}</h2>", unsafe_allow_html=True)
        last_sq_index = len(st.session_state.grid_map) - 1

        if not st.session_state.rolled:
            if st.button("🎲 ROLL DICE", use_container_width=True, type="primary"):
                st.session_state.current_roll = random.randint(1, 3)
                player['prev'], player['pos'] = player['pos'], min(player['pos'] + st.session_state.current_roll, last_sq_index)
                if player['pos'] == last_sq_index:
                    st.session_state.active_final_task = generate_final_challenge()
                st.session_state.rolled = True
                st.rerun()
        else:
            st.markdown(f"<h1 style='text-align:center;'>{st.session_state.current_roll}</h1>", unsafe_allow_html=True)
            if player['pos'] == last_sq_index:
                st.warning("🥅 FINAL CHALLENGE!")
                st.markdown(st.session_state.active_final_task, unsafe_allow_html=True)
                if st.button("🎯 Scored!", use_container_width=True):
                    st.session_state.winner = player
                    st.rerun()
                if st.button("🚫 Missed", use_container_width=True):
                    player['pos'] = player['prev']
                    st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players
                    st.session_state.rolled = False
                    st.rerun()
            else:
                if st.button("✅ Success", use_container_width=True):
                    st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players
                    st.session_state.rolled = False
                    st.rerun()
                if st.button("❌ Fail", use_container_width=True):
                    player['pos'] = player['prev']
                    st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players
                    st.session_state.rolled = False
                    st.rerun()

        st.markdown("---")
        if st.button("🚩 End Match & Reset", use_container_width=True):
            reset_all_data()
