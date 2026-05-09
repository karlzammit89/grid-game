# --- UPDATED DYNAMIC LOGIC ---
def generate_random_task():
    # Grouping nationalities for logic checks
    south_americans = ["Argentinian", "Brazilian", "Colombian", "Uruguayan", "Ecuadorian"]
    europeans = [
        "French", "Spanish", "English", "Portuguese", "Dutch", "Belgian", "German", 
        "Italian", "Croatian", "Swiss", "Danish", "Turkish", "Austrian", "Ukrainian", 
        "Scottish", "Swedish", "Welsh", "Polish", "Norwegian"
    ]
    all_nations = list(COUNTRY_DATA.keys())
    
    clubs_list = list(ESPN_LOGOS.keys())
    manager_clubs = ['Real Madrid', 'Chelsea', 'Bayern Munich', 'PSG', 'Juventus', 'Barcelona', 'Inter Milan', 'Man Utd', 'Liverpool', 'AC Milan']
    
    # Regional Competitions
    euro_comps = ["the Euros", "the Nations League"]
    sa_comps = ["the Copa America"]
    global_comps = ["the Champions League", "the Europa League", "the World Cup", "the FA Cup", "the Premier League", "the Championship", "La Liga", "Serie A", "Bundesliga", "Ligue 1"]

    # Logic to pick a valid Nation-Competition pair
    picker = random.random()
    if picker < 0.3: # 30% chance for a European specific task
        nation = random.choice(europeans)
        comp = random.choice(euro_comps + global_comps)
    elif picker < 0.5: # 20% chance for a South American specific task
        nation = random.choice(south_americans)
        comp = random.choice(sa_comps + global_comps)
    else: # 50% chance for any nation in a global competition
        nation = random.choice(all_nations)
        comp = random.choice(global_comps)

    article = "an" if nation[0].lower() in ['a', 'e', 'i', 'o', 'u'] else "a"
    pair = random.sample(clubs_list, 2)
    
    templates = [
        lambda: f"Name a player who played for both {pair[0]} & {pair[1]}",
        lambda: f"Name a {random.choice(['Brazilian', 'French', 'Spanish', 'Dutch', 'Argentinian', 'Portuguese', 'German', 'Italian'])} player who played for {random.choice(clubs_list)}",
        lambda: f"Name {article} {nation} player who has played in {comp}",
        lambda: f"Name a manager who managed {random.choice(manager_clubs)}",
        lambda: f"Name a stadium located in {random.choice(STADIUM_COUNTRIES)}",
        lambda: f"Name a football team whose primary home kit color is {random.choice(list(KIT_COLOR_MAP.keys()))}",
        lambda: f"Name a player who has won {comp}",
        lambda: f"Name a team that has won {comp}"
    ]
    return random.choice(templates)()
