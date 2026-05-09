import streamlit as st
import random
import time
import re

# --- 1. COMPREHENSIVE FLAG IMAGE MAPPING ---
# Maps keywords and adjectives to ISO codes for FlagCDN
COUNTRY_DATA = {
    "Spanish": "es", "Spain": "es", "English": "gb-eng", "England": "gb-eng",
    "Italian": "it", "Italy": "it", "German": "de", "Germany": "de",
    "French": "fr", "France": "fr", "Portuguese": "pt", "Portugal": "pt",
    "Dutch": "nl", "Netherlands": "nl", "Croatian": "hr", "Croatia": "hr",
    "Belgian": "be", "Belgium": "be", "Turkish": "tr", "Turkey": "tr",
    "Scottish": "gb-sct", "Scotland": "gb-sct", "Welsh": "gb-wls", "Wales": "gb-wls",
    "Brazilian": "br", "Brazil": "br", "Argentinian": "ar", "Argentina": "ar",
    "Uruguayan": "uy", "Uruguay": "uy", "Egyptian": "eg", "Egypt": "eg",
    "Senegalese": "sn", "Senegal": "sn", "Moroccan": "ma", "Morocco": "ma",
    "Nigerian": "ng", "Nigeria": "ng", "Japanese": "jp", "Japan": "jp",
    "Mexican": "mx", "Mexico": "mx", "Colombian": "co", "Colombia": "co",
    "American": "us", "USA": "us", "Ivorian": "ci", "Ivory Coast": "ci",
    "Ghanaian": "gh", "Ghana": "gh", "Cameroonian": "cm", "Cameroon": "cm",
    "Algerian": "dz", "Algeria": "dz", "Swiss": "ch", "Switzerland": "ch",
    "Danish": "dk", "Denmark": "dk", "Swedish": "se", "Sweden": "se",
    "Polish": "pl", "Poland": "pl", "Norwegian": "no", "Norway": "no",
    "Chilean": "cl", "Chile": "cl", "South Korean": "kr", "Korea": "kr",
    "Australian": "au", "Australia": "au", "Greek": "gr", "Greece": "gr",
    "Ukrainian": "ua", "Ukraine": "ua", "Austrian": "at", "Austria": "at"
}

def clean_and_get_flag(item):
    """
    1. Removes existing emoji characters/codes from the task text.
    2. Returns the clean text and a flag URL if a country is found.
    """
    text = item["task"]
    # Regex to remove common emoji patterns/placeholders that might show as "AR" or "CI"
    text = re.sub(r'[^\x00-\x7F]+', '', text).strip() 
    
    flag_url = None
    for word, iso in COUNTRY_DATA.items():
        if word.lower() in text.lower():
            flag_url = f"https://flagcdn.com/w80/{iso}.png"
            break
            
    return text, flag_url

# --- 2. CRITERIA POOL ---
CRITERIA_POOL = [
    {"task": "Played for both Barcelona & Inter", "icon": "🔵🔴"},
    {"task": "Name a Spanish Stadium", "icon": "🏟️"},
    {"task": "Croatians to win the UCL", "icon": "🥇"},
    {"task": "Teams with 3+ English 2nd Div Titles", "icon": "🏆"},
    {"task": "Brazilians to play for Man City", "icon": "⚽"},
    {"task": "Teams currently in the Liga Portugal", "icon": "🇵🇹"},
    {"task": "Played for both AC Milan & Chelsea", "icon": "🤝"},
    {"task": "African players to play for PSG", "icon": "🌍"},
    {"task": "Man Utd players to win a World Cup", "icon": "👹"},
    {"task": "Uruguayans to score in a World Cup", "icon": "🇺🇾"},
    {"task": "Players in France's 2018 WC Squad", "icon": "🇫🇷"},
    {"task": "German players to win a Golden Boot", "icon": "👟"},
    {"task": "Dutch players to play for Man Utd", "icon": "🇳🇱"},
    {"task": "Italian clubs to play in the UCL", "icon": "🇮🇹"},
    {"task": "Argentinian scorers in the PL", "icon": "🇦🇷"},
    {"task": "Belgian players to win the UCL", "icon": "🇧🇪"},
    {"task": "Portuguese players to play for Wolves", "icon": "🐺"},
    {"task": "Turkish clubs in the Super Lig", "icon": "🇹🇷"},
    {"task": "Scottish players to play in the PL", "icon": "🏴󠁧󠁢󠁳󠁣󠁴󠁿"},
    {"task": "Japanese players in the Bundesliga", "icon": "🇯🇵"},
    {"task": "Ivorian legends in the Premier League", "icon": "🇨🇮"},
    {"task": "Greek clubs in European competition", "icon": "🏛️"},
    {"task": "Mexican players to play in La Liga", "icon": "🌮"},
    {"task": "Swedish players to play for AC Milan", "icon": "🇸🇪"},
    {"task": "American players in the Premier League", "icon": "🦅"}
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
    board = [{"task": "KICK OFF", "icon_url": None, "icon_emoji": "🏁"}]
    
    selected_tasks = random.sample(CRITERIA_POOL, min(len(CRITERIA_POOL), total_sq - 2))
    
    for item in selected_tasks:
        clean_text, flag_url = clean_and_get_flag(item)
        board.append({
            "task": clean_text,
            "icon_url": flag_url,
            "icon_emoji": item["icon"] if not flag_url else None
        })
        
    board.append({"task": "FINAL WHISTLE", "icon_url": None, "icon_emoji": "🏆"})
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
        .grid-item {{ background: #1e2129; border: 1px solid #333; border-radius: 12px; padding: 12px; text-align: center; min-height: 150px; display: flex; flex-direction: column; align-items: center; justify-content: space-between; }}
        .active-sq {{ border: 3px solid {player['color']}; box-shadow: 0 0 15px {player['color']}55; }}
        .p-tag {{ border-radius: 50%; width: 28px; height: 28px; display: inline-flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: 800; border: 2px solid #fff; margin: 1px; }}
        .flag-img {{ height: 35px; border-radius: 4px; margin-bottom: 5px; border: 1px solid #444; }}
        .icon-emoji {{ font-size: 2rem; margin-bottom: 5px; }}
        </style>
    """, unsafe_allow_html=True)

    grid_html = f'<div class="grid-container" style="grid-template-columns: repeat({st.session_state.grid_size}, 1fr);">'
    for i, item in enumerate(st.session_state.grid_map):
        active = "active-sq" if i == player['pos'] else ""
        marks = "".join([f'<span class="p-tag" style="background:{p["color"]}">{p["initials"]}</span>' for pid, p in st.session_state.player_data.items() if p['pos'] == i])
        
        # Determine if we show a flag image or an emoji icon
        if item.get("icon_url"):
            icon_html = f'<img src="{item["icon_url"]}" class="flag-img">'
        else:
            icon_html = f'<div class="icon-emoji">{item.get("icon_emoji", "⚽")}</div>'

        grid_html += f'''
            <div class="grid-item {active}">
                <div style="width:100%; color:#555; font-size:0.7rem; text-align:left;">#{i:02}</div>
                {icon_html}
                <div style="color:#eee; font-weight:600; font-size:0.85rem; line-height:1.2;">{item["task"]}</div>
                <div style="min-height:30px; display:flex; justify-content:center; align-items:center;">{marks}</div>
            </div>'''
    st.markdown(grid_html + "</div>", unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(f"<h2 style='color:{player['color']}; text-align:center;'>{player['name']}</h2>", unsafe_allow_html=True)
        if not st.session_state.rolled:
            if st.button("🎲 ROLL", use_container_width=True, type="primary"):
                st.session_state.current_roll = random.randint(1, st.session_state.max_dice)
                player['prev'], player['pos'] = player['pos'], min(player['pos'] + st.session_state.current_roll, len(st.session_state.grid_map)-1)
                st.session_state.rolled = True
                st.rerun()
        else:
            st.markdown(f"<div style='text-align:center; font-size:4rem; font-weight:800;'>{st.session_state.current_roll}</div>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;'><b>Task:</b> {st.session_state.grid_map[player['pos']]['task']}</p>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            if c1.button("✅ Yes", use_container_width=True):
                st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players
                st.session_state.rolled = False
                st.rerun()
            if c2.button("❌ No", use_container_width=True):
                player['pos'] = player['prev']
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

    if player['pos'] == len(st.session_state.grid_map) - 1 and not st.session_state.rolled:
        st.balloons()
        st.success(f"🏆 {player['name']} Wins!")
