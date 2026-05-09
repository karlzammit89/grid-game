import streamlit as st
import random
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

# --- 2. INFINITE QUESTION GENERATOR ---
def generate_final_challenge():
    """Generates a unique high-difficulty question using templates."""
    counts = ["3", "4", "5"]
    subjects = ["players", "clubs", "managers", "stadiums", "nations"]
    
    templates = [
        f"Name {random.choice(counts)} {random.choice(subjects)} that have won both the {random.choice(['Champions League', 'World Cup', 'Domestic League'])} and {random.choice(['another major trophy', 'a continental cup', 'a secondary cup'])}.",
        f"Name {random.choice(counts)} {random.choice(['Brazilian', 'French', 'Spanish', 'German', 'Argentinian'])} {random.choice(['players', 'managers'])} who have won the {random.choice(['Champions League', 'Premier League', 'La Liga', 'Serie A'])}.",
        f"Name {random.choice(counts)} {random.choice(['London', 'Madrid', 'Milan', 'Manchester', 'Lisbon'])} based clubs that have played in {random.choice(['European competitions', 'top flight finals', 'relegation playoffs'])}.",
        f"Name {random.choice(counts)} players who have played for {random.choice(['Real Madrid', 'Barcelona', 'Bayern', 'Man Utd'])} and {random.choice(['AC Milan', 'Juventus', 'PSG', 'Chelsea'])}.",
        f"Name {random.choice(counts)} {random.choice(subjects)} that have achieved {random.choice(['a league & cup double', 'a treble', 'back-to-back titles', 'unbeaten runs'])}.",
        f"Name {random.choice(counts)} players who have scored {random.choice(['in a World Cup final', 'a UCL hat-trick', '100+ league goals', 'for 3 different top clubs'])}.",
        f"Name {random.choice(counts)} {random.choice(['African', 'South American', 'European'])} nations that have {random.choice(['reached a WC Semi-final', 'won their continental cup', 'beaten a top 10 ranked team'])}."
    ]
    return random.choice(templates)

CRITERIA_POOL = [
    "Name a player who has played for both Real Madrid & AC Milan",
    "Name any Stadium in England with 30,000+ capacity",
    "Name a Brazilian player who has won the Premier League",
    "Name any player to have played for both Liverpool & Chelsea",
    "Name a French player currently playing in the Bundesliga",
    "Name any team that has won the FA Cup",
    "Name a player with 100+ caps for any European nation",
    "Name any club currently in the Italian Serie A",
    "Name a Spanish player who has played in the Premier League",
    "Name any winner of the African Cup of Nations",
    "Name a player who played for both Manchester United & Arsenal",
    "Name any club that has played in a Champions League Final",
    "Name a Dutch player who has played for Barcelona",
    "Name any player who has scored 20+ goals in a single PL season",
    "Name an Argentinian player who has played in Italy",
    "Name any team currently in the German Bundesliga",
    "Name a player who has won the World Cup and Champions League",
    "Name any club based in London",
    "Name a Portuguese player who has played for Real Madrid",
    "Name any player to score a hat-trick in the Champions League",
    "Name a German player who has played for Arsenal",
    "Name any city that has a team in the top 2 Spanish divisions",
    "Name a player who has been managed by Jose Mourinho",
    "Name any club that has won the Europa League / UEFA Cup",
    "Name a Belgian player who has played in the Premier League"
]

# --- 3. STATE MANAGEMENT ---
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
    st.session_state.winner = None

# --- 4. UI ---
st.set_page_config(page_title="Football Path Trivia", layout="wide")

if st.session_state.winner:
    st.balloons()
    st.markdown(f"""<div style="text-align:center; padding:100px;"><h1 style="font-size:5rem;">🏆</h1><h1 style="font-size:3rem; color:white;">FULL TIME!</h1><h2 style="font-size:2.5rem; color:{st.session_state.winner['color']};">Congratulations {st.session_state.winner['name']}!</h2></div>""", unsafe_allow_html=True)
    if st.button("🏟️ Return to Menu", use_container_width=True, type="primary"):
        st.session_state.game_started = False
        st.session_state.winner = None
        st.rerun()

elif not st.session_state.game_started:
    st.title("⚽ Football Path Setup")
    with st.container(border=True):
        c1, c2 = st.columns(2)
        st.session_state.grid_size = c1.number_input("Grid Size (e.g. 4 for 16 squares)", 3, 6, 4)
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
        last_sq_index = len(st.session_state.grid_map) - 1

        if not st.session_state.rolled:
            if st.button("🎲 ROLL DICE (Max 3)", use_container_width=True, type="primary"):
                st.session_state.current_roll = random.randint(1, 3)
                new_pos = min(player['pos'] + st.session_state.current_roll, last_sq_index)
                player['prev'], player['pos'] = player['pos'], new_pos
                
                # Dynamic Question Generation if they land on final whistle
                if player['pos'] == last_sq_index:
                    st.session_state.active_final_task = generate_final_challenge()
                
                st.session_state.rolled = True
                st.rerun()
        else:
            st.markdown(f"<div style='text-align:center; font-size:4rem; font-weight:800;'>{st.session_state.current_roll}</div>", unsafe_allow_html=True)
            
            if player['pos'] == last_sq_index:
                st.warning("🥅 GOAL LINE CHALLENGE!")
                st.markdown(f"<p style='text-align:center; font-size:1.1rem; border:1px solid #555; padding:10px; border-radius:10px;'>{st.session_state.active_final_task}</p>", unsafe_allow_html=True)
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
            st.error("Quit Game?")
            cy, cn = st.columns(2)
            if cy.button("Yes", use_container_width=True, type="primary"):
                st.session_state.game_started = False
                st.session_state.confirm_reset = False
                st.rerun()
            if cn.button("No", use_container_width=True):
                st.session_state.confirm_reset = False
                st.rerun()
