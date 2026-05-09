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
    "Red": "🔴", "Blue": "🔵", "White": "⚪", "Yellow": "🟡", "Green": "🟢", "Black": "⚫"
}

# Regional Groups for Smart Mapping
SOUTH_AMERICANS = ["Argentinian", "Brazilian", "Colombian", "Uruguayan", "Ecuadorian"]
EUROPEANS = [
    "French", "Spanish", "English", "Portuguese", "Dutch", "Belgian", "German", 
    "Italian", "Croatian", "Swiss", "Danish", "Turkish", "Austrian", "Ukrainian", 
    "Scottish", "Swedish", "Welsh", "Polish", "Norwegian"
]

COMPETITION_GEOGRAPHY = {
    "Champions League": "eu", "Europa League": "eu", "Euros": "eu",
    "World Cup": "world", "Copa America": "world",
    "Premier League": "gb-eng", "Championship": "gb-eng", "FA Cup": "gb-eng",
    "La Liga": "es", "Serie A": "it", "Bundesliga": "de", "Ligue 1": "fr"
}

# --- 2. ASSET ENGINE ---
def get_assets(text):
    assets = {"logos": [], "flags": [], "emojis": []}
    
    for comp, geo in COMPETITION_GEOGRAPHY.items():
        if comp.lower() in text.lower():
            if geo == "world":
                if "🌍" not in assets["emojis"]: assets["emojis"].append("🌍")
            else:
                assets["flags"].append(f"https://flagcdn.com/w40/{geo}.png")
            break

    sorted_clubs = sorted(ESPN_LOGOS.keys(), key=len, reverse=True)
    found_ids = set()
    for club in sorted_clubs:
        if club.lower() in text.lower():
            espn_id = ESPN_LOGOS[club]
            if espn_id not in found_ids:
                assets["logos"].append(f"https://a.espncdn.com/i/teamlogos/soccer/500/{espn_id}.png")
                found_ids.add(espn_id)
                
    if not assets["flags"]:
        search_pool = {**COUNTRY_DATA, "England": "gb-eng", "Spain": "es", "Germany": "de", "Italy": "it", "France": "fr", "Portugal": "pt", "Brazil": "br", "Argentina": "ar", "Mexico": "mx"}
        for word, iso in search_pool.items():
            if word.lower() in re.sub(r'[^\w\s]', '', text).lower():
                assets["flags"].append(f"https://flagcdn.com/w40/{iso}.png")
                break
            
    return assets

def format_header_icons(assets):
    html = '<div style="display: flex; gap: 8px; justify-content: center; align-items: center; min-height: 25px; margin: 5px 0;">'
    for e in list(dict.fromkeys(assets["emojis"])):
        html += f'<span style="font-size:20px;">{e}</span>'
    for f in assets["flags"]:
        html += f'<img src="{f}" style="height:14px; border-radius:2px; border:1px solid #444;">'
    for l in assets["logos"]:
        html += f'<img src="{l}" style="height:22px;">'
    return html + '</div>'

# --- 3. DYNAMIC LOGIC ---
def generate_random_task():
    all_nations = list(COUNTRY_DATA.keys())
    clubs_list = list(ESPN_LOGOS.keys())
    manager_clubs = ['Real Madrid', 'Chelsea', 'Bayern Munich', 'PSG', 'Juventus', 'Barcelona', 'Inter Milan', 'Man Utd', 'Liverpool', 'AC Milan']
    
    euro_only = ["Euros"]
    sa_only = ["Copa America"]
    global_comps = ["Champions League", "Europa League", "World Cup", "FA Cup", "Premier League", "Championship", "La Liga", "Serie A", "Bundesliga", "Ligue 1"]

    picker = random.random()
    if picker < 0.25:
        nation, comp = random.choice(EUROPEANS), random.choice(euro_only + global_comps)
    elif picker < 0.45:
        nation, comp = random.choice(SOUTH_AMERICANS), random.choice(sa_only + global_comps)
    else:
        nation, comp = random.choice(all_nations), random.choice(global_comps)

    article = "an" if nation[0].lower() in ['a', 'e', 'i', 'o', 'u'] else "a"
    pair = random.sample(clubs_list, 2)
    comp_display = f"the {comp}" if comp not in ["La Liga", "Serie A", "Bundesliga", "Ligue 1"] else comp
    
    templates = [
        lambda: f"Name a player who played for both {pair[0]} & {pair[1]}",
        lambda: f"Name a {random.choice(['Brazilian', 'French', 'Spanish', 'Dutch', 'Argentinian', 'Portuguese', 'German', 'Italian'])} player who played for {random.choice(clubs_list)}",
        lambda: f"🏆 Name {article} {nation} player who has played in {comp_display}",
        lambda: f"Name a manager who managed {random.choice(manager_clubs)}",
        lambda: f"🏟️ Name a stadium located in {random.choice(STADIUM_COUNTRIES)}",
        lambda: f"Name a football team whose primary home kit color is {random.choice(list(KIT_COLOR_MAP.keys()))}",
        lambda: f"🏆 Name a player who has won {comp_display}",
        lambda: f"🏆 Name a team that has won {comp_display}"
    ]
    return random.choice(templates)()

# --- 4. ENGINE & UI ---
def reset_all_data():
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()

if 'game_started' not in st.session_state:
    st.session_state.update({'game_started': False, 'grid_size': 4, 'num_players': 2, 'player_names': [], 'player_data': {}, 'turn': 0, 'rolled': False, 'current_roll': 0, 'grid_map': [], 'winner': None, 'active_final_task': None})

def start_game():
    total_sq = st.session_state.grid_size ** 2
    board = [{"task": "🏁 KICK OFF", "assets": {"flags":[], "logos":[], "emojis":[]}}]
    unique_tasks = set()
    while len(unique_tasks) < (total_sq - 2): unique_tasks.add(generate_random_task())
    for t in list(unique_tasks): board.append({"task": t, "assets": get_assets(t)})
    board.append({"task": "🏆 FINAL WHISTLE", "assets": {"flags":[], "logos":[], "emojis":[]}})
    st.session_state.grid_map = board
    st.session_state.player_data = {i: {"pos": 0, "prev": 0, "name": st.session_state.player_names[i] or f"Manager {i+1}", "initials": (st.session_state.player_names[i][:2] if st.session_state.player_names[i] else f"M{i+1}").upper(), "color": ["#FF4B4B", "#1C83E1", "#00C04A", "#FFD700"][i]} for i in range(st.session_state.num_players)}
    st.session_state.game_started = True

st.set_page_config(page_title="Football Path", layout="wide")

if st.session_state.winner:
    st.balloons()
    st.markdown(f"<div style='text-align:center; padding:100px;'><h1>🏆</h1><h2 style='color:{st.session_state.winner['color']};'>{st.session_state.winner['name']} Wins!</h2></div>", unsafe_allow_html=True)
    if st.button("Return to Menu"): reset_all_data()
elif not st.session_state.game_started:
    st.title("⚽ Football Path Setup")
    st.session_state.grid_size = st.number_input("Grid Size", 3, 6, 4)
    st.session_state.num_players = st.number_input("Players", 1, 4, 2)
    st.session_state.player_names = [st.text_input(f"Manager {i+1}", key=f"p{i}") for i in range(st.session_state.num_players)]
    if st.button("START MATCH"): start_game(); st.rerun()
else:
    player = st.session_state.player_data[st.session_state.turn]
    st.markdown(f"<style>.grid-container {{ display: grid; gap: 10px; grid-template-columns: repeat({st.session_state.grid_size}, 1fr); }} .grid-item {{ background: #1e2129; border: 1px solid #333; border-radius: 8px; padding: 10px; text-align: center; min-height: 120px; }} .active-sq {{ border: 2px solid {player['color']}; }} .p-tag {{ border-radius: 50%; width: 22px; height: 22px; display: inline-flex; align-items: center; justify-content: center; font-size: 0.6rem; color: white; margin: 1px; }}</style>", unsafe_allow_html=True)
    
    grid_html = '<div class="grid-container">'
    for i, item in enumerate(st.session_state.grid_map):
        active = "active-sq" if i == player['pos'] else ""
        marks = "".join([f'<span class="p-tag" style="background:{p["color"]}">{p["initials"]}</span>' for pid, p in st.session_state.player_data.items() if p['pos'] == i])
        grid_html += f'<div class="grid-item {active}">{format_header_icons(item["assets"])}<div style="font-size:0.8rem; font-weight:600;">{item["task"]}</div>{marks}</div>'
    st.markdown(grid_html + "</div>", unsafe_allow_html=True)

    with st.sidebar:
        st.header(f"Turn: {player['name']}")
        if not st.session_state.rolled:
            if st.button("🎲 ROLL"):
                st.session_state.current_roll = random.randint(1, 3)
                player['prev'], player['pos'] = player['pos'], min(player['pos'] + st.session_state.current_roll, len(st.session_state.grid_map)-1)
                if player['pos'] == len(st.session_state.grid_map)-1:
                    t = generate_random_task()
                    st.session_state.active_final_task = {"text": t, "assets": get_assets(t)}
                st.session_state.rolled = True; st.rerun()
        else:
            st.subheader(f"Rolled: {st.session_state.current_roll}")
            curr = st.session_state.active_final_task if player['pos'] == len(st.session_state.grid_map)-1 else st.session_state.grid_map[player['pos']]
            st.info(f"Task: {curr['task']}")
            if st.button("✅ Success"):
                if player['pos'] == len(st.session_state.grid_map)-1: st.session_state.winner = player
                else: st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players; st.session_state.rolled = False
                st.rerun()
            if st.button("❌ Fail"):
                player['pos'] = player['prev']; st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players; st.session_state.rolled = False
                st.rerun()
