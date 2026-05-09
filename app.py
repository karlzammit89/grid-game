import streamlit as st
import pandas as pd
import random
import re

# --- 1. MOCK DATABASE FOR NAMES (Backup logic) ---
# FBref uses specific IDs for clubs. Here are common ones for the "Inter/Chelsea" type tasks.
CLUB_IDS = {
    "inter milan": "d60ad303",
    "chelsea": "cff3d3bb",
    "man utd": "19538871",
    "real madrid": "5324c30a",
    "liverpool": "822bd0ba",
    "arsenal": "18bb7c10"
}

@st.cache_data(show_spinner="Connecting to FBref archives...")
def get_online_answers(task_text):
    """
    Directly pulls the 'Players who played for both' table from FBref.
    """
    t = task_text.lower()
    try:
        if "played for both" in t:
            match = re.search(r"both (.*?) & (.*)", t)
            if match:
                # 1. Clean club names
                c1 = match.group(1).strip().lower()
                c2 = match.group(2).strip().lower()
                
                # 2. Get IDs (Fallback to search if not in our CLUB_IDS list)
                id1 = CLUB_IDS.get(c1)
                id2 = CLUB_IDS.get(c2)
                
                if id1 and id2:
                    # Construct the exact URL for players who played for both
                    url = f"https://fbref.com/en/friv/players-who-played-for-multiple-clubs-countries.fcgi?t1={id1}&t2={id2}"
                    
                    # Read HTML tables using Pandas (Super fast, no browser needed)
                    tables = pd.read_html(url)
                    if tables:
                        df = tables[0]
                        # The player names are usually in the 'Player' column
                        return df['Player'].tolist()
    except Exception as e:
        return [f"Lookup failed: {str(e)}"]
    
    return ["No players found or club not supported yet."]
