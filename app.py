import streamlit as st
import random
import time
import re

# --- 1. FLAG IMAGE MAPPING ---
COUNTRY_DATA = {
    "Spanish": "es", "Spain": "es", "English": "gb-eng", "England": "gb-eng",
    "Italian": "it", "Italy": "it", "German": "de", "Germany": "de",
    "French": "fr", "France": "fr", "Portuguese": "pt", "Portugal": "pt",
    "Dutch": "nl", "Netherlands": "nl", "Croatian": "hr", "Croatia": "hr",
    "Belgian": "be", "Belgium": "be", "Turkish": "tr", "Turkey": "tr",
    "Scottish": "gb-sct", "Scotland": "gb-sct", "Welsh": "gb-wls", "Wales": "gb-wls",
    "Brazilian": "br", "Brazil": "br", "Argentinian": "ar", "Argentina": "ar",
    "Uruguayan": "uy", "Uruguay": "uy", "Egyptian": "eg", "Senegalese": "sn", 
    "Moroccan": "ma", "Nigerian": "ng", "Japanese": "jp", "Mexican": "mx", 
    "Colombian": "co", "American": "us", "Ivorian": "ci", "Ghanaian": "gh"
}

def clean_text_and_add_flag(text):
    clean_text = re.sub(r'[^\x00-\x7F]+', '', text).strip()
    flag_html = ""
    for word, iso in COUNTRY_DATA.items():
        if word.lower() in clean_text.lower():
            flag_url = f"https://flagcdn.com/w40/{iso}.png"
            flag_html = f'<img src="{flag_url}" style="height:14px; vertical-align:middle; margin-left:6px; border-radius:2px; border:1px solid #444;">'
            break
    return f"{clean_text}{flag_html}"

# --- 2. CRITERIA POOL ---
CRITERIA_POOL = [
    "Played for both Barcelona & Inter", "Name a Spanish Stadium", "Croatians to win the UCL",
    "Teams with 3+ English 2nd Div Titles", "Brazilians to play for Man City", "Teams currently in the Liga Portugal",
    "Played for both AC Milan & Chelsea", "African players to play for PSG", "Man Utd players to win a World Cup",
    "Uruguayans to score in a World Cup", "Players in France's 2018 WC Squad", "German players to win a Golden Boot",
    "Dutch players to play for Man Utd", "Italian clubs to play in the UCL", "Argentinian scorers in the PL",
    "Belgian players to win the UCL", "Portuguese players to play for Wolves", "Turkish clubs in the Super Lig",
    "Scottish players to play in the PL", "Japanese players in the Bundesliga", "Ivorian legends in the Premier League"
]

# --- 3. STATE MANAGEMENT ---
if 'game_started' not in st.session_state:
    st.session_state.update({
        'game_started': False, 'grid_size': 4, 'max_dice': 3,
        'num_players': 2, 'player_names': [], 'player_data': {},
        'turn': 0, 'rolled': False, 'current_roll': 0, 
        'grid_map': [], 'confirm_reset': False
    })

def start_game():
    total_sq = st.session_state.grid_size ** 2
    board = [{"task": "KICK OFF"}]
    selected_tasks = random.sample(CRITERIA_POOL, min(len(CRITERIA_POOL), total_sq - 2))
    for task in selected_tasks:
        board.append({"task": clean_text_and_add_flag(task)})
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

if not st.session_state.game_started:
    st.title("⚽ Football Path Setup")
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        st.session_state.grid_size = c1.number_input("Grid Size", 3, 6, 4)
        st.session_state.num_players = c2.number_input("Players", 1, 4, 2)
        st.session_state.max_dice = c3.number_input("Max Dice", 1, 6, 3)
    cols = st.columns(st.session_state.num_players)
    st.session_state.player_names = [cols[i].text_input(f"Manager {i+1}", key=f"p{i}") for i in range(st.session_state.num_players)]
    if st.button("🚀 START MATCH", use_container_width=True, type="primary"):
        start_game()
        st.rerun()
else:
    player = st.session_state.player_data[st.session_state.turn]
    
    st.markdown(f"""
        <style>
        .grid-container {{ display: grid; gap: 10px; }}
        .grid-item {{ background: #1e2129; border: 1px solid #333; border-radius: 12px; padding: 12px; text-align: center; min-height: 140px; display: flex; flex-direction: column; align-items: center; justify-content: space-between; }}
        .active-sq {{ border: 3px solid {player['color']}; box-shadow: 0 0 15px {player['color']}55; }}
        .p-tag {{ border-radius: 50%; width: 28px; height: 28px; display: inline-flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: 800; border: 2px solid #fff; margin: 1px; }}
        .icon-emoji {{ font-size: 1.8rem; margin-bottom: 5px; }}
        </style>
    """, unsafe_allow_html=True)

    grid_html = f'<div class="grid-container" style="grid-template-columns: repeat({st.session_state.grid_size}, 1fr);">'
    for i, item in enumerate(st.session_state.grid_map):
        active = "active-sq" if i == player['pos'] else ""
        marks = "".join([f'<span class="p-tag" style="background:{p["color"]}">{p["initials"]}</span>' for pid, p in st.session_state.player_data.items() if p['pos'] == i])
        icon = "⚽" if i != 0 and i != len(st.session_state.grid_map)-1 else "🏁" if i == 0 else "🏆"
        grid_html += f'<div class="grid-item {active}"><div style="width:100%; color:#555; font-size:0.7rem; text-align:left;">#{i:02}</div><div class="icon-emoji">{icon}</div><div style="color:#eee; font-weight:600; font-size:0.85rem; line-height:1.2;">{item["task"]}</div><div style="min-height:30px; display:flex; justify-content:center; align-items:center;">{marks}</div></div>'
    st.markdown(grid_html + "</div>", unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(f"<h2 style='text-align:center; color:{player['color']};'>{player['name']}</h2>", unsafe_allow_html=True)
        
        # --- LOGIC TO HIDE TRIVIA FOR KICK OFF ---
        is_trivia_sq = player['pos'] != 0 and player['pos'] != (len(st.session_state.grid_map) - 1)

        if not st.session_state.rolled:
            if st.button("🎲 ROLL DICE", use_container_width=True, type="primary"):
                st.session_state.current_roll = random.randint(1, st.session_state.max_dice)
                player['prev'], player['pos'] = player['pos'], min(player['pos'] + st.session_state.current_roll, len(st.session_state.grid_map)-1)
                st.session_state.rolled = True
                st.rerun()
        else:
            st.markdown(f"<div style='text-align:center; font-size:4rem; font-weight:800;'>{st.session_state.current_roll}</div>", unsafe_allow_html=True)
            
            if is_trivia_sq:
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
                # If they landed on Final Whistle
                st.success("Goal! You've reached the end!")
                if st.button("End Turn", use_container_width=True):
                    st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players
                    st.session_state.rolled = False
                    st.rerun()

        st.markdown("---")
        if not st.session_state.confirm_reset:
            if st.button("🚩 End Match", use_container_width=True):
                st.session_state.confirm_reset = True
                st.rerun()
        else:
            st.warning("Confirm Quit?")
            ry, rn = st.columns(2)
            if ry.button("Yes", use_container_width=True, type="primary"):
                st.session_state.game_started = False
                st.session_state.confirm_reset = False
                st.rerun()
            if rn.button("No", use_container_width=True):
                st.session_state.confirm_reset = False
                st.rerun()

    if player['pos'] == len(st.session_state.grid_map) - 1:
        st.balloons()
