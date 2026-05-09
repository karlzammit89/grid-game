chromium
    chromium-driver
    ```

---

### The Complete Script (`football_grid.py`)

```python
import streamlit as st
import ScraperFC
import pandas as pd
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

STADIUM_COUNTRIES = {"England": "gb-eng", "Spain": "es", "Germany": "de", "Italy": "it", "France": "fr", "Portugal": "pt", "Brazil": "br", "Argentina": "ar", "Mexico": "mx"}
KIT_COLOR_MAP = {"Red": "🔴", "Blue": "🔵", "White": "⚪", "Yellow": "🟡", "Green": "🟢", "Black": "⚫"}

# --- 2. SCRAPER & INTERNET LOOKUP ---

@st.cache_resource
def get_scraper():
    """Initializes the ScraperFC FBRef engine."""
    return ScraperFC.FBRef()

@st.cache_data(show_spinner="Scouring the FBRef archives...")
def get_online_answers(task_text):
    """Uses ScraperFC to find correct answers on the internet."""
    scraper = get_scraper()
    t = task_text.lower()
    
    try:
        # Logic for "Played for both [Club A] & [Club B]"
        if "played for both" in t:
            # Matches text between 'both' and '&', and after '&'
            match = re.search(r"both (.*?) & (.*)", t)
            if match:
                club_a = match.group(1).strip()
                club_b = match.group(2).strip()
                
                # ScraperFC calls the FBRef 'Multiple-Squad Players' table
                df = scraper.get_inter_club_players(club_a, club_b)
                return df['Player'].tolist()
        
        # Add more scraper-specific logic here if needed for Trophies/Leagues
        
    except Exception:
        return []
    return []

# --- 3. GRAMMAR & ASSET ENGINES ---

def grid_text_formatter(text):
    text = text.replace("Name a football team whose", "Football teams whose")
    text = re.sub(r"Name a[n]? (\w+) player", r"\1 players", text)
    text = re.sub(r"Name a player", "Players", text)
    text = re.sub(r"Name a team", "Teams", text)
    text = re.sub(r"Name a stadium", "Stadiums", text)
    text = re.sub(r"Name a manager", "Managers", text)
    for word in ["players", "teams", "Managers", "Stadiums", "Players", "Teams"]:
        text = text.replace(f"{word} who has", f"{word} who have")
        text = text.replace(f"{word} that has", f"{word} that have")
    return text

def smart_pluralize(text, count):
    if count <= 1: return text
    text = text.replace("Name a football team whose", f"Name {count} football teams whose")
    text = re.sub(r"Name a[n]? (\w+) player", f"Name {count} \\1 players", text)
    text = re.sub(r"Name a player", f"Name {count} players", text)
    text = re.sub(r"Name a team", f"Name {count} teams", text)
    text = re.sub(r"Name a stadium", f"Name {count} stadiums", text)
    text = re.sub(r"Name a manager", f"Name {count} managers", text)
    text = text.replace("players who has", "players who have")
    text = text.replace("teams that has", "teams that have")
    return text

def articulate_task(subject_type, target, action="played for"):
    clean_target = target.replace("Name a player who ", "").replace("won ", "").replace("has won ", "").replace("the ", "")
    article = "an" if subject_type[0].lower() in ['a', 'e', 'i', 'o', 'u'] else "a"
    needs_the = ["Premier League", "Championship", "FA Cup", "Champions League", "Europa League", "World Cup", "Euros", "Copa America"]
    final_target = f"the {clean_target}" if clean_target in needs_the else clean_target
    if subject_type == "player": return f"Name a player who {action} {final_target}"
    return f"Name {article} {subject_type} player who {action} {final_target}"

def get_assets(text):
    assets = {"logos": [], "flags": [], "emojis": []}
    clean_text = re.sub(r'[^\w\s]', '', text).lower()
    if "won" in clean_text: assets["emojis"].append("🏆")
    for nation, iso in COUNTRY_DATA.items():
        if nation.lower() in clean_text: assets["flags"].append(f"https://flagcdn.com/w40/{iso}.png")
    for club, eid in ESPN_LOGOS.items():
        if club.lower() in clean_text: assets["logos"].append(f"https://a.espncdn.com/i/teamlogos/soccer/500/{eid}.png")
    return assets

def format_header_icons(assets, size_logos="24px", size_emojis="22px"):
    html = '<div style="display: flex; gap: 6px; justify-content: center; align-items: center; min-height: 25px; margin: 8px 0;">'
    for e in list(dict.fromkeys(assets["emojis"])): html += f'<span style="font-size:{size_emojis};">{e}</span>'
    for f in assets["flags"]: html += f'<img src="{f}" style="height:14px; border-radius:2px; border:1px solid #444;">'
    for l in assets["logos"]: html += f'<img src="{l}" style="height:{size_logos};">'
    return html + '</div>'

# --- 4. GAME LOGIC ---

def generate_random_task(categories):
    clubs_list = list(ESPN_LOGOS.keys())
    pool = []
    if "Club Connections" in categories: pool.extend([1, 2])
    if "Kits" in categories: pool.append(3)
    if "Trophies" in categories: pool.append(4)
    
    rtype = random.choice(pool) if pool else 1
    if rtype == 1:
        pair = random.sample(clubs_list, 2)
        return f"Name a player who played for both {pair[0]} & {pair[1]}"
    elif rtype == 2:
        return articulate_task(random.choice(["Brazilian", "French", "Spanish", "German"]), random.choice(clubs_list))
    elif rtype == 3:
        return f"Name a football team whose primary home kit color is {random.choice(list(KIT_COLOR_MAP.keys()))}"
    else:
        return f"Name a team that has won the {random.choice(['Champions League', 'World Cup', 'Premier League'])}"

def start_game():
    total_sq = st.session_state.grid_size ** 2
    board = [{"task": "KICK OFF", "assets": {"flags":[], "logos":[], "emojis":["🏁"]}}]
    unique_tasks = set()
    while len(unique_tasks) < (total_sq - 2):
        unique_tasks.add(generate_random_task(st.session_state.selected_categories))
    for task_text in list(unique_tasks):
        board.append({"task": task_text, "assets": get_assets(task_text)})
    board.append({"task": "FINAL WHISTLE", "assets": {"flags":[], "logos":[], "emojis":["🥇"]}})
    st.session_state.grid_map = board
    st.session_state.player_data = {i: {"pos": 0, "prev": 0, "name": st.session_state.player_names[i] or f"Manager {i+1}", "initials": (st.session_state.player_names[i][:2] if st.session_state.player_names[i] else f"M{i+1}").upper(), "color": ["#FF4B4B", "#1C83E1", "#00C04A", "#FFD700"][i]} for i in range(st.session_state.num_players)}
    st.session_state.game_started = True

# --- 5. MAIN UI ---

st.set_page_config(page_title="Football Path Trivia", layout="wide")

if 'game_started' not in st.session_state:
    st.session_state.update({'game_started': False, 'grid_size': 4, 'num_players': 2, 'player_names': [], 'player_data': {}, 'turn': 0, 'rolled': False, 'current_roll': 0, 'grid_map': [], 'winner': None, 'selected_categories': ["Club Connections", "Trophies", "Kits"]})

if not st.session_state.game_started:
    st.title("⚽ Football Grid Setup")
    c1, c2 = st.columns(2)
    st.session_state.grid_size = c1.number_input("Grid Size", 3, 6, 4)
    st.session_state.num_players = c2.number_input("Players", 1, 4, 2)
    st.session_state.selected_categories = st.multiselect("Active Categories", ["Club Connections", "Trophies", "Kits"], default=["Club Connections", "Trophies", "Kits"])
    st.session_state.player_names = [st.text_input(f"Manager {i+1}", key=f"p{i}") for i in range(st.session_state.num_players)]
    if st.button("🚀 START MATCH", use_container_width=True): start_game(); st.rerun()

else:
    player = st.session_state.player_data[st.session_state.turn]
    
    # Grid Styling
    st.markdown(f"<style>.grid-container {{ display: grid; gap: 12px; grid-template-columns: repeat({st.session_state.grid_size}, 1fr); }} .grid-item {{ background: #1e2129; border: 1px solid #333; border-radius: 12px; padding: 12px; text-align: center; min-height: 150px; display: flex; flex-direction: column; justify-content: space-between; }} .active-sq {{ border: 3px solid {player['color']}; }} .p-tag {{ border-radius: 50%; width: 24px; height: 24px; display: inline-flex; align-items: center; justify-content: center; font-size: 0.7rem; border: 1px solid #fff; margin: 1px; color: white; }}</style>", unsafe_allow_html=True)

    # Render Grid
    grid_html = '<div class="grid-container">'
    for i, item in enumerate(st.session_state.grid_map):
        active = "active-sq" if i == player['pos'] else ""
        marks = "".join([f'<span class="p-tag" style="background:{p["color"]}">{p["initials"]}</span>' for pid, p in st.session_state.player_data.items() if p['pos'] == i])
        text = grid_text_formatter(item["task"]) if 0 < i < len(st.session_state.grid_map)-1 else item["task"]
        grid_html += f'<div class="grid-item {active}"><div>#{i:02}</div>{format_header_icons(item["assets"])}<div style="font-size:0.85rem;">{text}</div><div style="height:30px;">{marks}</div></div>'
    st.markdown(grid_html + "</div>", unsafe_allow_html=True)

    # Sidebar Controls
    with st.sidebar:
        st.markdown(f"<h2 style='color:{player['color']}'>{player['name']}</h2>", unsafe_allow_html=True)
        if not st.session_state.rolled:
            if st.button("🎲 ROLL DICE", use_container_width=True, type="primary"):
                st.session_state.current_roll = random.randint(1, 3)
                player['prev'], player['pos'] = player['pos'], min(player['pos'] + st.session_state.current_roll, len(st.session_state.grid_map)-1)
                st.session_state.rolled = True; st.rerun()
        else:
            task_text = st.session_state.grid_map[player['pos']]['task']
            display_text = smart_pluralize(task_text, st.session_state.current_roll)
            st.info(display_text)
            
            # --- LIVE INTERNET ANSWERS ---
            if 0 < player['pos'] < len(st.session_state.grid_map)-1:
                ans_list = get_online_answers(task_text)
                with st.expander(f"👁️ Show Solutions ({len(ans_list)} found)"):
                    if ans_list:
                        for name in ans_list: st.write(f"• {name}")
                    else:
                        st.write("No matching players found on FBRef.")

            c1, c2 = st.columns(2)
            if c1.button("✅ Success", use_container_width=True): st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players; st.session_state.rolled = False; st.rerun()
            if c2.button("❌ Fail", use_container_width=True): player['pos'] = player['prev']; st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players; st.session_state.rolled = False; st.rerun()
