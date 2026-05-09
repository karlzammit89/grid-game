import streamlit as st
import random
import time

# --- 1. CONFIGURATION & DATA ---
# Expanded Criteria Pool with a wide variety of fun/fair categories
CRITERIA_POOL = [
    {"task": "Barcelona & Inter", "icon": "🔵🔴"}, {"task": "Spanish Stadiums", "icon": "🏟️"},
    {"task": "Croatians to win UCL", "icon": "🇭🇷"}, {"task": "English 2nd Div Titles", "icon": "🏆"},
    {"task": "Predominantly White Kit", "icon": "👕"}, {"task": "Brazilian Man City Players", "icon": "🇧🇷"},
    {"task": "Portuguese League Teams", "icon": "🇵🇹"}, {"task": "AC Milan & Chelsea", "icon": "🔴⚫"},
    {"task": "Africans for PSG", "icon": "🌍"}, {"task": "Man Utd World Cup Winners", "icon": "👹"},
    {"task": "Uruguayan Goalscorers", "icon": "🇺🇾"}, {"task": "200+ Games under Mourinho", "icon": "👔"},
    {"task": "French World Cup 2018 Squad", "icon": "🇫🇷"}, {"task": "Played for both Real & Barca", "icon": "⚔️"},
    {"task": "German Golden Boot Winners", "icon": "🇩🇪"}, {"task": "Champions League Finalists (Non-Winners)", "icon": "🥈"},
    {"task": "Players with 100+ PL Goals", "icon": "⚽"}, {"task": "Clubs from London", "icon": "🏴󠁧󠁢󠁥󠁮󠁧󠁿"},
    {"task": "Dutch players for Man Utd", "icon": "🇳🇱"}, {"task": "Clubs with 'City' in name", "icon": "🏙️"},
    {"task": "Ballon d'Or Winners", "icon": "🟡"}, {"task": "Players who wore Number 10", "icon": "🔟"},
    {"task": "African Cup of Nations Winners", "icon": "🐘"}, {"task": "Teams that have won the Treble", "icon": "✨"},
    {"task": "Italian clubs in Champions League", "icon": "🇮🇹"}, {"task": "Players who played for Bayern & Real", "icon": "👑"},
    {"task": "Left-footed Legends", "icon": "🦶"}, {"task": "Goalkeepers with PL Clean Sheets", "icon": "🧤"},
    {"task": "South American Stadiums", "icon": "🏜️"}, {"task": "Former Arsenal Captains", "icon": "🔫"},
    {"task": "Players who played in 4+ World Cups", "icon": "🌎"}, {"task": "Clubs with Red & White Kits", "icon": "🔴⚪"},
    {"task": "Premier League Managers (Active)", "icon": "📋"}, {"task": "Teams with Blue Home Kits", "icon": "🔵"}
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
    board = [{"task": "START", "icon": "🏁"}]
    
    # Ensure unique categories by sampling without replacement
    # If grid is larger than pool, it will allow some repeats but prioritize uniqueness
    if total_squares - 2 <= len(CRITERIA_POOL):
        random_pool = random.sample(CRITERIA_POOL, total_squares - 2)
    else:
        random_pool = random.sample(CRITERIA_POOL * 2, total_squares - 2)
        
    board.extend(random_pool)
    board.append({"task": "FINISH", "icon": "🏆"})
    
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
        st.session_state.max_dice = col3.slider("Max Dice Roll", 1, 6, 3)
    
    st.subheader("👥 Player Entry")
    name_cols = st.columns(st.session_state.num_players)
    st.session_state.player_names = [name_cols[i].text_input(f"Player {i+1}", key=f"n_{i}") for i in range(st.session_state.num_players)]
    
    if st.button("🚀 KICK OFF", use_container_width=True, type="primary"):
        start_game()
        st.rerun()

else:
    player_id = st.session_state.turn
    player = st.session_state.player_data[player_id]
    
    # Grid Styling
    player_tags_css = "".join([f".p-tag-{i} {{ background: {PLAYER_COLORS[i]}; color: white; border-radius: 50%; width: 30px; height: 30px; display: inline-flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: bold; margin: 3px; border: 2px solid white; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}" for i in range(4)])
    st.markdown(f"<style>.grid-container {{ display: grid; gap: 15px; margin-bottom: 20px; }}.grid-item {{ background: linear-gradient(145deg, #1e2129, #111318); border: 1px solid #333; border-radius: 15px; padding: 20px; text-align: center; min-height: 120px; transition: all 0.3s ease; display: flex; flex-direction: column; justify-content: space-between; }}.grid-item:hover {{ border-color: #555; transform: translateY(-2px); }}.active-sq {{ border: 3px solid {player['color']} !important; box-shadow: 0 0 20px {player['color']}66; background: linear-gradient(145deg, #252a34, #161a22) !important; }}.task-text {{ font-weight: 700; font-size: 1rem; color: #ffffff; margin: 5px 0; }}.task-icon {{ font-size: 1.5rem; }}{player_tags_css}</style>", unsafe_allow_html=True)

    # Board Display
    cols = st.session_state.grid_size
    grid_html = f'<div class="grid-container" style="grid-template-columns: repeat({cols}, 1fr);">'
    for i, item in enumerate(st.session_state.grid_map):
        is_active = "active-sq" if i == player['pos'] else ""
        markers = "".join([f'<span class="p-tag-{p_id}">{p["initials"]}</span>' for p_id, p in st.session_state.player_data.items() if p['pos'] == i])
        grid_html += f'<div class="grid-item {is_active}"><div style="color: #666; font-size: 0.75rem; text-align: left;">#{i}</div><div class="task-icon">{item["icon"]}</div><div class="task-text">{item["task"]}</div><div style="min-height: 35px;">{markers}</div></div>'
    st.markdown(grid_html + '</div>', unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown(f"### ⚡ Match Center")
        with st.container(border=True):
            st.markdown(f"<p style='text-align: center; color: #888; margin-bottom:0;'>PLAYER TO ACT</p><h2 style='color: {player['color']}; text-align: center; margin-top:0;'>{player['name']}</h2>", unsafe_allow_html=True)
            if not st.session_state.rolled:
                if st.button(f"🎲 ROLL DICE", use_container_width=True, type="primary"):
                    with st.spinner("Rolling..."):
                        time.sleep(1)
                    st.session_state.current_roll = random.randint(1, st.session_state.max_dice)
                    player['prev'] = player['pos']
                    player['pos'] = min(player['pos'] + st.session_state.current_roll, len(st.session_state.grid_map)-1)
                    st.session_state.rolled = True
                    st.rerun()
            else:
                st.markdown(f"<div style='text-align: center; font-size: 4.5rem; font-weight: 800; line-height: 1;'>{st.session_state.current_roll}</div>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: center; font-size: 1.1rem;'>Goal: Name <b>{st.session_state.current_roll}</b> answers!</p>", unsafe_allow_html=True)

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
            st.error("Are you sure?")
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
        st.success(f"🎊 {player['name']} IS THE CHAMPION!")
