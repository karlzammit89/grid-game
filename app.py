import streamlit as st
import random
import re
import pandas as pd

# --- 1. DATA MAPPING (Original) ---
CLUB_IDS = {
    "Man Utd": "19538871", "Liverpool": "822bd0ba", "Arsenal": "18bb7c10", 
    "Chelsea": "cff3d3bb", "Man City": "b8fd03ef", "Tottenham": "3ad23a75",
    "Aston Villa": "860223d1", "Newcastle": "b1b71fcb", "Real Madrid": "5324c30a", 
    "Barcelona": "206d9d25", "Atletico Madrid": "db3b5483", "Sevilla": "ad2be748",
    "AC Milan": "e2d42690", "Juventus": "e2d42690", "Inter Milan": "d60ad303",
    "Bayern Munich": "054fdde2", "PSG": "e2d8892c"
}

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

# --- STATIC ANSWER BANK (New: For categories without easy free APIs) ---
STATIC_ANSWERS = {
    "stadium": {
        "England": ["Wembley", "Old Trafford", "Anfield", "Emirates", "Stamford Bridge"],
        "Spain": ["Santiago Bernabéu", "Camp Nou", "Metropolitano", "Mestalla"],
        "Germany": ["Allianz Arena", "Signal Iduna Park", "Olympiastadion"],
        "Italy": ["San Siro", "Stadio Olimpico", "Juventus Stadium"],
        "France": ["Parc des Princes", "Stade de France", "Stade Vélodrome"]
    },
    "kit": {
        "Red": ["Liverpool", "Man Utd", "Arsenal", "Bayern Munich", "Ajax"],
        "Blue": ["Chelsea", "Man City", "Napoli", "Inter Milan", "Everton"],
        "Yellow": ["Dortmund", "Villarreal", "Norwich City", "Cadiz"],
        "White": ["Real Madrid", "Tottenham", "Leeds United", "Valencia"],
        "Green": ["Celtic", "Real Betis", "Sassuolo", "Saint-Étienne"]
    }
}

# --- 2. ENGINES ---
@st.cache_data(show_spinner=False)
def fetch_shared_players(club1, club2):
    id1, id2 = CLUB_IDS.get(club1), CLUB_IDS.get(club2)
    if not id1 or not id2: return []
    try:
        url = f"https://fbref.com/en/friv/players-who-played-for-multiple-clubs-countries.fcgi?t1={id1}&t2={id2}"
        storage_options = {'User-Agent': 'Mozilla/5.0'}
        tables = pd.read_html(url, storage_options=storage_options)
        if tables:
            return tables[0]['Player'].dropna().unique().tolist()
    except: return []
    return []

def get_answer_logic(task_text):
    """Identifies the task type and provides likely answers."""
    t_lower = task_text.lower()
    
    # 1. Shared Players (API/Scraper)
    if "both" in t_lower:
        match = re.search(r"both (.*?) & (.*)", task_text)
        if match:
            c1, c2 = match.group(1).strip(), match.group(2).strip()
            ans = fetch_shared_players(c1, c2)
            return f"**Common Players:** {', '.join(ans[:12])}" if ans else "No data found for this pair."
            
    # 2. Stadiums (Static Data)
    if "stadium" in t_lower:
        for country, names in STATIC_ANSWERS["stadium"].items():
            if country.lower() in t_lower:
                return f"**{country} Stadiums:** {', '.join(names)}"
                
    # 3. Kits (Static Data)
    if "kit color" in t_lower:
        for color, teams in STATIC_ANSWERS["kit"].items():
            if color.lower() in t_lower:
                return f"**Teams wearing {color}:** {', '.join(teams)}"
                
    return "Click the link below to search for the specific answer!"

# (The rest of your original formatting and generation functions go here...)

# --- 5. UI (REVERTED TO YOUR ORIGINAL STYLE) ---
# ... inside your sidebar logic ...

            # --- ANSWERS SECTION (Integrated with API/Logic) ---
            with st.expander("👁️ View Answers"):
                # Call the logic function to get content
                answer_content = get_answer_logic(task_text)
                st.markdown(f"<div style='font-size:0.9rem; margin-bottom:10px;'>{answer_content}</div>", unsafe_allow_html=True)
                
                # Original Search link
                search_query = task_text.replace("Name a", "").strip()
                st.markdown(f"""
                <a href="https://www.google.com/search?q=football+{search_query.replace(' ', '+')}" target="_blank" style="text-decoration:none;">
                    <div style="background:#333; color:white; padding:10px; border-radius:5px; text-align:center; font-size:0.8rem; border:1px solid #555;">
                        🔍 Search for Answers
                    </div>
                </a>
                """, unsafe_allow_html=True)
