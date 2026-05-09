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
    "Clean Sheets": {"Global": [50, 100], "League": [30, 50]}
}

# --- 2. GRAMMAR & ASSET ENGINES ---
def articulate_task(subject_type, target, action="played for"):
    needs_the = ["Premier League", "Championship", "FA Cup", "Champions League", 
                 "Europa League", "World Cup", "Euros", "Copa America", 
                 "Ligue 1", "Serie A", "La Liga", "Bundesliga"]
    
    # Ensure target isn't already a full sentence
    clean_target = target.replace("Name a player who played for ", "").replace("the ", "")
    final_target = f"the {clean_target}" if clean_target in needs_the else clean_target
    
    if subject_type == "player":
        return f"Name a player who {action} {final_target}"
    
    article = "an" if subject_type[0].lower() in ['a', 'e', 'i', 'o', 'u'] else "a"
    return f"Name {article} {subject_type} player who {action} {final_target}"

def get_assets(text):
    assets = {"logos": [], "flags": [], "emojis": []}
    clean_text = re.sub(r'[^\w\s]', '', text).lower()
    if "won" in clean_text: assets["emojis"].append("🏆")
    if "goals" in clean_text: assets["emojis"].append("🥅")
    if "assists" in clean_text: assets["emojis"].append("👟")
    if "clean sheets" in clean_text: assets["emojis"].append("🧤")
    
    for nation, iso in COUNTRY_DATA.items():
        if nation.lower() in clean_text:
            assets["flags"].append(f"https://flagcdn.com/w40/{iso}.png")
            
    sorted_clubs = sorted(ESPN_LOGOS.keys(), key=len, reverse=True)
    for club in sorted_clubs:
        if club.lower() in clean_text:
            assets["logos"].append(f"https://a.espncdn.com/i/teamlogos/soccer/500/{ESPN_LOGOS[club]}.png")
            break # Only one logo per task to keep it clean

    if "stadium" in clean_text: assets["emojis"].append("🏟️")
    return assets

def format_header_icons(assets, size_logos="24px", size_emojis="22px"):
    html = '<div style="display: flex; gap: 6px; justify-content: center; align-items: center; min-height: 25px; margin: 8px 0;">'
    for e in list(dict.fromkeys(assets.get("emojis", []))):
        html += f'<span style="font-size:{size_emojis};">{e}</span>'
    for f in list(dict.fromkeys(assets.get("flags", []))):
        html += f'<img src="{f}" style="height:14px; border-radius:2px; border:1px solid #444;">'
    for l in list(dict.fromkeys(assets.get("logos", []))):
        html += f'<img src="{l}" style="height:{size_logos};">'
    if not any(assets.values()):
        return html + f'<span style="font-size:{size_emojis};">⚽</span></div>'
    return html + '</div>'

# --- 3. DYNAMIC LOGIC ---
def generate_random_task(categories, hard_mode=False):
    all_nations = list(COUNTRY_DATA.keys())
    clubs_list = list(ESPN_LOGOS.keys())
    leagues_comps = ["Champions League", "Europa League", "World Cup", "FA Cup", "Premier League", "La Liga", "Serie A", "Bundesliga"]
    
    pool = []
    if "Club Connections" in categories: pool.extend([1, 2, 3])
    if "Stadiums" in categories: pool.append(4)
    if "Kits" in categories: pool.append(5)
    if "Trophies" in categories: pool.extend([6, 7])
    if "N+ Stats" in categories: pool.extend([10, 11])
    
    if not pool: return "Name a famous retired footballer"
    template_type = random.choice(pool)
    
    if template_type == 10:
        stat = random.choice(["Goals", "Assists", "Clean Sheets"])
        scope = random.choice(["Global", "League", "CL"])
        n_val = random.choice(STAT_THRESHOLDS[stat][scope])
        if hard_mode: n_val = int(n_val * 1.8)
        
        if scope == "Global":
            return f"Name a player who has {n_val}+ {stat.lower()} in his career"
        else:
            comp = "Champions League" if scope == "CL" else random.choice(["Premier League", "La Liga"])
            target = f"the {comp}" if comp in ["Champions League", "Premier League"] else comp
            return f"Name a player who has {n_val}+ {stat.lower()} in {target}"
            
    elif template_type == 11:
        nation = random.choice(["English", "Spanish", "French", "Brazilian", "German"])
        comp = random.choice(["Premier League", "La Liga", "Bundesliga"])
        n_val = 120 if hard_mode else 50
        target = f"the {comp}" if comp == "Premier League" else comp
        return f"Name a {nation} player who has {n_val}+ goals in {target}"
    
    elif template_type == 1: 
        pair = random.sample(clubs_list, 2)
        return f"Name a player who played for both {pair[0]} & {pair[1]}"
    elif template_type == 2:
        return articulate_task(random.choice(all_nations), random.choice(clubs_list))
    elif template_type == 3:
        return f"Name a manager who managed {random.choice(clubs_list)}"
    elif template_type == 4:
        return f"Name a stadium located in {random.choice(list(STADIUM_COUNTRIES.keys()))}"
    elif template_type == 5:
        return f"Name a team whose home kit is {random.choice(list(KIT_COLOR_MAP.keys()))}"
    elif template_type == 6:
        return articulate_task("team", random.choice(leagues_comps), action="has won")
    else:
        return articulate_task(random.choice(all_nations), random.choice(leagues_comps), action="has played in")

# --- 4. STATE MANAGEMENT ---
def reset_all_data():
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()

if 'game_started' not in st.session_state:
    st.session_state.update({
        'game_started': False, 'grid_size': 4, 'num_players': 2, 'player_names': [], 
        'player_data': {}, 'turn': 0, 'rolled': False, 'current_roll': 0, 
        'grid_map': [], 'confirm_reset': False, 'winner': None, 'active_final_task': None,
        'selected_categories': ["Club Connections", "Trophies", "N+ Stats", "Stadiums", "Kits"]
    })

def start_game():
    total_sq = st.session_state.grid_size ** 2
    board = [{"task": "KICK OFF", "assets": {"emojis":["🏁"]}}]
    unique_tasks = set()
    while len(unique_tasks) < (total_sq - 2):
        unique_tasks.add(generate_random_task(st.session_state.selected_categories))
    
    for task_text in list(unique_tasks):
        board.append({"task": task_text, "assets": get_assets(task_text)})
    board.append({"task": "FINAL WHISTLE", "assets": {"emojis":["🥇"]}})
    
    st.session_state.grid_map = board
    st.session_state.player_data = {
        i: {
            "pos": 0, "prev": 0, "name": st.session_state.player_names[i] or f"Manager {i+1}",
            "initials": (st.session_state.player_names[i][:2] if st.session_state.player_names[i] else f"M{i+1}").upper(),
            "color": ["#FF4B4B", "#1C83E1", "#00C04A", "#FFD700"][i]
        } for i in range(st.session_state.num_players)
    }
    st.session_state.game_started = True
    return True

# --- 5. UI ---
st.set_page_config(page_title="Football Path Trivia", layout="wide")

if st.session_state.winner:
    st.balloons()
    st.markdown(f"<div style='text-align:center; padding:100px;'><h1 style='font-size:5rem;'>🏆</h1><h2 style='color:{st.session_state.winner['color']};'>Congratulations {st.session_state.winner['name']}!</h2></div>", unsafe_allow_html=True)
    if st.button("🏟️ Return to Menu", use_container_width=True): reset_all_data()

elif not st.session_state.game_started:
    st.title("⚽ Football Grid Setup")
    with st.container(border=True):
        c1, c2 = st.columns(2)
        st.session_state.grid_size = c1.number_input("Grid Size", 3, 6, 4)
        st.session_state.num_players = c2.number_input("Players", 1, 4, 2)
        st.session_state.selected_categories = st.multiselect("Active Categories", 
            ["Club Connections", "Trophies", "N+ Stats", "Stadiums", "Kits"], 
            default=["Club Connections", "Trophies", "N+ Stats", "Stadiums", "Kits"])

    cols = st.columns(st.session_state.num_players)
    st.session_state.player_names = [cols[i].text_input(f"Manager {i+1}", key=f"p{i}") for i in range(st.session_state.num_players)]
    if st.button("🚀 START MATCH", use_container_width=True, type="primary"):
        if start_game(): st.rerun()

else:
    player = st.session_state.player_data[st.session_state.turn]
    is_at_finish = player['pos'] == len(st.session_state.grid_map) - 1

    st.markdown(f"<style>.grid-container {{ display: grid; gap: 12px; grid-template-columns: repeat({st.session_state.grid_size}, 1fr); }} .grid-item {{ background: #1e2129; border: 1px solid #333; border-radius: 12px; padding: 12px; text-align: center; min-height: 150px; display: flex; flex-direction: column; align-items: center; justify-content: space-between; }} .active-sq {{ border: 3px solid {player['color']}; box-shadow: 0 0 15px {player['color']}55; }} .p-tag {{ border-radius: 50%; width: 28px; height: 28px; display: inline-flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: 800; border: 2px solid #fff; margin: 1px; }} </style>", unsafe_allow_html=True)

    grid_html = '<div class="grid-container">'
    for i, item in enumerate(st.session_state.grid_map):
        active = "active-sq" if i == player['pos'] else ""
        marks = "".join([f'<span class="p-tag" style="background:{p["color"]}">{p["initials"]}</span>' for pid, p in st.session_state.player_data.items() if p['pos'] == i])
        grid_html += f'<div class="grid-item {active}"><div style="width:100%; color:#555; font-size:0.7rem; text-align:left;">#{i:02}</div>{format_header_icons(item["assets"])}<div style="color:#eee; font-weight:600; font-size:0.85rem;">{item["task"]}</div><div style="min-height:35px;">{marks}</div></div>'
    st.markdown(grid_html + "</div>", unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(f"<h3 style='text-align:center; color:{player['color']};'>{player['name']}</h3>", unsafe_allow_html=True)
        
        if not st.session_state.rolled:
            if is_at_finish:
                if st.button("🔥 GENERATE BONUS QUESTION", use_container_width=True, type="primary"):
                    txt = generate_random_task(st.session_state.selected_categories, hard_mode=True)
                    st.session_state.active_final_task = {"text": txt, "assets": get_assets(txt)}
                    st.session_state.rolled = True
                    st.rerun()
            else:
                if st.button("🎲 ROLL DICE", use_container_width=True, type="primary"):
                    st.session_state.current_roll = random.randint(1, 3)
                    player['prev'], player['pos'] = player['pos'], min(player['pos'] + st.session_state.current_roll, len(st.session_state.grid_map)-1)
                    st.session_state.rolled = True
                    st.rerun()
        else:
            if is_at_finish and st.session_state.active_final_task:
                st.markdown("<div style='text-align:center; color:#FFD700; font-weight:bold;'>🌟 BONUS QUESTION 🌟</div>", unsafe_allow_html=True)
                task_to_show = st.session_state.active_final_task
            else:
                st.markdown(f"<div style='text-align:center; font-size:3rem;'>🎲 {st.session_state.current_roll}</div>", unsafe_allow_html=True)
                task_to_show = st.session_state.grid_map[player['pos']]

            with st.container(border=True):
                st.markdown(format_header_icons(task_to_show['assets'], size_logos="30px", size_emojis="26px"), unsafe_allow_html=True)
                st.markdown(f"<div style='text-align:center; font-weight:600;'>{task_to_show['text'] if 'text' in task_to_show else task_to_show['task']}</div>", unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            if c1.button("✅ Success", use_container_width=True):
                if is_at_finish: st.session_state.winner = player
                else: 
                    st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players
                    st.session_state.rolled = False
                st.rerun()
            if c2.button("❌ Fail", use_container_width=True):
                player['pos'] = player['prev']
                st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players
                st.session_state.rolled = False
                st.rerun()

        st.markdown("---")
        if st.button("🚩 End Game", use_container_width=True): reset_all_data()
