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

PLAYER_COLORS = ["#FF4B4B", "#1C83E1", "#00C04A", "#FFD700"] 

# --- 2. HELPER FUNCTIONS ---
def get_initials(name):
    if not name: return "?"
    parts = name.split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return name[:2].upper()

# --- 3. STATE MANAGEMENT ---
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
    board = [{"task": "🏁 START", "req": 0}]
    random_pool = random.sample(CRITERIA_POOL * 2, total_squares - 2)
    board.extend(random_pool)
    board.append({"task": "🏆 FINISH", "req": 0})
    
    st.session_state.grid_map = board
    st.session_state.player_data = {
        i: {
            "pos": 0, 
            "prev": 0, 
            "name": st.session_state.player_names[i] if st.session_state.player_names[i] else f"Player {i+1}",
            "initials": get_initials(st.session_state.player_names[i] if st.session_state.player_names[i] else f"P{i+1}"),
            "color": PLAYER_COLORS[i]
        } for i in range(st.session_state.num_players)
    }
    st.session_state.game_started = True

# --- 4. UI SETUP ---
st.set_page_config(page_title="Football Path Trivia", layout="wide")

if not st.session_state.game_started:
    st.title("⚽ Football Trivia Setup")
    
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.grid_size = st.selectbox("Board Dimensions", [3, 4, 5, 6], index=1, help="Size of the N x N grid")
        with col2:
            st.session_state.num_players = st.number_input("Number of Players", 1, 4, 2)
    
    st.subheader("👤 Player Entry")
    st.session_state.player_names = []
    name_cols = st.columns(st.session_state.num_players)
    for i in range(st.session_state.num_players):
        name = name_cols[i].text_input(f"Player {i+1}", placeholder=f"Enter name...", key=f"name_in_{i}")
        st.session_state.player_names.append(name)
    
    if st.button("🚀 LAUNCH GAME", use_container_width=True, type="primary"):
        start_game()
        st.rerun()

else:
    # --- GAMEPLAY PHASE ---
    player_id = st.session_state.turn
    player = st.session_state.player_data[player_id]
    
    # Custom CSS for UI
    styles = "".join([f".p-tag-{i} {{ background: {PLAYER_COLORS[i]}; color: white; border-radius: 50%; width: 28px; height: 28px; display: inline-flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: bold; margin: 2px; border: 1px solid rgba(255,255,255,0.3); }}" for i in range(4)])
    st.markdown(f"""
        <style>
        .grid-container {{ display: grid; gap: 12px; margin-bottom: 20px; }}
        .grid-item {{ border: 1px solid #333; border-radius: 12px; padding: 15px; text-align: center; background: #0e1117; min-height: 100px; transition: 0.3s; }}
        .active-sq {{ border: 2px solid {player['color']} !important; box-shadow: 0 0 15px {player['color']}44; background: #161b22 !important; }}
        {styles}
        </style>
    """, unsafe_allow_html=True)

    # Board Display
    cols = st.session_state.grid_size
    grid_html = f'<div class="grid-container" style="grid-template-columns: repeat({cols}, 1fr);">'
    for i, item in enumerate(st.session_state.grid_map):
        is_active = "active-sq" if i == player['pos'] else ""
        
        # Initials Markers
        player_markers = '<div style="margin-top: 8px; display: flex; justify-content: center; flex-wrap: wrap;">'
        for p_id, p_info in st.session_state.player_data.items():
            if p_info['pos'] == i:
                player_markers += f'<span class="p-tag-{p_id}">{p_info["initials"]}</span>'
        player_markers += '</div>'
        
        grid_html += f'<div class="grid-item {is_active}"><div style="color: #555; font-size: 0.7rem;">{i}</div><div style="font-weight: 600; font-size: 0.9rem;">{item["task"]}</div>{player_markers}</div>'
    grid_html += '</div>'
    st.markdown(grid_html, unsafe_allow_html=True)

    # --- ENHANCED SIDEBAR UI ---
    with st.sidebar:
        st.markdown(f"## 🏟️ Pitch-side")
        
        # Player Turn Card
        with st.container(border=True):
            st.markdown(f"<p style='text-align: center; margin-bottom: 0; font-size: 0.9rem; color: #888;'>CURRENT TURN</p>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='color: {player['color']}; text-align: center; margin-top: 0;'>{player['name']}</h2>", unsafe_allow_html=True)
            
            if not st.session_state.rolled:
                st.info("Waiting for roll...")
                if st.button(f"🎲 ROLL DICE", use_container_width=True, type="primary"):
                    st.session_state.current_roll = random.randint(1, 3)
                    player['prev'] = player['pos']
                    player['pos'] = min(player['pos'] + st.session_state.current_roll, len(st.session_state.grid_map)-1)
                    st.session_state.rolled = True
                    st.rerun()
            else:
                st.markdown(f"<div style='text-align: center; font-size: 3rem;'>{st.session_state.current_roll}</div>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: center; color: #888;'>Required Answers: <b>{st.session_state.grid_map[player['pos']]['req']}</b></p>", unsafe_allow_html=True)

        # Referee Controls
        if st.session_state.rolled:
            st.markdown("### 📢 Referee Decision")
            col_a, col_b = st.columns(2)
            if col_a.button("✅ GO", use_container_width=True):
                st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players
                st.session_state.rolled = False
                st.rerun()
            if col_b.button("❌ BACK", use_container_width=True):
                player['pos'] = player['prev']
                st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players
                st.session_state.rolled = False
                st.rerun()

        # Restart Logic with Confirmation
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚩 End Session", use_container_width=True):
            st.session_state.confirm_reset = True
            
        if st.session_state.get('confirm_reset'):
            with st.status("Are you sure?", expanded=True):
                st.write("Current game progress will be lost.")
                col_y, col_n = st.columns(2)
                if col_y.button("Yes, Restart", type="primary"):
                    st.session_state.game_started = False
                    st.session_state.confirm_reset = False
                    st.rerun()
                if col_n.button("No, Keep Playing"):
                    st.session_state.confirm_reset = False
                    st.rerun()

    # Celebration
    if player['pos'] == len(st.session_state.grid_map) - 1 and not st.session_state.rolled:
        st.balloons()
        st.markdown(f"<h1 style='text-align: center; color: {player['color']}'>🏆 {player['name']} IS THE CHAMPION! 🏆</h1>", unsafe_allow_html=True)
