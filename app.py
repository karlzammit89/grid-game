import streamlit as st
import random
import re

# --- 1. SMART DATA MAPPING ---
COUNTRY_DATA = {
    "French": "fr", "France": "fr", "Spanish": "es", "Spain": "es",
    "English": "gb-eng", "England": "gb-eng", "Portuguese": "pt", "Portugal": "pt",
    "Dutch": "nl", "Netherlands": "nl", "Belgian": "be", "Belgium": "be",
    "German": "de", "Germany": "de", "Italian": "it", "Italy": "it",
    "Croatian": "hr", "Croatia": "hr", "Swiss": "ch", "Switzerland": "ch",
    "Danish": "dk", "Denmark": "dk", "Turkish": "tr", "Türkiye": "tr",
    "Austrian": "at", "Austria": "at", "Ukrainian": "ua", "Ukraine": "ua",
    "Scottish": "gb-sct", "Scotland": "gb-sct", "Swedish": "se", "Sweden": "se",
    "Welsh": "gb-wls", "Wales": "gb-wls", "Polish": "pl", "Poland": "pl",
    "Norwegian": "no", "Norway": "no",
    "Argentinian": "ar", "Argentina": "ar", "Brazilian": "br", "Brazil": "br",
    "Colombian": "co", "Colombia": "co", "Uruguayan": "uy", "Uruguay": "uy",
    "Ecuadorian": "ec", "Ecuador": "ec",
    "Moroccan": "ma", "Morocco": "ma", "Senegalese": "sn", "Senegal": "sn",
    "Nigerian": "ng", "Nigeria": "ng", "Egyptian": "eg", "Egypt": "eg",
    "Ivorian": "ci", "Côte d'Ivoire": "ci", "Algerian": "dz", "Algeria": "dz",
    "American": "us", "USA": "us", "Mexican": "mx", "Mexico": "mx",
    "Canadian": "ca", "Canada": "ca", "Japanese": "jp", "Japan": "jp",
    "South Korean": "kr", "South Korea": "kr", "Australian": "au", "Australia": "au"
}

ESPN_LOGOS = {
    "Man Utd": "360", "Manchester United": "360", "Liverpool": "364", "Arsenal": "359", 
    "Chelsea": "363", "Man City": "382", "Spurs": "367", "Tottenham": "367",
    "Aston Villa": "362", "Newcastle": "361", "Real Madrid": "86", "Barcelona": "83", 
    "Atletico Madrid": "1068", "Sevilla": "243", "Villarreal": "102", "AC Milan": "103", 
    "Juventus": "111", "Inter Milan": "110", "AS Roma": "104", "Napoli": "114", 
    "Bayern Munich": "132", "Dortmund": "124", "Leverkusen": "131", "PSG": "160", 
    "Marseille": "176", "Monaco": "174", 
    "Ajax": "139", "PSV Eindhoven": "148", "PSV": "148", "Feyenoord": "142", 
    "Benfica": "1929", "Porto": "437", "Sporting CP": "2250"
}

def get_club_logo_html(text):
    html = ""
    sorted_clubs = sorted(ESPN_LOGOS.keys(), key=len, reverse=True)
    found_ids = set()
    for club in sorted_clubs:
        if club.lower() in text.lower():
            espn_id = ESPN_LOGOS[club]
            if espn_id not in found_ids:
                url = f"https://a.espncdn.com/i/teamlogos/soccer/500/{espn_id}.png"
                html += f'<img src="{url}" style="height:18px; vertical-align:middle; margin-left:6px;">'
                found_ids.add(espn_id)
    return html

def clean_text_and_add_assets(text):
    clean_text = text.strip()
    flag_html = ""
    for word, iso in COUNTRY_DATA.items():
        if word.lower() in clean_text.lower():
            flag_url = f"https://flagcdn.com/w40/{iso}.png"
            flag_html = f'<img src="{flag_url}" style="height:14px; vertical-align:middle; margin-left:6px; border-radius:2px; border:1px solid #444;">'
            break
    logo_html = get_club_logo_html(clean_text)
    return f"{clean_text} {logo_html}{flag_html}"

# --- 2. DYNAMIC LOGIC GENERATORS ---
def generate_random_task():
    nation = random.choice(list(COUNTRY_DATA.keys()))
    article = "an" if nation[0].lower() in ['a', 'e', 'i', 'o', 'u'] else "a"
    clubs = random.sample(list(ESPN_LOGOS.keys()), 2)
    
    templates = [
        lambda: f"Name a player who played for both {clubs[0]} & {clubs[1]}",
        lambda: f"Name a {random.choice(['Brazilian', 'French', 'Spanish', 'Dutch', 'Argentinian', 'Portuguese', 'German', 'Italian', 'Turkish'])} player who played for {random.choice(list(ESPN_LOGOS.keys()))}",
        lambda: f"Name {article} {nation} player who has played in the Champions League",
        lambda: f"Name a manager who coached {random.choice(['Real Madrid', 'Chelsea', 'Bayern Munich', 'PSG', 'Juventus', 'Barcelona', 'Inter Milan'])}"
    ]
    return random.choice(templates)()

# --- 3. UI ENGINE & STATE ---
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
    
    # GUARANTEE UNIQUENESS
    unique_tasks = set()
    required_tasks = total_sq - 2
    
    while len(unique_tasks) < required_tasks:
        new_task = generate_random_task()
        unique_tasks.add(new_task)
    
    # Add unique tasks to board with assets
    for task_text in list(unique_tasks):
        board.append({"task": clean_text_and_add_assets(task_text)})
        
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

# --- 4. DASHBOARD UI ---
st.set_page_config(page_title="Football Path Trivia", layout="wide")

if st.session_state.winner:
    st.balloons()
    st.markdown(f"""<div style="text-align:center; padding:100px;"><h1 style="font-size:5rem;">🏆</h1><h1 style="font-size:3rem; color:white;">FULL TIME!</h1><h2 style="font-size:2.5rem; color:{st.session_state.winner['color']};">Congratulations {st.session_state.winner['name']}!</h2></div>""", unsafe_allow_html=True)
    if st.button("🏟️ Return to Menu", use_container_width=True, type="primary"):
        reset_all_data()

elif not st.session_state.game_started:
    st.title("⚽ Football Path Setup")
    with st.container(border=True):
        c1, c2 = st.columns(2)
        st.session_state.grid_size = c1.number_input("Grid Size (4 = 4x4, 5 = 5x5)", 3, 6, 4)
        st.session_state.num_players = c2.number_input("Number of Players", 1, 4, 2)
    cols = st.columns(st.session_state.num_players)
    st.session_state.player_names = [cols[i].text_input(f"Manager {i+1}", key=f"p{i}") for i in range(st.session_state.num_players)]
    if st.button("🚀 START MATCH", use_container_width=True, type="primary"):
        start_game()
        st.rerun()

else:
    player = st.session_state.player_data[st.session_state.turn]
    st.markdown(f"""
        <style>
        .grid-container {{ display: grid; gap: 12px; grid-template-columns: repeat({st.session_state.grid_size}, 1fr); }}
        .grid-item {{ background: #1e2129; border: 1px solid #333; border-radius: 12px; padding: 12px; text-align: center; min-height: 140px; display: flex; flex-direction: column; align-items: center; justify-content: space-between; }}
        .active-sq {{ border: 3px solid {player['color']}; box-shadow: 0 0 15px {player['color']}55; }}
        .p-tag {{ border-radius: 50%; width: 28px; height: 28px; display: inline-flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: 800; border: 2px solid #fff; margin: 1px; }}
        .icon-emoji {{ font-size: 1.8rem; margin-bottom: 5px; }}
        </style>
    """, unsafe_allow_html=True)

    grid_html = '<div class="grid-container">'
    for i, item in enumerate(st.session_state.grid_map):
        active = "active-sq" if i == player['pos'] else ""
        marks = "".join([f'<span class="p-tag" style="background:{p["color"]}">{p["initials"]}</span>' for pid, p in st.session_state.player_data.items() if p['pos'] == i])
        icon = "⚽" if i != 0 and i != len(st.session_state.grid_map)-1 else "🏁" if i == 0 else "🏆"
        grid_html += f'<div class="grid-item {active}"><div style="width:100%; color:#555; font-size:0.7rem; text-align:left;">#{i:02}</div><div class="icon-emoji">{icon}</div><div style="color:#eee; font-weight:600; font-size:0.85rem; line-height:1.2;">{item["task"]}</div><div style="min-height:30px; display:flex; justify-content:center; align-items:center;">{marks}</div></div>'
    st.markdown(grid_html + "</div>", unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(f"<h2 style='text-align:center; color:{player['color']};'>{player['name']}</h2>", unsafe_allow_html=True)
        last_sq_index = len(st.session_state.grid_map) - 1

        if not st.session_state.rolled:
            if st.button("🎲 ROLL DICE", use_container_width=True, type="primary"):
                st.session_state.current_roll = random.randint(1, 3)
                player['prev'], player['pos'] = player['pos'], min(player['pos'] + st.session_state.current_roll, last_sq_index)
                if player['pos'] == last_sq_index:
                    st.session_state.active_final_task = clean_text_and_add_assets(generate_random_task())
                st.session_state.rolled = True
                st.rerun()
        else:
            st.markdown(f"<div style='text-align:center; font-size:4rem; font-weight:800;'>{st.session_state.current_roll}</div>", unsafe_allow_html=True)
            if player['pos'] == last_sq_index:
                st.warning("🥅 GOAL LINE CHALLENGE!")
                st.markdown(f"<p style='text-align:center; font-size:1.1rem; border:1px solid #555; padding:15px; border-radius:10px;'><b>FINAL TASK:</b><br>{st.session_state.active_final_task}</p>", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                if c1.button("🎯 Scored!", use_container_width=True):
                    st.session_state.winner = player
                    st.rerun()
                if c2.button("🚫 Missed", use_container_width=True):
                    player['pos'] = player['prev']
                    st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players
                    st.session_state.rolled = False
                    st.rerun()
            elif player['pos'] != 0:
                st.markdown(f"<p style='text-align:center;'><b>Provide {st.session_state.current_roll} answers for:</b><br>{st.session_state.grid_map[player['pos']]['task']}</p>", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                if c1.button("✅ Success", use_container_width=True):
                    st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players
                    st.session_state.rolled = False
                    st.rerun()
                if c2.button("❌ Fail", use_container_width=True):
                    player['pos'] = player['prev']
                    st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players
                    st.session_state.rolled = False
                    st.rerun()
            else:
                if st.button("Next Turn", use_container_width=True):
                    st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players
                    st.session_state.rolled = False
                    st.rerun()

        st.markdown("---")
        if not st.session_state.confirm_reset:
            if st.button("🚩 End Match", use_container_width=True):
                st.session_state.confirm_reset = True
                st.rerun()
        else:
            st.error("Quit?")
            cy, cn = st.columns(2)
            if cy.button("Yes", use_container_width=True): reset_all_data()
            if cn.button("No", use_container_width=True): st.session_state.confirm_reset = False; st.rerun()
