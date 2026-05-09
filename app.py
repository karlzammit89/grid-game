import streamlit as st
import random
import re

# --- 1. SMART DATA MAPPING (Expanded with 2026 FIFA Top 50) ---
COUNTRY_DATA = {
    # Top 10
    "French": "fr", "France": "fr", "Spanish": "es", "Spain": "es",
    "Argentinian": "ar", "Argentina": "ar", "English": "gb-eng", "England": "gb-eng",
    "Portuguese": "pt", "Portugal": "pt", "Brazilian": "br", "Brazil": "br",
    "Dutch": "nl", "Netherlands": "nl", "Moroccan": "ma", "Morocco": "ma",
    "Belgian": "be", "Belgium": "be", "German": "de", "Germany": "de",
    # 11-25 & Notable Additions
    "Croatian": "hr", "Croatia": "hr", "Italian": "it", "Italy": "it",
    "Colombian": "co", "Colombia": "co", "Senegalese": "sn", "Senegal": "sn",
    "Mexican": "mx", "Mexico": "mx", "American": "us", "USA": "us",
    "Uruguayan": "uy", "Uruguay": "uy", "Japanese": "jp", "Japan": "jp",
    "Swiss": "ch", "Switzerland": "ch", "Danish": "dk", "Denmark": "dk",
    "Turkish": "tr", "Türkiye": "tr", "Ecuadorian": "ec", "Ecuador": "ec",
    "Austrian": "at", "Austria": "at", "South Korean": "kr", "South Korea": "kr",
    "Nigerian": "ng", "Nigeria": "ng", "Australian": "au", "Australia": "au",
    "Algerian": "dz", "Algeria": "dz", "Egyptian": "eg", "Egypt": "eg",
    "Canadian": "ca", "Canada": "ca", "Norwegian": "no", "Norway": "no",
    "Ukrainian": "ua", "Ukraine": "ua", "Ivorian": "ci", "Côte d'Ivoire": "ci",
    "Scottish": "gb-sct", "Scotland": "gb-sct", "Swedish": "se", "Sweden": "se",
    "Welsh": "gb-wls", "Wales": "gb-wls", "Polish": "pl", "Poland": "pl"
}

ESPN_LOGOS = {
    "Man Utd": "360", "Manchester United": "360", "Liverpool": "364", "Arsenal": "359", 
    "Chelsea": "363", "Man City": "382", "Spurs": "367", "Tottenham": "367",
    "Aston Villa": "362", "Newcastle": "361", "Real Madrid": "86", "Barcelona": "83", 
    "Atletico Madrid": "1068", "Sevilla": "243", "Villarreal": "102", "AC Milan": "103", 
    "Juventus": "111", "Inter Milan": "110", "AS Roma": "104", "Napoli": "114", 
    "Bayern Munich": "132", "Dortmund": "124", "Leverkusen": "131", "PSG": "160", 
    "Marseille": "176", "Monaco": "174", "Ajax": "148", "PSV": "149", "Benfica": "190", 
    "Porto": "192", "Sporting CP": "193"
}

VALID_CLUB_PAIRS = [
    ("Real Madrid", "AC Milan"), ("Barcelona", "PSG"), ("Man Utd", "Real Madrid"),
    ("Liverpool", "Chelsea"), ("Inter Milan", "AC Milan"), ("Bayern Munich", "Real Madrid"),
    ("Arsenal", "Barcelona"), ("Juventus", "Bayern Munich"), ("Man City", "Barcelona"),
    ("Chelsea", "Real Madrid"), ("PSG", "AC Milan"), ("Man Utd", "Juventus"),
    ("Arsenal", "Man City"), ("Chelsea", "Man City"), ("Atletico Madrid", "Barcelona")
]

def get_club_logo_html(text):
    html = ""
    for club, espn_id in ESPN_LOGOS.items():
        if club.lower() in text.lower():
            url = f"https://a.espncdn.com/i/teamlogos/soccer/500/{espn_id}.png"
            html += f'<img src="{url}" style="height:18px; vertical-align:middle; margin-left:6px;">'
    return html

def clean_text_and_add_assets(text):
    clean_text = re.sub(r'[^\x00-\x7F]+', '', text).strip()
    flag_html = ""
    for word, iso in COUNTRY_DATA.items():
        if word.lower() in clean_text.lower():
            flag_url = f"https://flagcdn.com/w40/{iso}.png"
            flag_html = f'<img src="{flag_url}" style="height:14px; vertical-align:middle; margin-left:6px; border-radius:2px; border:1px solid #444;">'
            break
    logo_html = get_club_logo_html(clean_text)
    return f"{clean_text} {logo_html}{flag_html}"

# --- 2. DYNAMIC LOGIC GENERATORS ---
def generate_random_task():
    templates = [
        lambda: f"Name a player who played for both {random.choice(VALID_CLUB_PAIRS)[0]} & {random.choice(VALID_CLUB_PAIRS)[1]}",
        lambda: f"Name a {random.choice(['Brazilian', 'French', 'Spanish', 'Dutch', 'Argentinian', 'Portuguese', 'German', 'Italian'])} player who played for {random.choice(list(ESPN_LOGOS.keys()))}",
        lambda: f"Name a player who won the Champions League with both {random.choice(['Real Madrid', 'AC Milan', 'Liverpool', 'Bayern Munich', 'Barcelona', 'Man City', 'Chelsea'])} and another club",
        lambda: f"Name a manager who coached {random.choice(['Real Madrid', 'Chelsea', 'Bayern Munich', 'PSG', 'Juventus', 'Barcelona', 'Inter Milan'])}",
        lambda: f"Name a {random.choice(list(COUNTRY_DATA.keys()))} player who has played in the Champions League"
    ]
    return clean_text_and_add_assets(random.choice(templates)())
