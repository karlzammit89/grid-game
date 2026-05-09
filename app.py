import streamlit as st
import ScraperFC
import pandas as pd
import random
import re

# --- 1. DATA MAPPING & ASSETS ---
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

KIT_COLOR_MAP = {"Red": "🔴", "Blue": "🔵", "White": "⚪", "Yellow": "🟡", "Green": "🟢", "Black": "⚫"}

# --- 2. INTERNET LOOKUP ENGINE (ScraperFC) ---

@st.cache_resource
def get_scraper():
    """Initializes the FBRef scraper engine once."""
    return ScraperFC.FBRef()

@st.cache_data(show_spinner="Searching FBRef for players...")
def get_online_answers(task_text):
    """
    Scrapes FBRef for 'Multiple-Squad Players'.
    Reference: ScraperFC handles web-scraping for soccer data.
    """
    scraper = get_scraper()
    t = task_text.lower()
    
    try:
        # Regex to extract club names: 'both [Club A] & [Club B]'
        if "played for both" in t:
            match = re.search(r"both (.*?) & (.*)", t)
            if match:
                club_a = match.group(1).strip()
                club_b = match.group(2).strip()
                
                # FBRef provides a specific tool for players who played for multiple clubs.
                # Note: If get_inter_club_players is not available in the latest ScraperFC,
                # you may need to use scrape_league_table or scrape_stats.
                df = scraper.get_inter_club_players(club_a, club_b)
                return df['Player'].tolist()
    except Exception:
        return []
    return []

# --- 3. FORMATTING UTILITIES ---

def grid_text_formatter(text):
    text = text.replace("Name a football team whose", "Football teams whose")
    text = re.sub(r"Name a[n]? (\w+) player", r"\1 players", text)
    text = re.sub(r"Name a player", "Players", text)
    text = re.sub(r"Name a team", "Teams", text)
    for word in ["players", "teams", "Managers", "Players", "Teams"]:
        text = text.replace(f"{word} who has", f"{word} who have")
    return text

def smart_pluralize(text, count):
    if count <= 1: return text
    text = text.replace("Name a player", f"Name {count} players")
    text = text.replace("Name a team", f"Name {count} teams")
    return text

def get_assets(text):
    assets = {"logos": [], "flags": [], "emojis": []}
    clean_text = text.lower()
    if "won" in clean_text: assets["emojis"].append("🏆")
    for nation, iso in COUNTRY_DATA.items():
        if nation.lower() in clean_text: assets["flags"].append(f"https://flagcdn.com/w40/{iso}.png")
    for club, eid in ESPN_LOGOS.items():
        if club.lower() in clean_text: assets["logos"].append(f"https://a.espncdn.com/i/teamlogos/soccer/500/{eid}.png")
    return assets

def format_header_icons(assets):
    html = '<div style="display: flex; gap: 6px; justify-content: center; align-items: center; min-height: 25px; margin: 8px 0;">'
    for e in assets["emojis"]: html += f'<span>{e}</span>'
    for f in assets["flags"]: html += f'<img src="{f}" style="height:12px;">'
    for l in assets["logos"]: html += f'<img src="{l}" style="height:22px;">'
    return html + '</div>'

# --- 4. GAME ENGINE ---

def generate_random_task(categories):
    clubs = list(ESPN_LOGOS.keys())
    pool = []
    if "Club Connections" in categories: pool.extend([1, 2])
    if "Kits" in categories: pool.append(3)
    if "Trophies" in categories: pool.append(4)
    
    rtype = random.choice(pool) if pool else 1
    if rtype == 1:
        pair = random.sample(clubs, 2)
        return f"Name a player who played for both {pair[0]} & {pair[1]}"
    elif rtype == 2:
        return f"Name a {random.choice(['Brazilian', 'French', 'Spanish'])} player who played for {random.choice(clubs)}"
    elif rtype == 3:
        return f"Name a football team whose primary home kit color is {random.choice(list(KIT_COLOR_MAP.keys()))}"
    else:
        return f"Name a team that has won the {random.choice(['Champions League', 'World Cup', 'Premier League'])}"

def start_game():
    total_sq = st.session_state.grid_size ** 2
    board = [{"task": "START", "assets": {"flags":[], "logos":[], "emojis":["🏁"]}}]
    tasks = [generate_random_task(st.session_state.selected_categories) for _ in range(total_sq - 2)]
    for t in tasks: board.append({"task": t, "assets": get_assets(t)})
    board.append({"task": "FINISH", "assets": {"flags":[], "logos":[], "emojis":["🥇"]}})
    st.session_state.grid_map = board
    st.session_state.player_data = {i: {"pos": 0, "prev": 0, "name": st.session_state.p_names[i] or f"P{i+1}", "color": ["#FF4B4B", "#1C83E1", "#00C04A", "#FFD700"][i]} for i in range(st.session_state.num_players)}
    st.session_state.game_started = True

# --- 5. UI LAYOUT ---

st.set_page_config(page_title="Football Internet Trivia", layout="wide")

if 'game_started' not in st.session_state:
    st.session_state.update({'game_started': False, 'grid_size': 4, 'num_players': 2, 'p_names': [], 'player_data': {}, 'turn': 0, 'rolled': False, 'current_roll': 0, 'grid_map': [], 'selected_categories': ["Club Connections", "Trophies"]})

if not st.session_state.game_started:
    st.title("⚽ Football Grid Setup")
    c1, c2 = st.columns(2)
    st.session_state.grid_size = c1.slider("Grid Dimensions", 3, 5, 4)
    st.session_state.num_players = c2.slider("Total Players", 1, 4, 2)
    st.session_state.selected_categories = st.multiselect("Game Categories", ["Club Connections", "Trophies", "Kits"], default=["Club Connections", "Trophies"])
    st.session_state.p_names = [st.text_input(f"Manager {i+1}", key=f"n{i}") for i in range(st.session_state.num_players)]
    if st.button("🚀 KICK OFF"): start_game(); st.rerun()

else:
    curr_p = st.session_state.player_data[st.session_state.turn]
    
    # CSS for Grid
    st.markdown(f"<style>.grid-item {{ background: #1e2129; border: 1px solid #333; border-radius: 8px; padding: 10px; text-align: center; min-height: 140px; }} .active-sq {{ border: 2px solid {curr_p['color']}; box-shadow: 0 0 10px {curr_p['color']}; }}</style>", unsafe_allow_html=True)

    # Display Grid
    cols = st.columns(st.session_state.grid_size)
    for i, item in enumerate(st.session_state.grid_map):
        with cols[i % st.session_state.grid_size]:
            is_active = "active-sq" if i == curr_p['pos'] else ""
            st.markdown(f'<div class="grid-item {is_active}">{format_header_icons(item["assets"])}<p style="font-size:0.8rem;">{grid_text_formatter(item["task"])}</p></div>', unsafe_allow_html=True)

    # Sidebar Controls
    with st.sidebar:
        st.subheader(f"Current Turn: {curr_p['name']}")
        if not st.session_state.rolled:
            if st.button("🎲 Roll Dice"):
                st.session_state.current_roll = random.randint(1, 3)
                curr_p['prev'], curr_p['pos'] = curr_p['pos'], min(curr_p['pos'] + st.session_state.current_roll, len(st.session_state.grid_map)-1)
                st.session_state.rolled = True; st.rerun()
        else:
            task = st.session_state.grid_map[curr_p['pos']]['task']
            st.info(smart_pluralize(task, st.session_state.current_roll))
            
            # --- LIVE INTERNET ANSWERS ---
            if 0 < curr_p['pos'] < len(st.session_state.grid_map)-1:
                results = get_online_answers(task)
                with st.expander(f"👁️ View Potential Answers ({len(results)})"):
                    if results:
                        st.write(", ".join(results[:15])) # Show top 15
                    else:
                        st.write("No direct matches found. Any valid player counts!")

            if st.button("✅ Success"): 
                st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players
                st.session_state.rolled = False; st.rerun()
            if st.button("❌ Fail (Go Back)"):
                curr_p['pos'] = curr_p['prev']
                st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players
                st.session_state.rolled = False; st.rerun()
