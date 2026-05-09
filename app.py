import streamlit as st
import random
import re

# --- 1. DATA MAPPING ---
COUNTRY_DATA = {
    "French": "fr", "Spanish": "es", "English": "gb-eng", "Portuguese": "pt",
    "Dutch": "nl", "Belgian": "be", "German": "de", "Italian": "it",
    "Croatian": "hr", "Swiss": "ch", "Danish": "dk", "Turkish": "tr",
    "Austrian": "at", "Ukrainian": "ua", "Scottish": "gb-sct", "Swedish": "se",
    "Welsh": "gb-wls", "Polish": "pl", "Norwegian": "no", "Argentinian": "ar",
    "Brazilian": "br", "Colombian": "co", "Uruguayan": "uy", "Ecuadorian": "ec",
    "Moroccan": "ma", "Senegalese": "sn", "Nigerian": "ng", "Egyptian": "eg",
    "Ivorian": "ci", "Algerian": "dz", "American": "us", "Mexican": "mx",
    "Canadian": "ca", "Japanese": "jp", "South Korean": "kr", "Australian": "au"
}

ESPN_LOGOS = {
    "Man Utd": "360", "Liverpool": "364", "Arsenal": "359", 
    "Chelsea": "363", "Man City": "382", "Tottenham": "367",
    "Aston Villa": "362", "Newcastle": "361", "Real Madrid": "86", "Barcelona": "83", 
    "Atletico Madrid": "1068", "Sevilla": "243", "Villarreal": "102", "AC Milan": "103", 
    "Juventus": "111", "Inter Milan": "110", "AS Roma": "104", "Napoli": "114", 
    "Bayern Munich": "132", "Dortmund": "124", "Leverkusen": "131", "PSG": "160", 
    "Marseille": "176", "Monaco": "174", "Ajax": "139", "PSV Eindhoven": "148", 
    "Feyenoord": "142", "Benfica": "1929", "Porto": "437", "Sporting CP": "2250"
}

STADIUM_COUNTRIES = ["England", "Spain", "Germany", "Italy", "France", "Portugal", "Brazil", "Argentina", "Mexico"]

KIT_COLOR_MAP = {
    "Red": "🔴", "Blue": "🔵", "White": "⚪", "Yellow": "🟡", "Black & White": "🏁"
}

# --- 2. ASSET ENGINE ---
def get_assets(text):
    assets = {"logos": [], "flags": [], "emojis": []}
    if "stadium" in text.lower():
        assets["emojis"].append("🏟️")
    sorted_clubs = sorted(ESPN_LOGOS.keys(), key=len, reverse=True)
    found_ids = set()
    for club in sorted_clubs:
        if club.lower() in text.lower():
            espn_id = ESPN_LOGOS[club]
            if espn_id not in found_ids:
                assets["logos"].append(f"https://a.espncdn.com/i/teamlogos/soccer/500/{espn_id}.png")
                found_ids.add(espn_id)
    search_pool = {**COUNTRY_DATA, "England": "gb-eng", "Spain": "es", "Germany": "de", 
                   "Italy": "it", "France": "fr", "Portugal": "pt", "Brazil": "br", 
                   "Argentina": "ar", "Mexico": "mx"}
    for word, iso in search_pool.items():
        if word.lower() in clean_text_via_regex(text).lower():
            assets["flags"].append(f"https://flagcdn.com/w40/{iso}.png")
            break
    for color, emoji in KIT_COLOR_MAP.items():
        if color.lower() in text.lower():
            assets["emojis"].append(emoji)
            break
    return assets

def clean_text_via_regex(text):
    return re.sub(r'[^\w\s]', '', text)

def format_header_icons(assets, size_logos="24px", size_emojis="22px"):
    html = '<div style="display: flex; gap: 8px; justify-content: center; align-items: center; min-height: 30px; margin-bottom: 5px;">'
    for e in assets["emojis"]:
        html += f'<span style="font-size:{size_emojis};">{e}</span>'
    for f in assets["flags"]:
        html += f'<img src="{f}" style="height:18px; border-radius:2px; border:1px solid #444;">'
    for l in assets["logos"]:
        html += f'<img src="{l}" style="height:{size_logos};">'
    if not any(assets.values()):
        return html + f'<span style="font-size:{size_emojis};">⚽</span></div>'
    return html + '</div>'

# --- 3. DYNAMIC LOGIC ---
def generate_random_task():
    nations = list(COUNTRY_DATA.keys())
    clubs_list = list(ESPN_LOGOS.keys())
    manager_clubs = ['Real Madrid', 'Chelsea', 'Bayern Munich', 'PSG', 'Juventus', 'Barcelona', 'Inter Milan', 'Man Utd', 'Liverpool', 'AC Milan']
    nation = random.choice(nations)
    article = "an" if nation[0].lower() in ['a', 'e', 'i', 'o', 'u'] else "a"
    pair = random.sample(clubs_list, 2)
    templates = [
        lambda: f"Name a player who played for both {pair[0]} & {pair[1]}",
        lambda: f"Name a {random.choice(['Brazilian', 'French', 'Spanish', 'Dutch', 'Argentinian', 'Portuguese', 'German', 'Italian'])} player who played for {random.choice(clubs_list)}",
        lambda: f"Name {article} {nation} player who has played in the Champions League",
        lambda: f"Name a manager who managed {random.choice(manager_clubs)}",
        lambda: f"Name a stadium located in {random.choice(STADIUM_COUNTRIES)}",
        lambda: f"Name a football team whose primary home kit color is {random.choice(list(KIT_COLOR_MAP.keys()))}"
    ]
    return random.choice(templates)()

# --- 4. STATE MANAGEMENT ---
def reset_all_data():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

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
    board = [{"task": "KICK OFF", "assets": {"flags":[], "logos":[], "emojis":["🏁"]}}]
    unique_tasks = set()
    while len(unique_tasks) < (total_sq - 2):
        new_task = generate_random_task()
        if "both" in new_task:
            parts = new_task.split("both ")[1].split(" & ")
            new_task = f"Name a player who played for both {min(parts)} & {max(parts)}"
        unique_tasks.add(new_task)
    for task_text in list(unique_tasks):
        board.append({"task": task_text, "assets": get_assets(task_text)})
    board.append({"task": "FINAL WHISTLE", "assets": {"flags":[], "logos":[], "emojis":["🏆"]}})
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

# --- 5. UI ---
st.set_page_config(page_title="Football Path Trivia", layout="wide")

if st.session_state.winner:
    st.balloons()
    st.markdown(f"<div style='text-align:center; padding:100px;'><h1 style='font-size:5rem;'>🏆</h1><h2 style='color:{st.session_state.winner['color']};'>Congratulations {st.session_state.winner['name']}!</h2></div>", unsafe_allow_html=True)
    if st.button("🏟️ Return to Menu", use_container_width=True): reset_all_data()

elif not st.session_state.game_started:
    st.title("⚽ Football Path Setup")
    with st.container(border=True):
        c1, c2 = st.columns(2)
        st.session_state.grid_size = c1.number_input("Grid Size", 3, 6, 4)
        st.session_state.num_players = c2.number_input("Players", 1, 4, 2)
    cols = st.columns(st.session_state.num_players)
    st.session_state.player_names = [cols[i].text_input(f"Manager {i+1}", key=f"p{i}") for i in range(st.session_state.num_players)]
    if st.button("🚀 START MATCH", use_container_width=True, type="primary"): start_game(); st.rerun()

else:
    player = st.session_state.player_data[st.session_state.turn]
    st.markdown(f"""
        <style>
        .grid-container {{ display: grid; gap: 12px; grid-template-columns: repeat({st.session_state.grid_size}, 1fr); }}
        .grid-item {{ background: #1e2129; border: 1px solid #333; border-radius: 12px; padding: 12px; text-align: center; min-height: 150px; display: flex; flex-direction: column; align-items: center; justify-content: space-between; }}
        .active-sq {{ border: 3px solid {player['color']}; box-shadow: 0 0 15px {player['color']}55; }}
        .p-tag {{ border-radius: 50%; width: 28px; height: 28px; display: inline-flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: 800; border: 2px solid #fff; margin: 1px; }}
        </style>
    """, unsafe_allow_html=True)

    grid_html = '<div class="grid-container">'
    for i, item in enumerate(st.session_state.grid_map):
        active = "active-sq" if i == player['pos'] else ""
        marks = "".join([f'<span class="p-tag" style="background:{p["color"]}">{p["initials"]}</span>' for pid, p in st.session_state.player_data.items() if p['pos'] == i])
        grid_html += f'<div class="grid-item {active}"><div style="width:100%; color:#555; font-size:0.7rem; text-align:left;">#{i:02}</div>{format_header_icons(item["assets"])}<div style="color:#eee; font-weight:600; font-size:0.85rem; line-height:1.2;">{item["task"]}</div><div style="min-height:35px; display:flex; justify-content:center; align-items:center;">{marks}</div></div>'
    st.markdown(grid_html + "</div>", unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(f"<h2 style='text-align:center; color:{player['color']}; margin-bottom: 20px;'>{player['name']}</h2>", unsafe_allow_html=True)
        
        if not st.session_state.rolled:
            if st.button("🎲 ROLL DICE", use_container_width=True, type="primary"):
                st.session_state.current_roll = random.randint(1, 3)
                player['prev'], player['pos'] = player['pos'], min(player['pos'] + st.session_state.current_roll, len(st.session_state.grid_map)-1)
                if player['pos'] == len(st.session_state.grid_map)-1:
                    t = generate_random_task()
                    st.session_state.active_final_task = {"text": t, "assets": get_assets(t)}
                st.session_state.rolled = True
                st.rerun()
        else:
            st.markdown(f"<div style='text-align:center; font-size:4rem; font-weight:800; margin-bottom:10px;'>{st.session_state.current_roll}</div>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center; color:#aaa; margin-bottom:5px;'>Provide <b>{st.session_state.current_roll}</b> answers for:</p>", unsafe_allow_html=True)
            
            # SIDEBAR ASSETS ADDED HERE
            current_assets = st.session_state.active_final_task['assets'] if player['pos'] == len(st.session_state.grid_map)-1 else st.session_state.grid_map[player['pos']]['assets']
            st.markdown(format_header_icons(current_assets, size_logos="32px", size_emojis="28px"), unsafe_allow_html=True)
            
            task_text = st.session_state.active_final_task['text'] if player['pos'] == len(st.session_state.grid_map)-1 else st.session_state.grid_map[player['pos']]['task']
            st.markdown(f"<div style='text-align:center; font-size:1.1rem; font-style:italic; font-weight:600; padding: 15px; margin-bottom: 25px; border-radius:8px; background:#262730; border: 1px solid #444;'>{task_text}</div>", unsafe_allow_html=True)

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

        st.markdown("<br><hr><br>", unsafe_allow_html=True)
        if not st.session_state.confirm_reset:
            if st.button("🚩 End Match", use_container_width=True): st.session_state.confirm_reset = True; st.rerun()
        else:
            st.error("Quit Match?")
            cy, cn = st.columns(2)
            if cy.button("Yes", use_container_width=True): reset_all_data()
            if cn.button("No", use_container_width=True): st.session_state.confirm_reset = False; st.rerun()
