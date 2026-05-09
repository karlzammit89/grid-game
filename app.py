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

# Mapping names to domains for the Logo CDN
CLUB_DOMAINS = {
    "Real Madrid": "realmadrid.com", "Barcelona": "fcbarcelona.com",
    "Man Utd": "manutd.com", "Liverpool": "liverpoolfc.com",
    "Bayern Munich": "fcbayern.com", "AC Milan": "acmilan.com",
    "Juventus": "juventus.com", "Chelsea": "chelseafc.com",
    "Inter Milan": "inter.it", "PSG": "psg.fr",
    "Arsenal": "arsenal.com", "Man City": "mancity.com"
}

def get_club_logo(text):
    """Detects club names in text and returns HTML for their logo."""
    logo_html = ""
    for club, domain in CLUB_DOMAINS.items():
        if club.lower() in text.lower():
            url = f"https://logo.clearbit.com/{domain}"
            logo_html += f'<img src="{url}" style="height:18px; vertical-align:middle; margin-right:5px; border-radius:3px;">'
    return logo_html

def clean_text_and_add_assets(text):
    """Adds both flags and club logos to the question text."""
    # Add Flags
    flag_html = ""
    for word, iso in COUNTRY_DATA.items():
        if word.lower() in text.lower():
            flag_url = f"https://flagcdn.com/w40/{iso}.png"
            flag_html = f'<img src="{flag_url}" style="height:12px; vertical-align:middle; margin-left:5px; border:1px solid #444;">'
            break
    
    # Add Club Logos
    logos = get_club_logo(text)
    
    return f"{logos}{text}{flag_html}"

# --- 2. STRUCTURED LOGIC GENERATOR ---
def generate_final_challenge():
    big_clubs = list(CLUB_DOMAINS.keys())
    nations = ["Brazil", "France", "Spain", "Germany", "Argentina", "Portugal", "Italy", "Netherlands", "England"]
    leagues = ["Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1"]
    
    templates = [
        lambda: f"Name 3 players who have played for both {random.choice(big_clubs)} and {random.choice([c for c in big_clubs if c != 'Real Madrid'])}.",
        lambda: f"Name 4 {random.choice(nations)}n players who have won the {random.choice(leagues)}.",
        lambda: f"Name 3 nations that have won the World Cup at least twice.",
        lambda: f"Name 3 managers who have won the {random.choice(['Champions League', 'Premier League', 'World Cup'])}.",
        lambda: f"Name 4 clubs that have won the {random.choice(['Champions League', 'Europa League'])} at least once.",
        lambda: f"Name 3 stadiums located in {random.choice(['London', 'Madrid', 'Paris', 'Manchester'])}.",
        lambda: f"Name 4 players who have scored over 150 Premier League goals."
    ]
    raw_task = random.choice(templates)()
    return clean_text_assets_no_wrap(raw_task) # Helper for sidebar display

def clean_text_assets_no_wrap(text):
    return clean_text_and_add_assets(text)

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
    # Pre-select base criteria and clean them with assets
    base_pool = [
        "Name a player who played for both Real Madrid & AC Milan",
        "Name a Brazilian player who has won the Premier League",
        "Name a French player currently playing in the Bundesliga",
        "Name a Spanish player who has played in the Premier League",
        "Name a Dutch player who has played for Barcelona",
        "Name a Portuguese player who has played for Real Madrid",
        "Name a German player who has played for Arsenal",
        "Name a player managed by Jose Mourinho",
        "Name a Belgian player who has played in the Premier League"
    ]
    board = [{"task": "KICK OFF"}]
    selected_tasks = random.sample(base_pool, min(len(base_pool), total_sq - 2))
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
st.set_page_config(page_title="Football Path Trivia Pro", layout="wide")

if st.session_state.winner:
    st.balloons()
    st.markdown(f'<div style="text-align:center; padding:100px;"><h1>🏆 FULL TIME!</h1><h2 style="color:{st.session_state.winner["color"]};">Congratulations {st.session_state.winner["name"]}!</h2></div>', unsafe_allow_html=True)
    if st.button("🏟️ Return to Menu", use_container_width=True, type="primary"):
        reset_all_data()

elif not st.session_state.game_started:
    st.title("⚽ Football Path: Pro Edition")
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
    
    # Board Layout
    grid_html = f'<div style="display: grid; gap: 10px; grid-template-columns: repeat({st.session_state.grid_size}, 1fr);">'
    for i, item in enumerate(st.session_state.grid_map):
        active = f"border: 3px solid {player['color']}; box-shadow: 0 0 10px {player['color']};" if i == player['pos'] else "border: 1px solid #333;"
        marks = "".join([f'<span style="background:{p["color"]}; border-radius:50%; width:20px; height:20px; display:inline-block; margin:2px; font-size:10px; color:white; text-align:center;">{p["initials"]}</span>' for pid, p in st.session_state.player_data.items() if p['pos'] == i])
        grid_html += f'<div style="background:#1e2129; {active} border-radius:10px; padding:10px; text-align:center; min-height:120px;">'
        grid_html += f'<div style="color:#eee; font-size:0.8rem;">{item["task"]}</div><div style="margin-top:10px;">{marks}</div></div>'
    st.markdown(grid_html + "</div>", unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(f"<h2 style='color:{player['color']};'>{player['name']}'s Turn</h2>", unsafe_allow_html=True)
        last_sq = len(st.session_state.grid_map) - 1

        if not st.session_state.rolled:
            if st.button("🎲 ROLL (Max 3)", use_container_width=True, type="primary"):
                st.session_state.current_roll = random.randint(1, 3)
                player['prev'], player['pos'] = player['pos'], min(player['pos'] + st.session_state.current_roll, last_sq)
                if player['pos'] == last_sq:
                    st.session_state.active_final_task = generate_final_challenge()
                st.session_state.rolled = True
                st.rerun()
        else:
            st.title(f"🎲 {st.session_state.current_roll}")
            if player['pos'] == last_sq:
                st.warning("🥅 GOAL LINE CHALLENGE!")
                st.write(st.session_state.active_final_task, unsafe_allow_html=True)
                if st.button("🎯 Scored!", use_container_width=True):
                    st.session_state.winner = player
                    st.rerun()
            else:
                st.write(f"Provide {st.session_state.current_roll} answers for the square task.")
                if st.button("✅ Success", use_container_width=True):
                    st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players
                    st.session_state.rolled = False
                    st.rerun()
            
            if st.button("❌ Fail / Back", use_container_width=True):
                player['pos'] = player['prev']
                st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players
                st.session_state.rolled = False
                st.rerun()

        st.markdown("---")
        if st.checkbox("🚩 End Match?"):
            if st.button("Confirm Quit", type="primary"):
                reset_all_data()
