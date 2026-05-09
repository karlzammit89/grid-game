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

STADIUM_COUNTRIES = {"England": "gb-eng", "Spain": "es", "Germany": "de", "Italy": "it", "France": "fr", "Portugal": "pt", "Brazil": "br", "Argentina": "ar", "Mexico": "mx"}

KIT_COLOR_MAP = {
    "Red": "🔴", "Blue": "🔵", "White": "⚪", "Yellow": "🟡", "Green": "🟢", "Black": "⚫"
}

STAT_THRESHOLDS = {
    "Goals": {"Global": [100, 200], "CL": [20, 30], "League": [50, 75]},
    "Assists": {"Global": [50, 100], "League": [25, 50]},
    "Clean Sheets": {"Global": [50, 100], "League": [30, 50]},
    "Bookings": {"Global": [40, 70, 100]}
}

TROPHY_WINNERS = {
    "Euros": ["French", "Spanish", "Portuguese", "German", "Italian", "Dutch", "Danish"],
    "Copa America": ["Argentinian", "Brazilian", "Uruguayan", "Colombian"],
    "World Cup": ["French", "Spanish", "German", "Italian", "Argentinian", "Brazilian", "English", "Uruguayan"]
}

EUROPEANS = [k for k, v in COUNTRY_DATA.items() if v in ["fr", "es", "gb-eng", "pt", "nl", "be", "de", "it", "hr", "ch", "dk", "tr", "at", "ua", "gb-sct", "se", "gb-wls", "pl", "no"]]
SOUTH_AMERICANS = ["Argentinian", "Brazilian", "Colombian", "Uruguayan", "Ecuadorian"]

# --- 2. GRAMMAR & ASSET ENGINES ---
def grid_text_formatter(text):
    """Removes 'Name a' and pluralizes subjects for a smarter grid UI."""
    # Convert "Name an Italian player" -> "Italian players"
    text = re.sub(r"Name a[n]? (\w+) player", r"\1 players", text)
    # Convert "Name a player" -> "Players"
    text = re.sub(r"Name a player", "Players", text)
    # Convert "Name a team" -> "Teams"
    text = re.sub(r"Name a team", "Teams", text)
    # Convert "Name a stadium" -> "Stadiums"
    text = re.sub(r"Name a stadium", "Stadiums", text)
    # Convert "Name a manager" -> "Managers"
    text = re.sub(r"Name a manager", "Managers", text)
    return text

def smart_pluralize(text, count):
    if count <= 1:
        return text
    text = re.sub(r"Name a[n]? (\w+) player", f"Name {count} \\1 players", text)
    text = re.sub(r"Name a player", f"Name {count} players", text)
    text = re.sub(r"Name a team", f"Name {count} teams", text)
    text = re.sub(r"Name a stadium", f"Name {count} stadiums", text)
    text = re.sub(r"Name a manager", f"Name {count} managers", text)
    return text

def articulate_task(subject_type, target, action="played for"):
    clean_target = target.replace("Name a player who ", "").replace("won ", "").replace("has won ", "").replace("the ", "")
    article = "an" if subject_type[0].lower() in ['a', 'e', 'i', 'o', 'u'] else "a"
    needs_the = ["Premier League", "Championship", "FA Cup", "Champions League", 
                 "Europa League", "World Cup", "Euros", "Copa America", 
                 "Ligue 1", "Serie A", "La Liga", "Bundesliga"]
    
    final_target = f"the {clean_target}" if clean_target in needs_the else clean_target
    
    if subject_type == "player":
        return f"Name a player who {action} {final_target}"
    return f"Name {article} {subject_type} player who {action} {final_target}"

def get_assets(text):
    assets = {"logos": [], "flags": [], "emojis": []}
    clean_text = re.sub(r'[^\w\s]', '', text).lower()
    if "won" in clean_text: assets["emojis"].append("🏆")
    if "goals" in clean_text: assets["emojis"].append("🥅")
    if "assists" in clean_text: assets["emojis"].append("👟")
    if "clean sheets" in clean_text: assets["emojis"].append("🧤")
    if "bookings" in clean_text: assets["emojis"].append("😵")
    
    for nation, iso in COUNTRY_DATA.items():
        if nation.lower() in clean_text:
            flag_url = f"https://flagcdn.com/w40/{iso}.png"
            if flag_url not in assets["flags"]: assets["flags"].append(flag_url)
    for s_country, iso in STADIUM_COUNTRIES.items():
        if s_country.lower() in clean_text:
            flag_url = f"https://flagcdn.com/w40/{iso}.png"
            if flag_url not in assets["flags"]: assets["flags"].append(flag_url)
    if "stadium" in clean_text: assets["emojis"].append("🏟️")
    
    sorted_clubs = sorted(ESPN_LOGOS.keys(), key=len, reverse=True)
    found_ids = set()
    for club in sorted_clubs:
        if club.lower() in clean_text:
            espn_id = ESPN_LOGOS[club]
            if espn_id not in found_ids:
                assets["logos"].append(f"https://a.espncdn.com/i/teamlogos/soccer/500/{espn_id}.png")
                found_ids.add(espn_id)
    for color, emoji in KIT_COLOR_MAP.items():
        if color.lower() in clean_text:
            assets["emojis"].append(emoji)
            break
    return assets

def format_header_icons(assets, size_logos="24px", size_emojis="22px"):
    html = '<div style="display: flex; gap: 6px; justify-content: center; align-items: center; min-height: 25px; margin: 8px 0;">'
    for e in list(dict.fromkeys(assets["emojis"])):
        html += f'<span style="font-size:{size_emojis};">{e}</span>'
    for f in assets["flags"]:
        html += f'<img src="{f}" style="height:14px; border-radius:2px; border:1px solid #444;">'
    for l in assets["logos"]:
        html += f'<img src="{l}" style="height:{size_logos};">'
    if not any(assets.values()):
        return html + f'<span style="font-size:{size_emojis};">⚽</span></div>'
    return html + '</div>'

# --- 3. DYNAMIC LOGIC ---
def generate_random_task(categories):
    all_nations = list(COUNTRY_DATA.keys())
    clubs_list = list(ESPN_LOGOS.keys())
    leagues_comps = ["Champions League", "Europa League", "World Cup", "FA Cup", "Premier League", "Championship", "La Liga", "Serie A", "Bundesliga", "Ligue 1"]
    pool = []
    if "Club Connections" in categories: pool.extend([1, 2, 3])
    if "Stadiums" in categories: pool.append(4)
    if "Kits" in categories: pool.append(5)
    if "Trophies" in categories: pool.extend([6, 7, 8, 9])
    if "N+ Stats" in categories: pool.extend([10, 11])
    
    if not pool: return "N/A"
    template_type = random.choice(pool)
    
    if template_type == 10:
        stat = random.choice(list(STAT_THRESHOLDS.keys()))
        scope = random.choice(["Global", "League", "CL"]) if stat != "Bookings" else "Global"
        n_value = random.choice(STAT_THRESHOLDS[stat][scope])
        comp = "Champions League" if scope == "CL" else random.choice(["Premier League", "La Liga", "Serie A"])
        return f"Name a player who has {n_value}+ {stat.lower()} in {'his career' if scope == 'Global' else comp}"
    elif template_type == 11:
        nation = random.choice(["English", "Spanish", "French", "Brazilian", "Argentinian", "German"])
        comp = random.choice(["Premier League", "La Liga", "Bundesliga"])
        return f"Name {'an' if nation[0].lower() in 'aeiou' else 'a'} {nation} player who has 50+ goals in {comp if comp != 'Premier League' else 'the Premier League'}"
    elif template_type == 1: 
        pair = random.sample(clubs_list, 2)
        return f"Name a player who played for both {pair[0]} & {pair[1]}"
    elif template_type == 2:
        n = random.choice(['Brazilian', 'French', 'Spanish', 'Dutch', 'Argentinian', 'Portuguese', 'German', 'Italian', 'Nigerian'])
        return articulate_task(n, random.choice(clubs_list))
    elif template_type == 3:
        target_club = random.choice(clubs_list)
        return f"Name a manager who managed {target_club}"
    elif template_type == 4:
        return f"Name a stadium located in {random.choice(list(STADIUM_COUNTRIES.keys()))}"
    elif template_type == 5:
        return f"Name a football team whose primary home kit color is {random.choice(list(KIT_COLOR_MAP.keys()))}"
    elif template_type == 6:
        comp = random.choice(leagues_comps + ["Euros", "Copa America"])
        return f"Name a team that has won {comp if 'League' not in comp else 'the ' + comp}"
    elif template_type == 7:
        return articulate_task("player", random.choice(leagues_comps), action="has won")
    elif template_type == 8:
        comp = random.choice(["Euros", "Copa America", "World Cup"])
        valid_nation = random.choice(TROPHY_WINNERS.get(comp, EUROPEANS))
        return articulate_task(valid_nation, comp, action="has won")
    else:
        comp = random.choice(leagues_comps)
        nation = random.choice(all_nations)
        return articulate_task(nation, comp, action="has played in")

# --- 4. STATE MANAGEMENT ---
if 'game_started' not in st.session_state:
    st.session_state.update({
        'game_started': False, 'grid_size': 4, 'num_players': 2, 'player_names': [], 
        'player_data': {}, 'turn': 0, 'rolled': False, 'current_roll': 0, 
        'grid_map': [], 'confirm_reset': False, 'winner': None, 'active_final_task': None,
        'selected_categories': ["Club Connections", "Trophies", "N+ Stats", "Stadiums", "Kits"]
    })

def start_game():
    total_sq = st.session_state.grid_size ** 2
    board = [{"task": "KICK OFF", "assets": {"flags":[], "logos":[], "emojis":["🏁"]}}]
    unique_tasks = set()
    while len(unique_tasks) < (total_sq - 2):
        new_task = generate_random_task(st.session_state.selected_categories)
        if new_task != "N/A": unique_tasks.add(new_task)
    
    for task_text in list(unique_tasks):
        board.append({"task": task_text, "assets": get_assets(task_text)})
    board.append({"task": "FINAL WHISTLE", "assets": {"flags":[], "logos":[], "emojis":["🥇"]}})
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

if not st.session_state.game_started:
    st.title("⚽ Football Grid Setup")
    c1, c2 = st.columns(2)
    st.session_state.grid_size = c1.number_input("Grid Size", 3, 6, 4)
    st.session_state.num_players = c2.number_input("Players", 1, 4, 2)
    st.session_state.player_names = [st.text_input(f"Manager {i+1}", key=f"p{i}") for i in range(st.session_state.num_players)]
    if st.button("🚀 START MATCH", use_container_width=True, type="primary"):
        start_game(); st.rerun()

else:
    player = st.session_state.player_data[st.session_state.turn]
    st.markdown(f"""<style>
        .grid-container {{ display: grid; gap: 12px; grid-template-columns: repeat({st.session_state.grid_size}, 1fr); }}
        .grid-item {{ background: #1e2129; border: 1px solid #333; border-radius: 12px; padding: 12px; text-align: center; min-height: 150px; display: flex; flex-direction: column; align-items: center; justify-content: space-between; }}
        .active-sq {{ border: 3px solid {player['color']}; box-shadow: 0 0 15px {player['color']}55; }}
        .p-tag {{ border-radius: 50%; width: 28px; height: 28px; display: inline-flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: 800; border: 2px solid #fff; margin: 1px; }}
        </style>""", unsafe_allow_html=True)

    grid_html = '<div class="grid-container">'
    for i, item in enumerate(st.session_state.grid_map):
        active = "active-sq" if i == player['pos'] else ""
        marks = "".join([f'<span class="p-tag" style="background:{p["color"]}">{p["initials"]}</span>' for pid, p in st.session_state.player_data.items() if p['pos'] == i])
        
        # UI FIX: Applying grid formatting for smart pluralized look
        display_task = grid_text_formatter(item["task"]) if i not in [0, len(st.session_state.grid_map)-1] else item["task"]
        
        grid_html += f'<div class="grid-item {active}"><div style="width:100%; color:#555; font-size:0.7rem; text-align:left;">#{i:02}</div>{format_header_icons(item["assets"])}<div style="color:#eee; font-weight:600; font-size:0.85rem; line-height:1.2;">{display_task}</div><div style="min-height:35px; display:flex; justify-content:center; align-items:center;">{marks}</div></div>'
    st.markdown(grid_html + "</div>", unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(f"<h3 style='text-align:center; color:{player['color']};'>{player['name']}</h3>", unsafe_allow_html=True)
        if not st.session_state.rolled:
            if st.button("🎲 ROLL DICE", use_container_width=True, type="primary"):
                st.session_state.current_roll = random.randint(1, 3)
                player['prev'], player['pos'] = player['pos'], min(player['pos'] + st.session_state.current_roll, len(st.session_state.grid_map)-1)
                if player['pos'] == len(st.session_state.grid_map)-1:
                    t = generate_random_task(st.session_state.selected_categories)
                    st.session_state.active_final_task = {"text": t, "assets": get_assets(t)}
                st.session_state.rolled = True; st.rerun()
        else:
            st.markdown(f"<div style='text-align:center; font-size:3rem;'>🎲 {st.session_state.current_roll}</div>", unsafe_allow_html=True)
            is_last = player['pos'] == len(st.session_state.grid_map) - 1
            task_info = st.session_state.active_final_task if is_last else st.session_state.grid_map[player['pos']]
            display_text = smart_pluralize(task_info['text'] if is_last else task_info['task'], st.session_state.current_roll)

            with st.container(border=True):
                st.markdown(format_header_icons(task_info['assets'], "30px", "26px"), unsafe_allow_html=True)
                st.markdown(f"<div style='text-align:center; font-weight:600;'>{display_text}</div>", unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            if c1.button("✅ Success", use_container_width=True):
                if is_last: st.session_state.winner = player
                else: st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players; st.session_state.rolled = False
                st.rerun()
            if c2.button("❌ Fail", use_container_width=True):
                player['pos'] = player['prev']; st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players; st.session_state.rolled = False
                st.rerun()
