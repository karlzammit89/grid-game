import streamlit as st
import random

# --- 1. GAME DATA (The 4x4 Grid) ---
# Each index represents a square on the board (0-15)
GRID_DATA = [
    {"task": "START", "req": 0},
    {"task": "Barcelona & Inter (1 player)", "req": 1},
    {"task": "Spanish Stadiums (3 answers)", "req": 3},
    {"task": "Croatians to win UCL (1 player)", "req": 1},
    {"task": "3+ English 2nd Div Titles (5 teams)", "req": 5},
    {"task": "Spanish Stadium (Not Camp Nou/Bernabeu)", "req": 1},
    {"task": "Predominantly White Kit (4 teams)", "req": 4},
    {"task": "Brazilian Man City Players (1 player)", "req": 1},
    {"task": "Portuguese League Teams (4 teams)", "req": 4},
    {"task": "Schalke Legends (1 player)", "req": 1},
    {"task": "AC Milan & Chelsea (5 players)", "req": 5},
    {"task": "Africans for PSG (3 players)", "req": 3},
    {"task": "Man Utd World Cup Winners (4 players)", "req": 4},
    {"task": "Uruguayan Goalscorers (3 players)", "req": 3},
    {"task": "200+ Games under Mourinho (5 players)", "req": 5},
    {"task": "🏆 FINISH LINE 🏆", "req": 0},
]

# --- 2. STATE MANAGEMENT ---
if 'pos' not in st.session_state:
    st.session_state.pos = 0
    st.session_state.prev_pos = 0
    st.session_state.rolled = False

def reset_game():
    st.session_state.pos = 0
    st.session_state.prev_pos = 0
    st.session_state.rolled = False

# --- 3. STYLES (Custom CSS for the Grid) ---
st.markdown("""
    <style>
    .grid-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 10px;
        padding: 10px;
    }
    .grid-item {
        border: 2px solid #444;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        min-height: 100px;
        background-color: #1e1e1e;
        color: white;
    }
    .active-square {
        border: 4px solid #FFD700 !important;
        background-color: #3d3d00 !important;
        box-shadow: 0 0 15px #FFD700;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. UI LAYOUT ---
st.title("⚽ Football Path Trivia")

# Sidebar Controls
with st.sidebar:
    st.header("Game Master")
    if st.button("🎲 Roll Dice", disabled=st.session_state.rolled):
        roll = random.randint(1, 3) # Using 1-3 for better gameplay on small grid
        st.session_state.prev_pos = st.session_state.pos
        st.session_state.pos = min(st.session_state.pos + roll, 15)
        st.session_state.rolled = True
        st.rerun()
    
    st.divider()
    if st.button("🔄 Restart Game"):
        reset_game()
        st.rerun()

# Draw the 4x4 Board
grid_html = '<div class="grid-container">'
for i, item in enumerate(GRID_DATA):
    active_class = "active-square" if i == st.session_state.pos else ""
    grid_html += f'<div class="grid-item {active_class}">{i}<br><b>{item["task"]}</b></div>'
grid_html += '</div>'
st.markdown(grid_html, unsafe_allow_html=True)

st.divider()

# Gameplay Logic
if st.session_state.pos == 15:
    st.balloons()
    st.success("WE HAVE A WINNER!")
elif st.session_state.rolled:
    current = GRID_DATA[st.session_state.pos]
    st.subheader(f"📍 Current Challenge: {current['task']}")
    st.info(f"The player must provide **{current['req']}** answers.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ CORRECT (Stay Here)", use_container_width=True):
            st.session_state.rolled = False
            st.rerun()
    with col2:
        if st.button("❌ INCORRECT (Backtrack)", use_container_width=True):
            st.session_state.pos = st.session_state.prev_pos
            st.session_state.rolled = False
            st.rerun()
else:
    st.write("Waiting for the next roll...")
