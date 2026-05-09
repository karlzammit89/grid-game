import streamlit as st
import random

# --- 1. CONFIGURATION & DATA ---
CRITERIA_POOL = [
    {"task": "Barcelona & Inter", "req": 1},
    {"task": "Spanish Stadiums", "req": 3},
    {"task": "Croatians to win UCL", "req": 1},
    {"task": "3+ English 2nd Div Titles", "req": 5},
    {"task": "Spanish Stadium (Not Camp Nou/Bernabeu)", "req": 1},
    {"task": "Predominantly White Kit", "req": 4},
    {"task": "Brazilian Man City Players", "req": 1},
    {"task": "Portuguese League Teams", "req": 4},
    {"task": "AC Milan & Chelsea", "req": 5},
    {"task": "Africans for PSG", "req": 3},
    {"task": "Man Utd World Cup Winners", "req": 4},
    {"task": "Uruguayan Goalscorers", "req": 3},
    {"task": "200+ Games under Mourinho", "req": 5},
    {"task": "French World Cup 2018 Squad", "req": 3},
    {"task": "Played for both Real & Barca", "req": 1},
    {"task": "German Golden Boot Winners", "req": 2}
]

PLAYER_COLORS = ["#FF4B4B", "#1C83E1", "#00C04A", "#FFD700"] # Red, Blue, Green, Gold

# --- 2. STATE MANAGEMENT ---
if 'game_started' not in st.session_state:
    st.session_state.game_started = False
    st.session_state.grid_size = 4
    st.session_state.num_players = 2
    st.session_state.player_names = []
    st.session_state.player_data = {} 
    st.session_state.turn = 0
    st.session_state.rolled = False
    st.session_state.current_roll = 0
    st.session_state.grid_map = []

def start_game():
    total_squares = st.session_state.grid_size ** 2
    board = [{"task": "START", "req": 0}]
    random_pool = random.sample(CRITERIA_POOL * 2, total_squares - 2)
    board.extend(random_pool)
    board.append({"task": "🏆 FINISH 🏆", "req": 0})
    
    st.session_state.grid_map = board
    st.session_state.player_data = {
        i: {
            "pos": 0, 
            "prev": 0, 
            "name": st.session_state.player_names[i] if st.session_state.player_names[i] else f"Player {i+1}",
            "color": PLAYER_COLORS[i]
        } for i in range(st.session_state.num_players)
    }
    st.session_state.game_started = True

# --- 3. UI SETUP ---
st.set_page_config(page_title="Football Path Trivia", layout="wide")

if not st.session_state.game_started:
    st.title("⚽ Game Setup")
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.grid_size = st.selectbox("Grid Size (N x N)", [3, 4, 5, 6], index=1)
        st.session_state.num_players = st.number_input("Number of Players", 1, 4, 2)
    
    st.subheader("Player Names")
    st.session_state.player_names = []
    name_cols = st.columns(st.session_state.num_players)
    for i in range(st.session_state.num_players):
        name = name_cols[i].text_input(f"P{i+1} Name", placeholder=f"Player {i+1}", key=f"name_input_{i}")
        st.session_state.player_names.append(name)
    
    st.divider()
    if st.button("🚀 Start Game", use_container_width=True):
        start_game()
        st.rerun()

else:
    # --- GAMEPLAY PHASE ---
    player_id = st.session_state.turn
    player = st.session_state.player_data[player_id]
    
    # Custom CSS for Dynamic Player Colors
    styles = "".join([f".p-tag-{i} {{ background: {PLAYER_COLORS[i]}; color: white; border-radius: 4px; padding: 2px 6px; font-size: 0.75rem; margin: 2px; font-weight: bold; }}" for i in range(4)])
    st.markdown(f"""
        <style>
        .grid-container {{ display: grid; gap: 10px; margin-bottom: 20px; }}
        .grid-item {{ border: 1px solid #444; border-radius: 8px; padding: 10px; text-align: center; background: #1e1e1e; min-height: 90px; color: #ccc; }}
        .active-sq {{ border: 2px solid white !important; background: #2d2d2d !important; box-shadow: inset 0 0 10px #444; }}
        {styles}
        </style>
    """, unsafe_allow_html=True)

    # Display Board
    cols = st.session_state.grid_size
    grid_html = f'<div class="grid-container" style="grid-template-columns: repeat({cols}, 1fr);">'
    for i, item in enumerate(st.session_state.grid_map):
        is_active = "active-sq" if i == player['pos'] else ""
        
        # Build markers for all players on this square
        player_markers = '<div style="margin-top: 5px;">'
        for p_id, p_info in st.session_state.player_data.items():
            if p_info['pos'] == i:
                player_markers += f'<span class="p-tag-{p_id}">{p_info["name"]}</span>'
        player_markers += '</div>'
        
        grid_html += f'<div class="grid-item {is_active}"><small>{i}</small><br><b>{item["task"]}</b>{player_markers}</div>'
    grid_html += '</div>'
    st.markdown(grid_html, unsafe_allow_html=True)

    # --- SIDEBAR LOGIC ---
    with st.sidebar:
        st.markdown(f"### 🎯 Current Turn")
        st.markdown(f"<h1 style='color: {player['color']}; text-align: center;'>{player['name']}</h1>", unsafe_allow_html=True)
        
        if not st.session_state.rolled:
            if st.button(f"🎲 {player['name']}, Roll Dice!", use_container_width=True):
                st.session_state.current_roll = random.randint(1, 3)
                player['prev'] = player['pos']
                player['pos'] = min(player['pos'] + st.session_state.current_roll, len(st.session_state.grid_map)-1)
                st.session_state.rolled = True
                st.rerun()
        else:
            st.metric(label="Roll Result", value=st.session_state.current_roll)
            st.divider()
            st.warning("Referee Decision Required")
            
            if st.button("✅ CORRECT", type="primary", use_container_width=True):
                st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players
                st.session_state.rolled = False
                st.rerun()
            
            if st.button("❌ WRONG (Go Back)", type="secondary", use_container_width=True):
                player['pos'] = player['prev']
                st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players
                st.session_state.rolled = False
                st.rerun()
        
        st.divider()
        if st.button("Restart Session"):
            st.session_state.game_started = False
            st.rerun()

    # Winning Check
    if player['pos'] == len(st.session_state.grid_map) - 1 and not st.session_state.rolled:
        st.balloons()
        st.success(f"🎊 {player['name']} wins! 🎊")
