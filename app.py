import streamlit as st
import random
import time

# --- 1. CONFIGURATION & DATA ---
CRITERIA_POOL = [
    {"task": "Barcelona & Inter"}, {"task": "Spanish Stadiums"},
    {"task": "Croatians to win UCL"}, {"task": "English 2nd Div Titles"},
    {"task": "Spanish Stadiums"}, {"task": "Predominantly White Kit"},
    {"task": "Brazilian Man City Players"}, {"task": "Portuguese League Teams"},
    {"task": "AC Milan & Chelsea"}, {"task": "Africans for PSG"},
    {"task": "Man Utd World Cup Winners"}, {"task": "Uruguayan Goalscorers"},
    {"task": "200+ Games under Mourinho"}, {"task": "French World Cup 2018 Squad"},
    {"task": "Played for both Real & Barca"}, {"task": "German Golden Boot Winners"}
]

PLAYER_COLORS = ["#FF4B4B", "#1C83E1", "#00C04A", "#FFD700"] 

def get_initials(name):
    if not name: return "?"
    parts = name.split()
    return (parts[0][0] + parts[-1][0]).upper() if len(parts) >= 2 else name[:2].upper()

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
    st.session_state.confirm_reset = False

def start_game():
    total_squares = st.session_state.grid_size ** 2
    board = [{"task": "🏁 START"}]
    random_pool = random.sample(CRITERIA_POOL * 2, total_squares - 2)
    board.extend(random_pool)
    board.append({"task": "🏆 FINISH"})
    
    st.session_state.grid_map = board
    st.session_state.player_data = {
        i: {
            "pos": 0, "prev": 0, 
            "name": st.session_state.player_names[i] if st.session_state.player_names[i] else f"Player {i+1}",
            "initials": get_initials(st.session_state.player_names[i] if st.session_state.player_names[i] else f"P{i+1}"),
            "color": PLAYER_COLORS[i]
        } for i in range(st.session_state.num_players)
    }
    st.session_state.game_started = True

# --- 3. UI SETUP ---
st.set_page_config(page_title="Football Path Trivia", layout="wide")

if not st.session_state.game_started:
    st.title("⚽ Football Trivia Setup")
    with st.container(border=True):
        col1, col2 = st.columns(2)
        st.session_state.grid_size = col1.selectbox("Board Dimensions", [3, 4, 5, 6], index=1)
        st.session_state.num_players = col2.number_input("Number of Players", 1, 4, 2)
    
    st.subheader("👤 Player Entry")
    name_cols = st.columns(st.session_state.num_players)
    st.session_state.player_names = [name_cols[i].text_input(f"Player {i+1}", key=f"n_{i}") for i in range(st.session_state.num_players)]
    
    if st.button("🚀 LAUNCH GAME", use_container_width=True, type="primary"):
        start_game()
        st.rerun()

else:
    player_id = st.session_state.turn
    player = st.session_state.player_data[player_id]
    
    # CSS for Grid, Circles, and Button Neutrality
    styles = "".join([f".p-tag-{i} {{ background: {PLAYER_COLORS[i]}; color: white; border-radius: 50%; width: 28px; height: 28px; display: inline-flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: bold; margin: 2px; border: 1px solid rgba(255,255,255,0.3); }}" for i in range(4)])
    st.markdown(f"""
        <style>
        .grid-container {{ display: grid; gap: 12px; margin-bottom: 20px; }}
        .grid-item {{ border: 1px solid #333; border-radius: 12px; padding: 15px; text-align: center; background: #0e1117; min-height: 100px; }}
        .active-sq {{ border: 2px solid {player['color']} !important; box-shadow: 0 0 15px {player['color']}44; }}
        {styles}
        /* Make secondary buttons blend in */
        div.stButton > button {{
            background-color: transparent;
        }}
        </style>
    """, unsafe_allow_html=True)

    # Board Display
    cols = st.session_state.grid_size
    grid_html = f'<div class="grid-container" style="grid-template-columns: repeat({cols}, 1fr);">'
    for i, item in enumerate(st.session_state.grid_map):
        is_active = "active-sq" if i == player['pos'] else ""
        markers = "".join([f'<span class="p-tag-{p_id}">{p["initials"]}</span>' for p_id, p in st.session_state.player_data.items() if p['pos'] == i])
        grid_html += f'<div class="grid-item {is_active}"><div style="color: #555; font-size: 0.7rem;">{i}</div><div style="font-weight: 600;">{item["task"]}</div><div style="margin-top: 8px;">{markers}</div></div>'
    st.markdown(grid_html + '</div>', unsafe_allow_html=True)

    # --- SIDEBAR UI ---
    with st.sidebar:
        st.markdown(f"### 🏟️ Pitch-side")
        with st.container(border=True):
            st.markdown(f"<p style='text-align: center; color: #888; font-size: 0.8rem;'>TURN</p><h2 style='color: {player['color']}; text-align: center;'>{player['name']}</h2>", unsafe_allow_html=True)
            
            if not st.session_state.rolled:
                if st.button(f"🎲 ROLL DICE", use_container_width=True, type="primary"):
                    with st.spinner("🎲 Rolling..."):
                        time.sleep(1.2)
                    st.session_state.current_roll = random.randint(1, 3)
                    player['prev'] = player['pos']
                    player['pos'] = min(player['pos'] + st.session_state.current_roll, len(st.session_state.grid_map)-1)
                    st.session_state.rolled = True
                    st.rerun()
            else:
                st.markdown(f"<div style='text-align: center; font-size: 4rem; line-height: 1;'>{st.session_state.current_roll}</div>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: center;'>Provide <b>{st.session_state.current_roll}</b> answers!</p>", unsafe_allow_html=True)

        if st.session_state.rolled:
            st.markdown("### 📢 Referee's Decision")
            c_yes, c_no = st.columns(2)
            # Using type="secondary" (default) ensures no highlight until hover
            if c_yes.button("Correct", use_container_width=True):
                st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players
                st.session_state.rolled = False
                st.rerun()
            if c_no.button("Wrong", use_container_width=True):
                player['pos'] = player['prev']
                st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players
                st.session_state.rolled = False
                st.rerun()

        # Restart Logic with Confirmation
        st.markdown("<br><br>", unsafe_allow_html=True)
        if not st.session_state.confirm_reset:
            if st.button("🚩 End Session", use_container_width=True):
                st.session_state.confirm_reset = True
                st.rerun()
        else:
            with st.container(border=True):
                st.warning("Confirm End Session?")
                col_y, col_n = st.columns(2)
                if col_y.button("Yes", type="primary", use_container_width=True):
                    st.session_state.game_started = False
                    st.session_state.confirm_reset = False
                    st.rerun()
                if col_n.button("No", use_container_width=True):
                    st.session_state.confirm_reset = False
                    st.rerun()

    if player['pos'] == len(st.session_state.grid_map) - 1 and not st.session_state.rolled:
        st.balloons()
        st.success(f"🏆 {player['name']} WINS!")
