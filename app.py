import streamlit as st
import random
import time

# --- 1. CONFIGURATION & DATA ---
# Criteria updated with specific country flags and explicit phrasing
CRITERIA_POOL = [
    {"task": "Played for both Barcelona & Inter", "icon": "🔵🔴"},
    {"task": "Name a Spanish 🇪🇸 Stadium", "icon": "🏟️"},
    {"task": "Croatians 🇭🇷 to win the UCL", "icon": "🇭🇷"},
    {"task": "Teams with 3+ English 🏴󠁧󠁢󠁥󠁮󠁧󠁿 2nd Div Titles", "icon": "🏆"},
    {"task": "Teams that wear a White Home Kit", "icon": "👕"},
    {"task": "Brazilians 🇧🇷 to play for Man City", "icon": "🇧🇷"},
    {"task": "Teams currently in the Liga Portugal 🇵🇹", "icon": "🇵🇹"},
    {"task": "Played for both AC Milan & Chelsea", "icon": "🔴⚫"},
    {"task": "African players to play for PSG", "icon": "🌍"},
    {"task": "Man Utd players to win a World Cup", "icon": "👹"},
    {"task": "Uruguayans 🇺🇾 to score in a World Cup", "icon": "🇺🇾"},
    {"task": "Played 200+ games under Mourinho", "icon": "👔"},
    {"task": "Players in France's 🇫🇷 2018 WC Squad", "icon": "🇫🇷"},
    {"task": "Played for both Real Madrid & Barca", "icon": "⚔️"},
    {"task": "German 🇩🇪 players to win a Golden Boot", "icon": "🇩🇪"},
    {"task": "CL Finalists who NEVER won the trophy", "icon": "🥈"},
    {"task": "Players with 100+ Premier League Goals", "icon": "⚽"},
    {"task": "Clubs currently based in London", "icon": "🏴󠁧󠁢󠁥󠁮󠁧󠁿"},
    {"task": "Dutch 🇳🇱 players to play for Man Utd", "icon": "🇳🇱"},
    {"task": "Active Managers in the Premier League", "icon": "📋"},
    {"task": "Clubs with 'City' in their official name", "icon": "🏙️"},
    {"task": "Players who have won a Ballon d'Or", "icon": "🟡"},
    {"task": "Legends who wore the Number 10 shirt", "icon": "🔟"},
    {"task": "Winners of the African Cup of Nations", "icon": "🐘"},
    {"task": "European clubs to have won a Treble", "icon": "✨"},
    {"task": "Italian 🇮🇹 clubs to play in the UCL", "icon": "🇮🇹"},
    {"task": "Played for both Bayern Munich & Real Madrid", "icon": "👑"},
    {"task": "Famous Left-footed Footballers", "icon": "🦶"},
    {"task": "Goalkeepers with 100+ PL Clean Sheets", "icon": "🧤"},
    {"task": "Major Stadiums in South America", "icon": "🏜️"},
    {"task": "Former Captains of Arsenal FC", "icon": "🔫"},
    {"task": "Played in 4 or more World Cup editions", "icon": "🌎"},
    {"task": "Clubs that wear Red & White Home Kits", "icon": "🔴⚪"},
    {"task": "Clubs currently in the German 🇩🇪 Bundesliga", "icon": "🍺"},
    {"task": "Argentinian 🇦🇷 scorers in the PL", "icon": "🇦🇷"},
    {"task": "Belgian 🇧🇪 players to win the UCL", "icon": "🇧🇪"}
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
    st.session_state.max_dice = 3
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
    board = [{"task": "STARTING LINE", "icon": "🏁"}]
    
    # Random sample to ensure uniqueness on the grid
    if total_squares - 2 <= len(CRITERIA_POOL):
        random_pool = random.sample(CRITERIA_POOL, total_squares - 2)
    else:
        random_pool = random.sample(CRITERIA_POOL * 2, total_squares - 2)
        
    board.extend(random_pool)
    board.append({"task": "FINISH LINE", "icon": "🏆"})
    
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
    st.title("🏟️ Football Path Trivia Setup")
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        st.session_state.grid_size = col1.selectbox("Board Dimensions", [3, 4, 5, 6], index=1)
        st.session_state.num_players = col2.number_input("Number of Players", 1, 4, 2)
        # Changed Max Dice Roll to a Dropdown
        st.session_state.max_dice = col3.selectbox("Max Dice Roll", [1, 2, 3, 4, 5, 6], index=2)
    
    st.subheader("👥 Player Entry")
    name_cols = st.columns(st.session_state.num_players)
    st.session_state.player_names = [name_cols[i].text_input(f"Player {i+1}", key=f"n_{i}") for i in range(st.session_state.num_players)]
    
    if st.button("🚀 KICK OFF", use_container_width=True, type="primary"):
        start_game()
        st.rerun()

else:
    player_id = st.session_state.turn
    player = st.session_state.player_data[player_id]
    
    # CSS for Grid Layout and Player Tokens
    player_tags_css = "".join([f".p-tag-{i} {{ background: {PLAYER_COLORS[i]}; color: white; border-radius: 50%; width: 30px; height: 30px; display: inline-flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: bold; margin: 3px; border: 2px solid white; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}" for i in range(4)])
    st.markdown(f"<style>.grid-container {{ display: grid; gap: 15px; margin-bottom: 20px; }}.grid-item {{ background: linear-gradient(145deg, #1e2129, #111318); border: 1px solid #333; border-radius: 15px; padding: 15px; text-align: center; min-height: 140px; display: flex; flex-direction: column; justify-content: center; transition: 0.2s; }}.grid-item:hover {{ border-color: #555; }}.active-sq {{ border: 3px solid {player['color']} !important; box-shadow: 0 0 20px {player['color']}66; }}.task-text {{ font-weight: 700; font-size: 0.95rem; color: #ffffff; margin: 8px 0; line-height: 1.2; }}.task-icon {{ font-size: 1.4rem; }}{player_tags_css}</style>", unsafe_allow_html=True)

    # Grid Display
    cols = st.session_state.grid_size
    grid_html = f'<div class="grid-container" style="grid-template-columns: repeat({cols}, 1fr);">'
    for i, item in enumerate(st.session_state.grid_map):
        is_active = "active-sq" if i == player['pos'] else ""
        markers = "".join([f'<span class="p-tag-{p_id}">{p["initials"]}</span>' for p_id, p in st.session_state.player_data.items() if p['pos'] == i])
        grid_html += f'<div class="grid-item {is_active}"><div style="color: #666; font-size: 0.7rem; margin-bottom: 5px;">#{i}</div><div class="task-icon">{item["icon"]}</div><div class="task-text">{item["task"]}</div><div style="min-height: 35px;">{markers}</div></div>'
    st.markdown(grid_html + '</div>', unsafe_allow_html=True)

    # Sidebar Match Center
    with st.sidebar:
        st.markdown(f"### ⚡ Match Center")
        with st.container(border=True):
            st.markdown(f"<p style='text-align: center; color: #888; margin-bottom:0;'>ACTIVE PLAYER</p><h2 style='color: {player['color']}; text-align: center; margin-top:0;'>{player['name']}</h2>", unsafe_allow_html=True)
            if not st.session_state.rolled:
                if st.button(f"🎲 ROLL DICE", use_container_width=True, type="primary"):
                    with st.spinner("Rolling..."): time.sleep(0.8)
                    st.session_state.current_roll = random.randint(1, st.session_state.max_dice)
                    player['prev'] = player['pos']
                    player['pos'] = min(player['pos'] + st.session_state.current_roll, len(st.session_state.grid_map)-1)
                    st.session_state.rolled = True
                    st.rerun()
            else:
                st.markdown(f"<div style='text-align: center; font-size: 4.5rem; font-weight: 800;'>{st.session_state.current_roll}</div>", unsafe_allow_html=True)
                st.info(f"**Target:** {st.session_state.grid_map[player['pos']]['task']}")
                st.markdown(f"<p style='text-align: center; font-size: 1.1rem; color: #FFD700;'>Provide <b>{st.session_state.current_roll}</b> correct answers!</p>", unsafe_allow_html=True)

        if st.session_state.rolled:
            st.markdown("### 🏁 Referee's Decision")
            c_yes, c_no = st.columns(2)
            if c_yes.button("✅ Correct", use_container_width=True):
                st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players
                st.session_state.rolled = False
                st.rerun()
            if c_no.button("❌ Wrong", use_container_width=True):
                player['pos'] = player['prev']
                st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players
                st.session_state.rolled = False
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if not st.session_state.confirm_reset:
            if st.button("🚩 End Session", use_container_width=True):
                st.session_state.confirm_reset = True
                st.rerun()
        else:
            st.error("End session?")
            cy, cn = st.columns(2)
            if cy.button("Yes", type="primary", use_container_width=True):
                st.session_state.game_started = False
                st.session_state.confirm_reset = False
                st.rerun()
            if cn.button("No", use_container_width=True):
                st.session_state.confirm_reset = False
                st.rerun()

    if player['pos'] == len(st.session_state.grid_map) - 1 and not st.session_state.rolled:
        st.balloons()
        st.success(f"🎊 {player['name']} IS THE CHAMPION!")
