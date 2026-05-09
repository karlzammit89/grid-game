import streamlit as st
import random
import time

# --- 1. GLOBAL FLAG MAPPING ---
# Comprehensive mapping for footballing nations and adjectives
FLAG_MAP = {
    # Europe
    "Spanish": "🇪🇸", "Spain": "🇪🇸", "English": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "England": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    "Italian": "🇮🇹", "Italy": "🇮🇹", "German": "🇩🇪", "Germany": "🇩🇪",
    "French": "🇫🇷", "France": "🇫🇷", "Portuguese": "🇵🇹", "Portugal": "🇵🇹",
    "Dutch": "🇳🇱", "Netherlands": "🇳🇱", "Croatian": "🇭🇷", "Croatia": "🇭🇷",
    "Belgian": "🇧🇪", "Belgium": "🇧🇪", "Turkish": "🇹🇷", "Turkey": "🇹🇷",
    "Scottish": "🏴󠁧󠁢󠁳󠁣󠁴󠁿", "Scotland": "🏴󠁧󠁢󠁳󠁣󠁴󠁿", "Welsh": "🏴󠁧󠁢󠁷󠁬󠁳󠁿", "Wales": "🏴󠁧󠁢󠁷󠁬󠁳󠁿",
    "Swiss": "🇨🇭", "Switzerland": "🇨🇭", "Danish": "🇩🇰", "Denmark": "🇩🇰",
    "Swedish": "🇸🇪", "Sweden": "🇸🇪", "Norwegian": "🇳🇴", "Norway": "🇳🇴",
    "Polish": "🇵🇱", "Poland": "🇵🇱", "Austrian": "🇦🇹", "Austria": "🇦🇹",
    "Greek": "🇬🇷", "Greece": "🇬🇷", "Ukrainian": "🇺🇦", "Ukraine": "🇺🇦",
    # South America
    "Brazilian": "🇧🇷", "Brazil": "🇧🇷", "Argentinian": "🇦🇷", "Argentina": "🇦🇷",
    "Uruguayan": "🇺🇾", "Uruguay": "🇺🇾", "Colombian": "🇨🇴", "Colombia": "🇨🇴",
    "Chilean": "🇨🇱", "Chile": "🇨🇱", "Paraguayan": "🇵🇾", "Paraguay": "🇵🇾",
    # Africa
    "African": "🌍", "Egyptian": "🇪🇬", "Egypt": "🇪🇬", "Senegalese": "🇸🇳", "Senegal": "🇸🇳",
    "Moroccan": "🇲🇦", "Morocco": "🇲🇦", "Nigerian": "🇳🇬", "Nigeria": "🇳🇬",
    "Ivorian": "🇨🇮", "Ivory Coast": "🇨🇮", "Cameroonian": "🇨🇲", "Cameroon": "🇨🇲",
    "Algerian": "🇩🇿", "Algeria": "🇩🇿", "Ghanaian": "🇬🇭", "Ghana": "🇬🇭",
    # Others
    "American": "🇺🇸", "USA": "🇺🇸", "Mexican": "🇲🇽", "Mexico": "🇲🇽",
    "Japanese": "🇯🇵", "Japan": "🇯🇵", "Korean": "🇰🇷", "South Korea": "🇰🇷",
    "Australian": "🇦🇺", "Australia": "🇦🇺"
}

def inject_flags(text):
    """Automatically detects country keywords and appends the correct flag."""
    for word, emoji in FLAG_MAP.items():
        # Check for word boundaries to avoid partial matches (e.g., 'A' in 'Arsenal')
        if f" {word} " in f" {text} " and emoji not in text:
            return f"{text} {emoji}"
    return text

# --- 2. EXPANDED CRITERIA POOL ---
CRITERIA_POOL = [
    {"task": "Played for both Barcelona & Inter", "icon": "🔵🔴"},
    {"task": "Name a Spanish Stadium", "icon": "🏟️"},
    {"task": "Croatians to win the UCL", "icon": "🇭🇷"},
    {"task": "Teams with 3+ English 2nd Div Titles", "icon": "🏆"},
    {"task": "Brazilians to play for Man City", "icon": "🇧🇷"},
    {"task": "Teams currently in the Liga Portugal", "icon": "🇵🇹"},
    {"task": "Played for both AC Milan & Chelsea", "icon": "🔴⚫"},
    {"task": "African players to play for PSG", "icon": "🌍"},
    {"task": "Man Utd players to win a World Cup", "icon": "👹"},
    {"task": "Uruguayans to score in a World Cup", "icon": "🇺🇾"},
    {"task": "Players in France's 2018 WC Squad", "icon": "🇫🇷"},
    {"task": "German players to win a Golden Boot", "icon": "🇩🇪"},
    {"task": "Dutch players to play for Man Utd", "icon": "🇳🇱"},
    {"task": "Italian clubs to play in the UCL", "icon": "🇮🇹"},
    {"task": "Argentinian scorers in the PL", "icon": "🇦🇷"},
    {"task": "Belgian players to win the UCL", "icon": "🇧🇪"},
    {"task": "Portuguese players to play for Wolves", "icon": "🐺"},
    {"task": "Turkish clubs in the Super Lig", "icon": "🇹🇷"},
    {"task": "Scottish players to play in the Premier League", "icon": "🏴󠁧󠁢󠁳󠁣󠁴󠁿"},
    {"task": "Mexican players who played in Europe", "icon": "🇲🇽"},
    {"task": "Senegalese players to score in the PL", "icon": "🇸🇳"},
    {"task": "Moroccan players to play in La Liga", "icon": "🇲🇦"},
    {"task": "Japanese players in the Bundesliga", "icon": "🇯🇵"},
    {"task": "Swiss players to win a major trophy", "icon": "🇨🇭"},
    {"task": "Colombian goalscorers in Europe", "icon": "🇨🇴"},
    {"task": "Swedish players to play for AC Milan", "icon": "🇸🇪"},
    {"task": "Nigerian players to play for Arsenal", "icon": "🦅"},
    {"task": "Danish players to play for Man Utd", "icon": "🇩🇰"},
    {"task": "Ivorian legends in the Premier League", "icon": "🇨🇮"},
    {"task": "Greek clubs to play in European competitions", "icon": "🇬🇷"}
]

# --- 3. STATE MANAGEMENT & GAMEPLAY ---
if 'game_started' not in st.session_state:
    st.session_state.update({
        'game_started': False, 'grid_size': 4, 'max_dice': 3,
        'num_players': 2, 'player_names': [], 'player_data': {},
        'turn': 0, 'rolled': False, 'current_roll': 0, 
        'grid_map': [], 'confirm_reset': False
    })

def start_game():
    total_sq = st.session_state.grid_size ** 2
    board = [{"task": "KICK OFF", "icon": "🏁"}]
    
    # Select unique tasks and apply auto-flag injection
    pool = random.sample(CRITERIA_POOL, min(len(CRITERIA_POOL), total_sq - 2))
    for item in pool:
        item["task"] = inject_flags(item["task"])
        
    board.extend(pool)
    board.append({"task": "FINAL WHISTLE", "icon": "🏆"})
    
    st.session_state.grid_map = board
    st.session_state.player_data = {
        i: {
            "pos": 0, "prev": 0, 
            "name": st.session_state.player_names[i] or f"Manager {i+1}",
            "initials": get_initials(st.session_state.player_names[i] or f"M{i+1}"),
            "color": PLAYER_COLORS[i]
        } for i in range(st.session_state.num_players)
    }
    st.session_state.game_started = True

def get_initials(name):
    parts = name.split()
    return (parts[0][0] + parts[-1][0]).upper() if len(parts) >= 2 else name[:2].upper()

PLAYER_COLORS = ["#FF4B4B", "#1C83E1", "#00C04A", "#FFD700"]

# --- 4. UI RENDERING ---
st.set_page_config(page_title="Football Path Trivia", layout="wide")

if not st.session_state.game_started:
    st.title("⚽ Football Path Setup")
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        st.session_state.grid_size = c1.selectbox("Grid Size", [3, 4, 5, 6], index=1)
        st.session_state.num_players = c2.number_input("Players", 1, 4, 2)
        st.session_state.max_dice = c3.selectbox("Max Dice Roll", [1, 2, 3, 4, 5, 6], index=2)
    
    st.subheader("👤 Enter Manager Names")
    cols = st.columns(st.session_state.num_players)
    st.session_state.player_names = [cols[i].text_input(f"Manager {i+1}", key=f"p{i}") for i in range(st.session_state.num_players)]
    
    if st.button("🚀 START MATCH", use_container_width=True, type="primary"):
        start_game()
        st.rerun()

else:
    player = st.session_state.player_data[st.session_state.turn]
    
    # CSS for a polished look
    tags_css = "".join([f".p-tag-{i} {{ background: {PLAYER_COLORS[i]}; color: white; border-radius: 50%; width: 32px; height: 32px; display: inline-flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: 800; margin: 2px; border: 2px solid #fff; }}" for i in range(4)])
    st.markdown(f"<style>.grid-container {{ display: grid; gap: 12px; }}.grid-item {{ background: #1e2129; border: 1px solid #333; border-radius: 12px; padding: 15px; text-align: center; min-height: 140px; display: flex; flex-direction: column; justify-content: space-between; }}.active-sq {{ border: 3px solid {player['color']}; box-shadow: 0 0 15px {player['color']}55; }}.task-text {{ font-weight: 600; font-size: 0.9rem; color: #eee; }}{tags_css}</style>", unsafe_allow_html=True)

    # Grid Display
    grid_html = f'<div class="grid-container" style="grid-template-columns: repeat({st.session_state.grid_size}, 1fr);">'
    for i, item in enumerate(st.session_state.grid_map):
        active = "active-sq" if i == player['pos'] else ""
        marks = "".join([f'<span class="p-tag-{pid}">{p["initials"]}</span>' for pid, p in st.session_state.player_data.items() if p['pos'] == i])
        grid_html += f'<div class="grid-item {active}"><div style="color:#555;font-size:0.7rem;text-align:left;">#{i:02}</div><div style="font-size:1.5rem;">{item["icon"]}</div><div class="task-text">{item["task"]}</div><div style="min-height:35px;">{marks}</div></div>'
    st.markdown(grid_html + "</div>", unsafe_allow_html=True)

    # Sidebar Controls
    with st.sidebar:
        st.markdown(f"### 🎙️ Match Center")
        with st.container(border=True):
            st.markdown(f"<h3 style='color:{player['color']}; text-align:center;'>{player['name']}</h3>", unsafe_allow_html=True)
            if not st.session_state.rolled:
                if st.button("🎲 ROLL DICE", use_container_width=True, type="primary"):
                    st.session_state.current_roll = random.randint(1, st.session_state.max_dice)
                    player['prev'], player['pos'] = player['pos'], min(player['pos'] + st.session_state.current_roll, len(st.session_state.grid_map)-1)
                    st.session_state.rolled = True
                    st.rerun()
            else:
                st.markdown(f"<div style='text-align:center; font-size:4rem; font-weight:800;'>{st.session_state.current_roll}</div>", unsafe_allow_html=True)
                st.info(f"Target: {st.session_state.grid_map[player['pos']]['task']}")

        if st.session_state.rolled:
            st.markdown("### 🏁 Referee's Decision")
            cy, cn = st.columns(2)
            if cy.button("✅ Correct", use_container_width=True):
                st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players
                st.session_state.rolled = False
                st.rerun()
            if cn.button("❌ Wrong", use_container_width=True):
                player['pos'] = player['prev']
                st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players
                st.session_state.rolled = False
                st.rerun()

        st.markdown("---")
        if not st.session_state.confirm_reset:
            if st.button("🚩 End Session", use_container_width=True):
                st.session_state.confirm_reset = True
                st.rerun()
        else:
            st.error("Abandon Match?")
            ry, rn = st.columns(2)
            if ry.button("Yes", use_container_width=True, type="primary"):
                st.session_state.game_started = False
                st.session_state.confirm_reset = False
                st.rerun()
            if rn.button("No", use_container_width=True):
                st.session_state.confirm_reset = False
                st.rerun()

    if player['pos'] == len(st.session_state.grid_map) - 1 and not st.session_state.rolled:
        st.balloons()
        st.success(f"🏆 {player['name']} Wins!")
