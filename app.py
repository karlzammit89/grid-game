import streamlit as st
import random

# --- 1. CONFIGURATION & DATA ---
# Default criteria to fill dynamic grids
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
    {"task": "German Golden Boot Winners", "req": 2},
    {"task": "Teams with 'United' in Premier League", "req": 4},
    {"task": "Ballon d'Or Winners (Active)", "req": 2},
    {"task": "Champions League Winners (Non-European)", "req": 1},
    {"task": "Everton & Liverpool players", "req": 1}
]

# --- 2. STATE MANAGEMENT ---
if 'game_started' not in st.session_state:
    st.session_state.game_started = False
    st.session_state.grid_size = 4
    st.session_state.num_players = 2
    st.session_state.player_data = {} # {id: {"pos": 0, "prev": 0, "name": ""}}
    st.session_state.turn = 0
    st.session_state.rolled = False
    st.session_state.current_roll = 0
    st.session_state.grid_map = []

def start_game():
    total_squares = st.session_state.grid_size ** 2
    # Create the board: Start + Random Criteria + Finish
    board = [{"task": "START", "req": 0}]
    random_pool = random.sample(CRITERIA_POOL * 2, total_squares - 2)
    board.extend(random_pool)
    board.append({"task": "🏆 FINISH 🏆", "req": 0})
    
    st.session_state.grid_map = board
    st.session_state.player_data = {
        i: {"pos": 0, "prev": 0, "name": f"Player {i+1}"} 
        for i in range(st.session_state.num_players)
    }
    st.session_state.game_started = True

# --- 3. UI SETUP ---
st.set_page_config(page_title="Football Path Trivia", layout="wide")

if not st.session_state.game_started:
    # --- SETUP PHASE ---
    st.title("⚽ Game Setup")
    st.write("Configure your football trivia board game.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.grid_size = st.selectbox("Grid Size (N x N)", [3, 4, 5, 6], index=1)
        st.session_state.num_players = st.number_input("Number of Players", 1, 4, 2)
    
    st.divider()
    if st.button("🚀 Start Game", use_container_width=True):
        start_game()
        st.rerun()

else:
    # --- GAMEPLAY PHASE ---
    player_id = st.session_state.turn
    player = st.session_state.player_data[player_id]
    
    st.title(f"🏃 {player['name']}'s Turn")
    
    # Custom CSS for Multi-player Grid
    st.markdown("""
        <style>
        .grid-container { display: grid; gap: 10px; margin-bottom: 20px; }
        .grid-item { border: 1px solid #444; border-radius: 8px; padding: 10px; text-align: center; background: #1e1e1e; min-height: 80px; font-size: 0.8rem; }
        .active-sq { border: 3px solid #FFD700 !important; background: #3d3d00 !important; }
        .player-tag { background: #007bff; color: white; border-radius: 4px; padding: 2px 5px; font-size: 0.7rem; margin: 2px; display: inline-block; }
        </style>
    """, unsafe_allow_html=True)

    # Display Board
    cols = st.session_state.grid_size
    grid_html = f'<div class="grid-container" style="grid-template-columns: repeat({cols}, 1fr);">'
    for i, item in enumerate(st.session_state.grid_map):
        is_active = "active-sq" if i == player['pos'] else ""
        
        # Check if any players are on this square
        player_markers = ""
        for p_id, p_info in st.session_state.player_data.items():
            if p_info['pos'] == i:
                player_markers += f'<span class="player-tag">P{p_id+1}</span>'
        
        grid_html += f'<div class="grid-item {is_active}">{i}<br><b>{item["task"]}</b><br>{player_markers}</div>'
    grid_html += '</div>'
    st.markdown(grid_html, unsafe_allow_html=True)

    # Game Controls
    with st.sidebar:
        st.header("Controls")
        if not st.session_state.rolled:
            if st.button("🎲 Roll Dice"):
                st.session_state.current_roll = random.randint(1, 3)
                player['prev'] = player['pos']
                player['pos'] = min(player['pos'] + st.session_state.current_roll, len(st.session_state.grid_map)-1)
                st.session_state.rolled = True
                st.rerun()
        else:
            st.write(f"You rolled a **{st.session_state.current_roll}**")
            st.subheader("Referee Decision:")
            
            c1, c2 = st.columns(2)
            if c1.button("✅ Correct"):
                # Move to next player
                st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players
                st.session_state.rolled = False
                st.rerun()
            if c2.button("❌ Wrong"):
                # Backtrack and move to next player
                player['pos'] = player['prev']
                st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players
                st.session_state.rolled = False
                st.rerun()
        
        st.divider()
        if st.button("Quit Game"):
            st.session_state.game_started = False
            st.rerun()

    # Winning Condition
    if player['pos'] == len(st.session_state.grid_map) - 1:
        st.balloons()
        st.success(f"🏆 {player['name']} HAS WON THE GAME!")
