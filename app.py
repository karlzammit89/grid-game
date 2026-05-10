import streamlit as st
import random
import re
import pandas as pd
import requests

# --- 1. DATA MAPPING ---
# FBref numeric club IDs — used by BOTH the club-vs-club and nationality-at-club
# scraper functions with the ?level=franch URL format.
# Sourced from FBref club page URLs: fbref.com/en/squads/{NUMERIC_ID}/...
CLUB_IDS = {
    "Man Utd":        "19538871", "Liverpool":      "164575",  "Arsenal":        "153995",
    "Chelsea":        "cff3d3bb", "Man City":       "b8fd03ef","Tottenham":      "157033",
    "Aston Villa":    "164959",   "Newcastle":      "b2b91eca","Real Madrid":    "159928",
    "Barcelona":      "154774",   "Atletico Madrid":"173488",  "Sevilla":        "ad2be748",
    "AC Milan":       "173603",   "Juventus":       "e0652b08","Inter Milan":    "172965",
    "Bayern Munich":  "054fdde2", "PSG":            "174223",  "Dortmund":       "add600a5",
    "Ajax":           "a96ecf6e", "Porto":          "5f43e2c5","Benfica":        "f8ca3df0",
    "Sporting CP":    "afd5e9dc", "Napoli":         "d348d1a8","AS Roma":        "cf74a709",
    "Marseille":      "f74cd1e4", "Lyon":           "f4ede454","Monaco":         "fd6114db",
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

STADIUM_COUNTRIES = {
    "England": "gb-eng", "Spain": "es", "Germany": "de", 
    "Italy": "it", "France": "fr", "Portugal": "pt", 
    "Brazil": "br", "Argentina": "ar", "Mexico": "mx"
}

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

# ─────────────────────────────────────────────────────────────────────────────
# 2. STATIC ANSWER DATABASE
#    These are hardcoded because they change rarely (stadiums) or never (kits).
#    Wikipedia / TheSportsDB answers are fetched live and cached via st.cache_data.
# ─────────────────────────────────────────────────────────────────────────────

STADIUM_ANSWERS = {
    "England": [
        "Old Trafford (Man Utd)", "Anfield (Liverpool)", "Emirates Stadium (Arsenal)",
        "Stamford Bridge (Chelsea)", "Etihad Stadium (Man City)", "Tottenham Hotspur Stadium",
        "Villa Park (Aston Villa)", "St. James' Park (Newcastle)", "Goodison Park (Everton)",
        "Elland Road (Leeds)", "Molineux (Wolves)", "London Stadium (West Ham)",
        "Selhurst Park (Crystal Palace)", "Amex Stadium (Brighton)", "Portman Road (Ipswich)",
        "Bramall Lane (Sheffield Utd)", "Craven Cottage (Fulham)", "Vitality Stadium (Bournemouth)",
        "King Power Stadium (Leicester)", "Turf Moor (Burnley)", "Carrow Road (Norwich)",
        "Gtech Community Stadium (Brentford)", "City Ground (Nottingham Forest)",
        "St. Mary's Stadium (Southampton)", "Hillsborough (Sheffield Wednesday)",
        "Loftus Road (QPR)", "The Den (Millwall)", "Pride Park (Derby County)",
        "Wembley Stadium", "Riverside Stadium (Middlesbrough)", "bet365 Stadium (Stoke)",
    ],
    "Spain": [
        "Santiago Bernabéu (Real Madrid)", "Estadi Olímpic Lluís Companys (Barcelona)",
        "Civitas Metropolitano (Atlético Madrid)", "Ramón Sánchez-Pizjuán (Sevilla)",
        "Mestalla (Valencia)", "San Mamés (Athletic Bilbao)", "Estadio de la Cerámica (Villarreal)",
        "El Sadar (Osasuna)", "Reale Arena (Real Sociedad)", "Balaídos (Celta Vigo)",
        "Coliseum (Getafe)", "Estadio Benito Villamarín (Betis)", "Riyadh Air Metropolitano (Atlético)",
    ],
    "Germany": [
        "Allianz Arena (Bayern Munich)", "Signal Iduna Park (Dortmund)",
        "BayArena (Leverkusen)", "Volksparkstadion (Hamburg)", "MHPArena (Stuttgart)",
        "Deutsche Bank Park (Eintracht Frankfurt)", "RheinEnergieStadion (Cologne)",
        "Red Bull Arena (RB Leipzig)", "Volkswagen Arena (Wolfsburg)",
        "PreZero Arena (Hoffenheim)", "MEWA Arena (Mainz)",
    ],
    "Italy": [
        "San Siro / Giuseppe Meazza (AC Milan & Inter)", "Juventus Stadium / Allianz Stadium (Juventus)",
        "Stadio Olimpico (Roma & Lazio)", "Diego Armando Maradona (Napoli)",
        "Gewiss Stadium (Atalanta)", "Artemio Franchi (Fiorentina)",
        "Luigi Ferraris (Sampdoria & Genoa)", "Unipol Domus (Cagliari)",
    ],
    "France": [
        "Parc des Princes (PSG)", "Orange Vélodrome (Marseille)", "Groupama Stadium (Lyon)",
        "Roazhon Park (Rennes)", "Stade Louis-II (Monaco)", "Stade de la Beaujoire (Nantes)",
        "Stade Auguste-Delaune (Reims)", "Stade Pierre-Mauroy (Lille)",
        "Allianz Riviera (Nice)", "Stade de France",
    ],
    "Portugal": [
        "Estádio da Luz (Benfica)", "Estádio do Dragão (Porto)",
        "Estádio José Alvalade (Sporting CP)", "Estádio Municipal de Braga",
        "Estádio D. Afonso Henriques (Vitória SC)",
    ],
    "Brazil": [
        "Maracanã (Flamengo / Fluminense)", "Allianz Parque (Palmeiras)",
        "Neo Química Arena (Corinthians)", "MorumBIS (São Paulo)",
        "Arena da Baixada (Athletico Paranaense)", "Estádio Mineirão (Atlético Mineiro / Cruzeiro)",
        "Arena MRV (Atlético Mineiro)",
    ],
    "Argentina": [
        "La Bombonera (Boca Juniors)", "El Monumental (River Plate)",
        "Estadio Único Ciudad de La Plata (Gimnasia / Estudiantes)",
        "Estadio Marcelo Bielsa (Newell's Old Boys)", "Estadio Padre Ernesto Martearena (Salta)",
    ],
    "Mexico": [
        "Estadio Azteca (América / Cruz Azul)", "Estadio BBVA (Monterrey)",
        "Estadio Akron (Guadalajara)", "Estadio Ciudad de los Deportes (Cruz Azul)",
        "Estadio Nemesio Díez (Toluca)", "Estadio Victoria (Aguascalientes)",
    ],
}

KIT_ANSWERS = {
    "Red": [
        "Man Utd", "Liverpool", "Arsenal", "AC Milan", "Bayern Munich",
        "Atletico Madrid", "Flamengo", "Benfica", "AS Roma",
        "Nottingham Forest", "Sheffield Utd", "Brentford",
        "Southampton", "Wrexham", "Bristol City", "Middlesbrough",
        "Sparta Prague", "Urawa Red Diamonds", "Independiente",
        "River Plate", "Osasuna", "Rayo Vallecano",
    ],
    "Blue": [
        "Chelsea", "Man City", "Inter Milan", "Porto", "Everton",
        "Leicester", "Lech Poznań", "Napoli", "Schalke",
        "Millwall", "Birmingham City", "Ipswich Town", "Peterborough",
        "Reading (change kit)", "Real Madrid (away)", "France (national)", "Italy (national)"
    ],
    "White": [
        "Real Madrid", "Juventus", "Tottenham", "Swansea City", "Leeds Utd",
        "Bolton Wanderers", "Derby County", "Fulham (home)",
        "Preston North End", "England (national)", "Argentina (national)"
    ],
    "Yellow": [
        "Dortmund", "Watford", "Norwich City", "Burton Albion", "Oxford Utd",
        "Brazil (national)", "Colombia (national)", "Villarreal",
        "Modena", "Wolves (amber)", "Cadiz", "Las Palmas"
    ],
    "Green": [
        "Sporting CP", "Celtic (away)", "Werder Bremen", "Betis",
        "Sassuolo", "Venezia (third)", "Plymouth Argyle", "Yeovil Town",
        "Nigeria (national)", "Senegal (away)", "Saudi Arabia (national)"
    ],
    "Black": [
        "Juventus (away)", "Notts County", "Newcastle (away)", "Grimsby Town (away)",
        "Fulham (away)", "Udinese (home)", "AEK Athens (away)", "FC Seoul"
    ],
}

MANAGERS_BY_CLUB = {
    "Real Madrid": [
        # Most recent first
        "Carlo Ancelotti", "Santiago Solari", "Julen Lopetegui", "Zinedine Zidane",
        "Rafael Benítez", "Carlo Ancelotti (1st spell)", "José Mourinho",
        "Manuel Pellegrini", "Bernd Schuster", "Fabio Capello", "Juan Ramón López Caro",
        "Vanderlei Luxemburgo", "José Antonio Camacho", "Carlos Queiroz",
        "Vicente del Bosque", "John Toshack", "Guus Hiddink", "Radoslav Momčilović",
        "Johan Cruyff", "Leo Beenhakker", "Alfredo Di Stéfano",
    ],
    "Barcelona": [
        # Most recent first
        "Hansi Flick", "Xavi Hernández", "Quique Setién",
        "Ernesto Valverde", "Luis Enrique", "Tito Vilanova", "Pep Guardiola",
        "Frank Rijkaard", "Louis van Gaal (2nd spell)", "Lorenzo Serra Ferrer",
        "Louis van Gaal (1st spell)", "Bobby Robson", "Johan Cruyff",
        "Udo Lattek", "Luis Aragonés", "Helenio Herrera",
        "Vic Buckingham", "Rinus Michels", "Ronald Koeman", "Víctor Fernández",
    ],
    "Bayern Munich": [
        # Most recent first
        "Vincent Kompany", "Thomas Tuchel", "Julian Nagelsmann", "Niko Kovač",
        "Jupp Heynckes", "Carlo Ancelotti", "Pep Guardiola", "Jupp Heynckes (1st spell)",
        "Louis van Gaal", "Ottmar Hitzfeld", "Felix Magath", "Ottmar Hitzfeld (1st spell)",
        "Giovanni Trapattoni", "Hansi Flick", "Søren Lerby", "Udo Lattek",
        "Dettmar Cramer", "Branko Zebec",
    ],
    "Chelsea": [
        # Most recent first
        "Enzo Maresca", "Mauricio Pochettino", "Frank Lampard (caretaker)",
        "Graham Potter", "Thomas Tuchel", "Thomas Tuchel (caretaker)", "Frank Lampard",
        "Maurizio Sarri", "Antonio Conte", "Guus Hiddink (caretaker)",
        "José Mourinho (2nd spell)", "Rafa Benítez", "Roberto Di Matteo",
        "André Villas-Boas", "Carlo Ancelotti", "Guus Hiddink (1st caretaker)",
        "Luiz Felipe Scolari", "Avram Grant", "José Mourinho (1st spell)",
        "Claudio Ranieri", "Gianluca Vialli", "Ruud Gullit", "Glenn Hoddle",
        "Bobby Campbell", "John Neal",
    ],
    "PSG": [
        # Most recent first
        "Luis Enrique", "Christophe Galtier", "Mauricio Pochettino",
        "Thomas Tuchel", "Thomas Tuchel (caretaker)", "Unai Emery",
        "Laurent Blanc", "Carlo Ancelotti", "Antoine Kombouaré",
        "Kombouaré", "Paul Le Guen", "Vahid Halilhodžić",
    ],
    "Juventus": [
        # Most recent first
        "Thiago Motta", "Massimiliano Allegri (2nd spell)", "Andrea Pirlo",
        "Maurizio Sarri", "Massimiliano Allegri (1st spell)", "Antonio Conte",
        "Luigi Delneri", "Ciro Ferrara", "Claudio Ranieri", "Didier Deschamps",
        "Carlo Ancelotti", "Marcello Lippi", "Giovanni Trapattoni",
        "Fabio Capello", "Roberto Bettega",
    ],
    "Inter Milan": [
        # Most recent first
        "Simone Inzaghi", "Christian Chivu (caretaker)", "Stefano Pioli (caretaker)",
        "Antonio Conte", "Luciano Spalletti", "Frank de Boer", "Roberto Mancini",
        "Walter Mazzarri", "Rafa Benítez", "José Mourinho", "Roberto Mancini (1st spell)",
        "Héctor Cúper", "Marcello Lippi", "Gigi Simoni", "Roy Hodgson", "Ottavio Bianchi",
        "Giovanni Trapattoni",
    ],
    "Man Utd": [
        # Most recent first
        "Ruben Amorim", "Erik ten Hag", "Ralf Rangnick", "Ole Gunnar Solskjær",
        "Michael Carrick (caretaker)", "José Mourinho", "Louis van Gaal",
        "Ryan Giggs (caretaker)", "David Moyes", "Sir Alex Ferguson",
        "Ron Atkinson", "Dave Sexton", "Tommy Docherty", "Frank O'Farrell",
        "Wilf McGuinness", "Matt Busby",
    ],
    "Liverpool": [
        # Most recent first
        "Arne Slot", "Jürgen Klopp", "Brendan Rodgers", "Kenny Dalglish (2nd spell)",
        "Roy Hodgson", "Rafael Benítez", "Gérard Houllier", "Roy Evans",
        "Kenny Dalglish (1st spell)", "Bob Paisley", "Bill Shankly",
        "Graeme Souness", "Ronnie Moran (caretaker)", "Phil Thompson (caretaker)",
    ],
    "Arsenal": [
        # Most recent first
        "Mikel Arteta", "Freddie Ljungberg (caretaker)", "Unai Emery",
        "Arsène Wenger", "Bruce Rioch", "Stewart Houston (caretaker)",
        "George Graham", "Don Howe", "Terry Neill", "Bertie Mee",
    ],
    "AC Milan": [
        # Most recent first
        "Sérgio Conceição", "Paulo Fonseca", "Stefano Pioli", "Marco Giampaolo",
        "Gennaro Gattuso", "Vincenzo Montella", "Cristian Brocchi (caretaker)",
        "Sinisa Mihajlovic", "Filippo Inzaghi", "Clarence Seedorf",
        "Massimiliano Allegri", "Leonardo (caretaker)", "Carlo Ancelotti",
        "Fatih Terim", "Arrigo Sacchi (2nd spell)", "Fabio Capello",
        "Arrigo Sacchi", "Nils Liedholm",
    ],
    "Atletico Madrid": [
        # Most recent first
        "Diego Simeone", "Gregorio Manzano", "Quique Sánchez Flores",
        "Abel Resino", "Luis Aragonés", "Arrigo Sacchi", "César Luis Menotti",
        "Ron Atkinson", "Héctor Núñez",
    ],
}

# FBref uses ISO 3166-1 alpha-3 codes for nationalities in its URL parameter NAT_XXX.
# URL pattern: ?level=franch&t1=NAT_{ISO3}&t2={FBREF_CLUB_ID}
# These are the same club IDs already used in CLUB_IDS above for the "played for both" feature.
FBREF_NAT_ISO3 = {
    "French":      "FRA", "Spanish":     "ESP", "English":     "ENG",
    "Portuguese":  "POR", "Dutch":       "NED", "Belgian":     "BEL",
    "German":      "GER", "Italian":     "ITA", "Croatian":    "CRO",
    "Swiss":       "SUI", "Danish":      "DEN", "Turkish":     "TUR",
    "Austrian":    "AUT", "Ukrainian":   "UKR", "Scottish":    "SCO",
    "Swedish":     "SWE", "Welsh":       "WAL", "Polish":      "POL",
    "Norwegian":   "NOR", "Argentinian": "ARG", "Brazilian":   "BRA",
    "Colombian":   "COL", "Uruguayan":   "URU", "Ecuadorian":  "ECU",
    "Moroccan":    "MAR", "Senegalese":  "SEN", "Nigerian":    "NGA",
    "Egyptian":    "EGY", "Ivorian":     "CIV", "Algerian":    "ALG",
    "American":    "USA", "Mexican":     "MEX", "Canadian":    "CAN",
    "Japanese":    "JPN", "South Korean":"KOR", "Australian":  "AUS",
}

# FBREF_CLUB_IDS is an alias — CLUB_IDS now contains numeric IDs used by both fetchers.
FBREF_CLUB_IDS = CLUB_IDS

TROPHY_TEAM_ANSWERS = {
    "Champions League": [
        "Real Madrid", "AC Milan", "Bayern Munich", "Liverpool", "Barcelona",
        "Ajax", "Inter Milan", "Juventus", "Man Utd", "Chelsea", "Porto",
        "Dortmund", "Benfica", "Nottingham Forest", "Aston Villa", "PSV Eindhoven",
        "Steaua București", "Marseille", "Red Star Belgrade", "Celtic", "Feyenoord",
        "Atlético Madrid (runner-up x3)"
    ],
    "Europa League": [
        "Sevilla", "Juventus", "Inter Milan", "Liverpool", "Chelsea", "Arsenal",
        "Man Utd", "Atlético Madrid", "Valencia", "Fiorentina", "Parma",
        "Atalanta", "Rangers", "Eintracht Frankfurt", "Roma", "West Ham"
    ],
    "Premier League": [
        "Man Utd", "Chelsea", "Arsenal", "Liverpool", "Man City",
        "Blackburn Rovers", "Leicester City", "Tottenham (1951 — old First Division)"
    ],
    "FA Cup": [
        "Arsenal", "Man Utd", "Chelsea", "Liverpool", "Tottenham", "Man City",
        "Aston Villa", "Newcastle", "Everton", "Blackburn", "Bolton", "Wimbledon",
        "Wigan Athletic", "Portsmouth", "Cardiff City", "West Ham"
    ],
    "La Liga": [
        "Real Madrid", "Barcelona", "Atletico Madrid", "Valencia", "Sevilla",
        "Real Sociedad", "Athletic Bilbao", "Deportivo la Coruña", "Real Betis",
        "Villarreal (never won — closest was 7th)"
    ],
    "Serie A": [
        "Juventus", "Inter Milan", "AC Milan", "Roma", "Lazio", "Fiorentina",
        "Napoli", "Atalanta (never won)", "Cagliari", "Hellas Verona", "Sampdoria",
        "Torino", "Bologna", "Pro Vercelli"
    ],
    "Bundesliga": [
        "Bayern Munich", "Dortmund", "Borussia Mönchengladbach", "Werder Bremen",
        "Hamburg", "Kaiserslautern", "Schalke", "VfB Stuttgart", "Bayer Leverkusen",
        "Eintracht Frankfurt (1959)"
    ],
    "Ligue 1": [
        "PSG", "Lyon", "Marseille", "Monaco", "Saint-Étienne", "Bordeaux",
        "Lens", "Lille", "Nantes", "Auxerre", "Nice", "Reims"
    ],
    "World Cup": [
        "Brazil (5)", "Germany (4)", "Italy (4)", "Argentina (3)", "France (2)",
        "Uruguay (2)", "England (1)", "Spain (1)", "Netherlands (runner-up x3)"
    ],
    "Euros": [
        "Germany (3)", "Spain (4)", "France (2)", "Italy (2)", "Netherlands (1)",
        "Portugal (1)", "Denmark (1)", "Greece (1)", "Czechoslovakia (1)",
        "Soviet Union (1)"
    ],
    "Copa America": [
        "Argentina (16)", "Uruguay (15)", "Brazil (9)", "Paraguay (2)",
        "Colombia (1)", "Chile (2)", "Peru (2)", "Bolivia (1)",
        "Ecuador (never won)"
    ],
    "Championship": [
        "Leicester City", "Burnley", "Fulham", "Norwich City", "Brentford",
        "Leeds Utd", "Sheffield Utd", "Wolverhampton", "Newcastle",
        "Nottingham Forest", "Bournemouth", "Watford", "Huddersfield",
        "Cardiff City", "Stoke City", "QPR", "Derby County", "West Brom",
        "Blackpool", "Sunderland", "Luton Town", "Birmingham City",
        "Reading", "Wigan Athletic", "Ipswich Town", "Southampton",
        "Crystal Palace", "Brighton", "Millwall", "Swansea City",
    ],
}

PLAYER_TROPHY_ANSWERS = {
    "Champions League": [
        "Cristiano Ronaldo", "Lionel Messi", "Karim Benzema", "Luka Modrić",
        "Sergio Ramos", "Gareth Bale", "Toni Kroos", "Iker Casillas",
        "Zinedine Zidane", "Roberto Carlos", "Raúl", "Clarence Seedorf",
        "Didier Drogba", "Wayne Rooney", "Steven Gerrard", "Thierry Henry",
        "Patrick Vieira", "Ryan Giggs", "Roy Keane", "Peter Schmeichel",
        "Andrés Iniesta", "Xavi", "Carles Puyol", "Samuel Eto'o"
    ],
    "Europa League": [
        "Ivan Rakitić", "Kevin De Bruyne", "Henrikh Mkhitaryan", "Pedro",
        "Cesc Fàbregas", "Diego Forlán", "Radamel Falcao", "Arjen Robben",
        "Michael Essien", "Eden Hazard", "Mark Hughes", "Olivier Giroud"
    ],
    "World Cup": [
        "Pelé", "Ronaldo (R9)", "Kylian Mbappé", "Lionel Messi",
        "Zinedine Zidane", "Thierry Henry", "Luca Modric (runner-up)", "Gerd Müller",
        "Franz Beckenbauer", "Bobby Moore", "Geoff Hurst", "Paolo Maldini (runner-up)",
        "Marco van Basten (runner-up)", "Johan Cruyff (runner-up x2)"
    ],
    "Euros": [
        "Cristiano Ronaldo", "Andrés Iniesta", "Fernando Torres", "Xavi",
        "Kylian Mbappé (2021)", "Peter Schmeichel (1992)", "Marco van Basten (1988)",
        "Teddy Sheringham (runner-up 1996)", "Gareth Bale (runner-up 2016)",
        "Antoine Griezmann", "Zinedine Zidane (runner-up 2000)"
    ],
    "Copa America": [
        "Lionel Messi", "Lautaro Martínez", "Nicolás Otamendi", "Romero",
        "Neymar (runner-up x2)", "Casemiro (runner-up)", "Dani Alves (runner-up)",
        "Diego Forlán (2011)", "Luis Suárez (2011)", "Falcao (runner-up)"
    ],
    "Premier League": [
        "Ryan Giggs", "Paul Scholes", "Gary Neville", "Roy Keane", "Peter Schmeichel",
        "Frank Lampard", "John Terry", "Didier Drogba", "Thierry Henry",
        "Patrick Vieira", "Steven Gerrard (never won)", "Sergio Agüero",
        "Vincent Kompany", "Yaya Touré", "Kevin De Bruyne", "Mohamed Salah"
    ],
    "La Liga": [
        "Cristiano Ronaldo", "Lionel Messi", "Sergio Ramos", "Karim Benzema",
        "Luka Modrić", "Toni Kroos", "Andrés Iniesta", "Xavi", "Neymar",
        "Luis Suárez", "Antoine Griezmann", "Diego Forlán", "Fernando Torres"
    ],
    "Serie A": [
        "Cristiano Ronaldo (Juventus)", "Zlatan Ibrahimović", "Antonio Conte",
        "Pavel Nedvěd", "David Trezeguet", "Alessandro Del Piero", "Gianluigi Buffon",
        "Romelu Lukaku (Inter)", "Lautaro Martínez", "Edin Džeko"
    ],
    "Bundesliga": [
        "Robert Lewandowski", "Thomas Müller", "Manuel Neuer", "Franck Ribéry",
        "Arjen Robben", "Toni Kroos", "Mario Götze", "Mesut Özil",
        "Miroslav Klose", "Pep Guardiola (manager)"
    ],
    "Ligue 1": [
        "Neymar", "Kylian Mbappé", "Zlatan Ibrahimović", "Cavani",
        "Thiago Silva", "Marco Verratti", "Angel Di María", "Ronaldinho (Barcelona — no)",
        "Thierry Henry (Monaco)", "Samuel Eto'o (never — Cameroon connection)"
    ],
    "FA Cup": [
        "Thierry Henry", "Dennis Bergkamp", "Robert Pires", "Patrick Vieira",
        "Didier Drogba", "Frank Lampard", "John Terry", "Eden Hazard",
        "Ryan Giggs", "Paul Scholes", "Wayne Rooney", "Rio Ferdinand",
        "Steven Gerrard", "Michael Owen", "Robbie Fowler"
    ],
}

STAT_ANSWERS = {
    # ── Goals – career global ─────────────────────────────────────────────────
    ("goals", "career", 100): [
        "Cristiano Ronaldo", "Lionel Messi", "Romário", "Pelé", "Josef Bican",
        "Ferenc Puskás", "Gerd Müller", "Eusébio", "Wayne Rooney", "Andrew Cole",
        "Frank Lampard", "Jimmy Greaves", "Thierry Henry", "Robbie Fowler",
        "Michael Owen", "Ian Rush", "Gary Lineker", "Alan Shearer",
        "Zlatan Ibrahimović", "Robert Lewandowski", "Karim Benzema", "Samuel Eto'o",
    ],
    ("goals", "career", 200): [
        "Cristiano Ronaldo", "Lionel Messi", "Romário", "Pelé", "Josef Bican",
        "Ferenc Puskás", "Gerd Müller", "Eusébio", "Raúl", "Karim Benzema",
        "Filippo Inzaghi", "Zlatan Ibrahimović", "Robert Lewandowski", "Samuel Eto'o",
        "Ronaldo (R9)", "David Villa", "Didier Drogba",
    ],

    # ── Goals – Premier League ────────────────────────────────────────────────
    ("goals", "Premier League", 50): [
        "Alan Shearer (260)", "Andrew Cole (187)", "Wayne Rooney (208)",
        "Frank Lampard (177)", "Thierry Henry (175)", "Robbie Fowler (163)",
        "Michael Owen (150)", "Les Ferdinand (149)", "Teddy Sheringham (146)",
        "Jimmy Floyd Hasselbaink (127)", "Robbie Keane (126)", "Emile Heskey (110)",
        "Jermain Defoe (162)", "Nicolas Anelka (125)", "Dion Dublin (111)",
        "Ian Wright (113)", "Dwight Yorke (123)", "Paul Scholes (107)",
        "Steve McManaman", "Darren Bent (106)", "Harry Kane (213+)",
        "Mohamed Salah (170+)", "Sergio Agüero (184)",
    ],
    ("goals", "Premier League", 75): [
        "Alan Shearer (260)", "Andrew Cole (187)", "Wayne Rooney (208)",
        "Frank Lampard (177)", "Thierry Henry (175)", "Robbie Fowler (163)",
        "Harry Kane (213+)", "Mohamed Salah (170+)", "Sergio Agüero (184)",
        "Michael Owen (150)", "Jermain Defoe (162)", "Les Ferdinand (149)",
    ],

    # ── Goals – La Liga ───────────────────────────────────────────────────────
    ("goals", "La Liga", 50): [
        "Lionel Messi (474)", "Cristiano Ronaldo (311)", "Raúl (228)",
        "Karim Benzema (219)", "Hugo Sánchez (234)", "Telmo Zarra (251)",
        "Quini (219)", "Pahiño", "Alfredo Di Stéfano (227)",
        "Carlos Santillana (186)", "Fernando Torres (82)", "David Villa (185)",
        "Ronaldo R9 (30 — too few)", "Luis Suárez (121)", "Antoine Griezmann (133+)",
        "Robert Lewandowski (60+)", "Vinicius Jr (80+)",
    ],
    ("goals", "La Liga", 75): [
        "Lionel Messi (474)", "Cristiano Ronaldo (311)", "Raúl (228)",
        "Karim Benzema (219)", "Hugo Sánchez (234)", "Telmo Zarra (251)",
        "David Villa (185)", "Luis Suárez (121)", "Antoine Griezmann (133+)",
    ],

    # ── Goals – Serie A ───────────────────────────────────────────────────────
    ("goals", "Serie A", 50): [
        "Silvio Piola (274)", "Gunnar Nordahl (225)", "Giuseppe Meazza (216)",
        "José Altafini (216)", "Roberto Baggio (205)", "Alessandro Del Piero (188)",
        "Gigi Riva (164)", "Francesco Totti (250)", "Gianluca Vialli (132)",
        "Filippo Inzaghi (156)", "Luca Toni (138)", "Christian Vieri (123)",
        "Zlatan Ibrahimović (93)", "Romelu Lukaku (64)", "Lautaro Martínez (100+)",
        "Ciro Immobile (207+)", "Edin Džeko (85)", "Antonio Di Natale (188)",
    ],
    ("goals", "Serie A", 75): [
        "Silvio Piola (274)", "Francesco Totti (250)", "Gunnar Nordahl (225)",
        "Roberto Baggio (205)", "Ciro Immobile (207+)", "Alessandro Del Piero (188)",
        "Antonio Di Natale (188)", "Gigi Riva (164)", "Filippo Inzaghi (156)",
        "Luca Toni (138)", "Gianluca Vialli (132)", "Christian Vieri (123)",
    ],

    # ── Goals – Bundesliga ────────────────────────────────────────────────────
    ("goals", "Bundesliga", 50): [
        "Gerd Müller (365)", "Robert Lewandowski (312)", "Klaus Fischer (268)",
        "Jupp Heynckes (220)", "Manfred Burgsmüller (213)", "Dieter Müller (177)",
        "Uli Hoeneß (86)", "Karl-Heinz Rummenigge (162)", "Stefan Kuntz (179)",
        "Thomas Müller (230+)", "Mario Basler (97)", "Rudi Völler (134)",
        "Oliver Bierhoff (102)", "Mario Gómez (177)", "Claudio Pizarro (197)",
        "Miroslav Klose (121)", "Arjen Robben (99)", "Franck Ribéry (86)",
    ],
    ("goals", "Bundesliga", 75): [
        "Gerd Müller (365)", "Robert Lewandowski (312)", "Klaus Fischer (268)",
        "Jupp Heynckes (220)", "Thomas Müller (230+)", "Manfred Burgsmüller (213)",
        "Dieter Müller (177)", "Mario Gómez (177)", "Claudio Pizarro (197)",
        "Rudi Völler (134)", "Miroslav Klose (121)",
    ],

    # ── Goals – Ligue 1 ──────────────────────────────────────────────────────
    ("goals", "Ligue 1", 50): [
        "Delio Onnis (299)", "Josip Skoblar (202)", "Bernard Lacombe (255)",
        "Jean-Pierre Papin (159)", "Zlatan Ibrahimović (113)", "Edinson Cavani (138)",
        "Kylian Mbappé (180+)", "Neymar (73)", "Wissam Ben Yedder (153+)",
        "Alexandre Lacazette (100)", "Andy Delort (86)", "Bafétimbi Gomis (176)",
    ],
    ("goals", "Ligue 1", 75): [
        "Delio Onnis (299)", "Bernard Lacombe (255)", "Josip Skoblar (202)",
        "Edinson Cavani (138)", "Kylian Mbappé (180+)", "Bafétimbi Gomis (176)",
        "Jean-Pierre Papin (159)", "Wissam Ben Yedder (153+)",
        "Alexandre Lacazette (100)", "Zlatan Ibrahimović (113)",
    ],

    # ── Goals – Champions League ──────────────────────────────────────────────
    ("goals", "Champions League", 20): [
        "Cristiano Ronaldo (140)", "Lionel Messi (129)", "Robert Lewandowski (91)",
        "Karim Benzema (90)", "Raúl (71)", "Ruud van Nistelrooy (56)",
        "Thomas Müller (53)", "Thierry Henry (50)", "Andriy Shevchenko (48)",
        "Zlatan Ibrahimović (48)", "Didier Drogba (44)", "Edin Džeko (35)",
        "Filippo Inzaghi (46)", "Fernando Morientes (33)", "Mo Salah (46+)",
        "Erling Haaland (45+)", "Vinicius Jr (25+)", "Kylian Mbappé (42+)",
    ],
    ("goals", "Champions League", 30): [
        "Cristiano Ronaldo (140)", "Lionel Messi (129)", "Robert Lewandowski (91)",
        "Karim Benzema (90)", "Raúl (71)", "Ruud van Nistelrooy (56)",
        "Thomas Müller (53)", "Andriy Shevchenko (48)", "Zlatan Ibrahimović (48)",
        "Thierry Henry (50)", "Filippo Inzaghi (46)", "Erling Haaland (45+)",
        "Mo Salah (46+)", "Kylian Mbappé (42+)",
    ],

    # ── Assists – career global ───────────────────────────────────────────────
    ("assists", "career", 50): [
        "Lionel Messi", "Cristiano Ronaldo", "Kevin De Bruyne", "Toni Kroos",
        "Luka Modrić", "Cesc Fàbregas", "Ryan Giggs", "David Beckham",
        "Angel Di María", "Mesut Özil", "Frank Lampard", "Steven Gerrard",
        "Paul Scholes", "Thierry Henry", "Dennis Bergkamp",
    ],
    ("assists", "career", 100): [
        "Lionel Messi", "Cristiano Ronaldo", "Kevin De Bruyne",
        "Cesc Fàbregas", "Ryan Giggs", "Angel Di María", "Mesut Özil",
    ],
    ("assists", "Premier League", 25): [
        "Ryan Giggs (162)", "Cesc Fàbregas (111)", "Wayne Rooney (103)",
        "Frank Lampard (102)", "Andrew Cole (92)", "Steven Gerrard (92)",
        "Kevin De Bruyne (110+)", "Mesut Özil (77)", "Dennis Bergkamp (94)",
        "Robert Pires (73)", "David Beckham (80)", "Paul Scholes (55)",
    ],
    ("assists", "Premier League", 50): [
        "Ryan Giggs (162)", "Kevin De Bruyne (110+)", "Cesc Fàbregas (111)",
        "Wayne Rooney (103)", "Frank Lampard (102)", "Dennis Bergkamp (94)",
        "Steven Gerrard (92)", "Andrew Cole (92)", "David Beckham (80)",
    ],

    # ── Clean sheets – career global ──────────────────────────────────────────
    ("clean_sheets", "career", 50): [
        "Gianluigi Buffon", "Iker Casillas", "Peter Schmeichel", "Edwin van der Sar",
        "Oliver Kahn", "Manuel Neuer", "David de Gea", "Pepe Reina",
        "Joe Hart", "Thibaut Courtois", "Hugo Lloris", "Alisson Becker",
        "Ederson", "Kasper Schmeichel", "Gianluigi Donnarumma",
        "Victor Valdés", "Claudio Bravo", "David Seaman", "Neville Southall",
        "Pat Jennings", "Gordon Banks",
    ],
    ("clean_sheets", "career", 100): [
        "Gianluigi Buffon", "Iker Casillas", "Peter Schmeichel", "Edwin van der Sar",
        "Oliver Kahn", "Manuel Neuer", "Thibaut Courtois", "Hugo Lloris",
        "Pepe Reina", "David de Gea",
    ],
    ("clean_sheets", "Premier League", 30): [
        "Pepe Reina (172)", "David de Gea (163)", "Joe Hart (159)",
        "Peter Schmeichel (141)", "Edwin van der Sar (131)", "Thibaut Courtois (109)",
        "Alisson Becker (140+)", "Hugo Lloris (130+)", "Rob Green (96)",
        "Mark Schwarzer (107)", "Tim Howard (96)", "Brad Friedel (136)",
    ],
    ("clean_sheets", "Premier League", 50): [
        "Pepe Reina (172)", "David de Gea (163)", "Joe Hart (159)",
        "Brad Friedel (136)", "Peter Schmeichel (141)", "Alisson Becker (140+)",
        "Edwin van der Sar (131)", "Hugo Lloris (130+)", "Thibaut Courtois (109)",
        "Mark Schwarzer (107)",
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
# 3. LIVE ANSWER FETCHERS (Wikipedia API — no key required, auto-updates)
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_shared_players(club1, club2):
    """Scrape FBref for players who played for both clubs using numeric franchise IDs."""
    id1, id2 = CLUB_IDS.get(club1), CLUB_IDS.get(club2)
    if not id1 or not id2:
        return []
    try:
        url = f"https://fbref.com/en/friv/players-who-played-for-multiple-clubs-countries.fcgi?level=franch&t1={id1}&t2={id2}"
        storage_options = {'User-Agent': 'Mozilla/5.0 (compatible; FootballTrivia/1.0)'}
        tables = pd.read_html(url, storage_options=storage_options)
        if tables:
            return tables[0]['Player'].dropna().unique().tolist()
    except Exception:
        pass
    return []



@st.cache_data(ttl=86400, show_spinner=False)
def fetch_club_players_nationality(club: str, nationality: str) -> list[str]:
    """
    Scrape FBref's 'players who played for multiple clubs/countries' tool,
    filtering by nationality + club franchise.  This returns ALL historical
    players (not just the current squad) because FBref tracks every season.

    URL pattern:
        https://fbref.com/en/friv/players-who-played-for-multiple-clubs-countries.fcgi
            ?level=franch&t1=NAT_{ISO3}&t2={CLUB_HEX_ID}
    """
    iso3    = FBREF_NAT_ISO3.get(nationality)
    club_id = FBREF_CLUB_IDS.get(club)
    if not iso3 or not club_id:
        return []
    url = (
        "https://fbref.com/en/friv/players-who-played-for-multiple-clubs-countries.fcgi"
        f"?level=franch&t1=NAT_{iso3}&t2={club_id}"
    )
    try:
        tables = pd.read_html(
            url,
            storage_options={"User-Agent": "Mozilla/5.0 (compatible; FootballTrivia/1.0)"},
        )
        if tables:
            # FBref returns a single table; the player-name column is called "Player"
            players = tables[0]["Player"].dropna().unique().tolist()
            return players
    except Exception:
        pass
    return []

# Wikidata QIDs for competitions — used for live trophy winner lookups.
# Championship is intentionally excluded: Wikidata's EFL Championship data
# is too sparse to return reliable results, so we use the static list instead.
WIKIDATA_COMP_INSTANCE_QIDS = {
    "Champions League": "Q37186",
    "Europa League":    "Q193796",
    "Premier League":   "Q9448",
    "FA Cup":           "Q51457",
    "La Liga":          "Q324994",
    "Serie A":          "Q15804",
    "Bundesliga":       "Q82595",
    "Ligue 1":          "Q31867",
    "World Cup":        "Q19317",
    "Euros":            "Q12548",
    "Copa America":     "Q35765",
}

_SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
_SPARQL_HEADERS  = {
    "Accept": "application/sparql-results+json",
    "User-Agent": "FootballTrivia/1.0 (streamlit app)",
}

@st.cache_data(ttl=43200, show_spinner=False)   # refresh every 12 h
def fetch_trophy_teams_wikidata(competition: str) -> list[str]:
    """
    Return all clubs/nations that have won a competition, via Wikidata SPARQL.
    Only used for team-level questions. Championship excluded (sparse Wikidata data).
    """
    comp_qid = WIKIDATA_COMP_INSTANCE_QIDS.get(competition)
    if not comp_qid:
        return []
    sparql = f"""
SELECT DISTINCT ?winnerLabel WHERE {{
  ?edition wdt:P31/wdt:P279* wd:{comp_qid} .
  ?edition wdt:P1346 ?winner .
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}}
ORDER BY ?winnerLabel
"""
    try:
        resp = requests.get(
            _SPARQL_ENDPOINT,
            params={"query": sparql, "format": "json"},
            headers=_SPARQL_HEADERS,
            timeout=10,
        )
        data = resp.json()
        return [b["winnerLabel"]["value"] for b in data["results"]["bindings"]]
    except Exception:
        return []


# Note: player trophy answers are static-only (PLAYER_TROPHY_ANSWERS dict).
# A Wikidata player query would return every player who ever appeared for a
# winning club regardless of nationality — producing false positives like
# "Egyptian players who won Copa América". The static list is curated and correct.


# ─────────────────────────────────────────────────────────────────────────────
# 4. MASTER ANSWER RESOLVER
# ─────────────────────────────────────────────────────────────────────────────

# Top clubs per league/competition — used by multiple resolver branches to
# gather nationality-filtered player lists from FBref. Ordered by prestige so
# the most recognisable players appear first in results.
LEAGUE_CLUBS = {
    "Premier League":   ["Man Utd", "Liverpool", "Arsenal", "Chelsea", "Man City",
                         "Tottenham", "Aston Villa", "Newcastle"],
    "La Liga":          ["Real Madrid", "Barcelona", "Atletico Madrid", "Sevilla"],
    "Serie A":          ["AC Milan", "Juventus", "Inter Milan", "AS Roma", "Napoli"],
    "Bundesliga":       ["Bayern Munich", "Dortmund"],
    "Ligue 1":          ["PSG", "Marseille", "Lyon", "Monaco"],
    "Championship":     ["Leeds Utd", "Nottingham Forest", "Sheffield Utd",
                         "Norwich City", "Brentford", "Watford"],
    "Champions League": ["Real Madrid", "Barcelona", "Bayern Munich", "Liverpool",
                         "Juventus", "Inter Milan", "AC Milan", "Chelsea", "Man City", "PSG"],
    "Europa League":    ["Sevilla", "Atletico Madrid", "Liverpool", "Man Utd",
                         "Chelsea", "Arsenal", "Juventus"],
    "World Cup":        ["Real Madrid", "Barcelona", "Man Utd", "Bayern Munich", "PSG",
                         "Liverpool", "Juventus", "Inter Milan", "AC Milan",
                         "Chelsea", "Arsenal", "Man City"],
    "Euros":            ["Real Madrid", "Barcelona", "Man Utd", "Bayern Munich", "PSG",
                         "Liverpool", "Juventus", "Inter Milan", "AC Milan",
                         "Chelsea", "Arsenal", "Man City"],
    "Copa America":     ["Real Madrid", "Barcelona", "Liverpool", "Man City", "PSG",
                         "Atletico Madrid", "Juventus", "Inter Milan", "AC Milan"],
    "FA Cup":           ["Man Utd", "Liverpool", "Arsenal", "Chelsea", "Man City",
                         "Tottenham", "Aston Villa", "Newcastle"],
}

def resolve_answers(task_text: str) -> dict:
    """
    Parse the task text and return a dict:
      { "answers": [...], "note": "optional caveat string" }
    Returns empty answers list if we can't determine them.
    """
    t = task_text.lower()
    result = {"answers": [], "note": ""}

    # ── "played for both X & Y" ──────────────────────────────────────────────
    m = re.search(r"played for both (.+?) & (.+)", t)
    if m:
        c1 = m.group(1).strip().title()
        c2 = m.group(2).strip().title()
        # Normalise common variations
        club_norm = {"Man Utd": "Man Utd", "Manchester United": "Man Utd",
                     "Manchester City": "Man City", "Man City": "Man City"}
        c1 = club_norm.get(c1, c1)
        c2 = club_norm.get(c2, c2)
        players = fetch_shared_players(c1, c2)
        result["answers"] = players[:20]
        result["note"] = "Live from FBref — may take a moment"
        return result

    # ── "manager who managed X" ──────────────────────────────────────────────
    m = re.search(r"manager who managed (.+)", t)
    if m:
        club = m.group(1).strip().title()
        mgrs = MANAGERS_BY_CLUB.get(club, [])
        result["answers"] = mgrs
        if not mgrs:
            result["note"] = "No preset data — try a web search"
        return result

    # Detect nationality and club early — used by several branches below
    nat_match = None
    for nat in COUNTRY_DATA:
        if nat.lower() in t:
            nat_match = nat
            break
    club_match = None
    for club in ESPN_LOGOS:
        if club.lower() in t:
            club_match = club
            break

    # ── "[Nationality] player who played for [Club]" ─────────────────────────
    if nat_match and club_match and ("played for" in t or "who" in t):
        players = fetch_club_players_nationality(club_match, nat_match)
        result["answers"] = players
        result["note"] = "All-time players from FBref — current & historical"
        return result

    # ── "stadium in [Country]" ───────────────────────────────────────────────
    m = re.search(r"stadium (?:located )?in (.+)", t)
    if m:
        country = m.group(1).strip().title()
        result["answers"] = STADIUM_ANSWERS.get(country, [])
        result["note"] = "Classic / well-known stadiums shown"
        return result

    # ── "kit color is [Color]" / "home kit color is [Color]" ────────────────
    for color in KIT_COLOR_MAP:
        if color.lower() in t and ("kit" in t or "color" in t or "colour" in t):
            result["answers"] = KIT_ANSWERS.get(color, [])
            result["note"] = "Primary home kit only"
            return result

    # ── "team that has won [Trophy]" — live via Wikidata ─────────────────────
    if "team" in t and "won" in t:
        for trophy in WIKIDATA_COMP_INSTANCE_QIDS:
            if trophy.lower() in t:
                live = fetch_trophy_teams_wikidata(trophy)
                if live:
                    result["answers"] = live
                    result["note"] = "Live from Wikidata — updates after each final"
                else:
                    result["answers"] = TROPHY_TEAM_ANSWERS.get(trophy, [])
                    result["note"] = "Static list (Wikidata unavailable)"
                return result

    # ── "player who has won [Trophy]" — static lookup ────────────────────────
    if ("player" in t or nat_match) and "won" in t:
        for trophy in PLAYER_TROPHY_ANSWERS:
            if trophy.lower() in t:
                result["answers"] = PLAYER_TROPHY_ANSWERS[trophy]
                if nat_match:
                    result["note"] = f"Filter to {nat_match} players"
                return result

    # ── "[Nationality] player with N+ goals in [League]" (template type 11) ──
    # e.g. "Name a French player who has 50+ goals in La Liga"
    # Strategy: pull the league-specific STAT_ANSWERS list, then filter by
    # players known to be of that nationality via FBref cross-reference.
    # If STAT_ANSWERS has no list, fall back to FBref nat+club lookup.
    if nat_match and re.search(r"\d+\+", t) and "goals" in t:
        n = int(re.search(r"(\d+)\+", t).group(1))
        league_hit = None
        for league in ["Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1"]:
            if league.lower() in t:
                league_hit = league
                break

        answered = False
        if league_hit:
            # Try curated league list first
            candidates = [
                (th, lst) for (s, sc, th), lst in STAT_ANSWERS.items()
                if s == "goals" and sc == league_hit and th <= n
            ]
            if candidates:
                # Show full league list with a note to filter by nationality —
                # exact nationality data per scorer isn't in our static store
                best_list = max(candidates, key=lambda x: x[0])[1]
                result["answers"] = best_list
                result["note"] = f"{league_hit} scorers with {n}+ goals · filter to {nat_match} players"
                answered = True

        if not answered:
            # FBref fallback: all players of that nationality at top clubs in that league
            clubs_to_check = LEAGUE_CLUBS.get(league_hit, []) if league_hit else []
            players = []
            for c in clubs_to_check:
                players.extend(fetch_club_players_nationality(c, nat_match))
            seen = set()
            unique_players = [p for p in players if not (p.lower() in seen or seen.add(p.lower()))]
            result["answers"] = unique_players
            league_label = league_hit or "that league"
            result["note"] = f"{nat_match} players at top {league_label} clubs · check goal tallies"
        return result

    # ── N+ stat questions (goals / assists / clean sheets) ───────────────────
    # Parse: stat type, threshold, and scope (career / specific league / CL).
    # Uses keyed STAT_ANSWERS[(stat, scope, threshold)] — no cross-league bleed.
    stat_kw = None
    if "clean sheets" in t:
        stat_kw = "clean_sheets"
    elif "assists" in t:
        stat_kw = "assists"
    elif "goals" in t:
        stat_kw = "goals"

    if stat_kw and re.search(r"\d+\+", t):
        n = int(re.search(r"(\d+)\+", t).group(1))

        # Determine scope: which league/competition the stat is measured in
        SCOPE_KEYWORDS = {
            "Champions League": "Champions League",
            "Premier League":   "Premier League",
            "La Liga":          "La Liga",
            "Serie A":          "Serie A",
            "Bundesliga":       "Bundesliga",
            "Ligue 1":          "Ligue 1",
        }
        scope = "career"
        for kw, label in SCOPE_KEYWORDS.items():
            if kw.lower() in t:
                scope = label
                break
        # "his career" or no league → career
        if "career" in t or "his career" in t:
            scope = "career"

        # Find the closest threshold key at or below n
        def best_key(stat, sc, threshold):
            """Return the STAT_ANSWERS list for the closest threshold ≤ n."""
            candidates = [
                (th, lst) for (s, sc2, th), lst in STAT_ANSWERS.items()
                if s == stat and sc2 == sc and th <= threshold
            ]
            if not candidates:
                return []
            return max(candidates, key=lambda x: x[0])[1]

        answers = best_key(stat_kw, scope, n)

        # If no league-specific list exists but a league was mentioned,
        # fall back to FBref nat+club lookup for that league (no nationality
        # filter — just top clubs — so we get scorers of any nationality)
        if not answers and scope in LEAGUE_CLUBS:
            result["note"] = f"No curated list for {n}+ {stat_kw} in {scope} — showing top-club players"
            # Return empty so Google link shows; avoids wrong data
        else:
            result["answers"] = answers
            league_label = scope if scope != "career" else "career"
            result["note"] = f"Players with {n}+ {stat_kw.replace('_', ' ')} in {league_label}"
        return result

    # ── "[Nationality] player who has played in [League]" (template type 9) ───
    # e.g. "Name a Dutch player who has played in La Liga"
    # Triggered when: nationality detected + domestic league mentioned + "played in"
    # Uses the same LEAGUE_CLUBS map as the stat branch — FBref returns players
    # ordered by matches played, so the list is naturally sorted most→least.
    if nat_match and "played in" in t:
        league_hit = None
        for league in LEAGUE_CLUBS:
            if league.lower() in t:
                league_hit = league
                break
        if league_hit:
            players = []
            for c in LEAGUE_CLUBS[league_hit]:
                players.extend(fetch_club_players_nationality(c, nat_match))
            seen = set()
            unique_players = []
            for p in players:
                k = p.lower()
                if k not in seen:
                    seen.add(k)
                    unique_players.append(p)
            result["answers"] = unique_players
            result["note"] = f"{nat_match} players at top {league_hit} clubs · ordered by appearances"
            return result

    # ── Generic "player who has played in [Competition]" (no nationality filter) ─
    if "played in" in t:
        for trophy in PLAYER_TROPHY_ANSWERS:
            if trophy.lower() in t:
                result["answers"] = PLAYER_TROPHY_ANSWERS[trophy]
                result["note"] = "Players who have appeared in this competition"
                return result

    return result

# ─────────────────────────────────────────────────────────────────────────────
# 5. ENGINES (unchanged)
# ─────────────────────────────────────────────────────────────────────────────

def grid_text_formatter(text):
    text = text.replace("Name a football team whose", "Football teams whose")
    text = re.sub(r"Name a[n]? (\w+) player", r"\1 players", text)
    text = re.sub(r"Name a player", "Players", text)
    text = re.sub(r"Name a team", "Teams", text)
    text = re.sub(r"Name a stadium", "Stadiums", text)
    text = re.sub(r"Name a manager", "Managers", text)
    text = text.replace("players who has", "players who have")
    text = text.replace("Players who has", "Players who have")
    text = text.replace("teams that has", "teams that have")
    text = text.replace("Teams that has", "Teams that have")
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

# ─────────────────────────────────────────────────────────────────────────────
# 6. DYNAMIC QUESTION LOGIC (unchanged)
# ─────────────────────────────────────────────────────────────────────────────

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
        if scope not in STAT_THRESHOLDS[stat]: scope = "Global"
        n_value = random.choice(STAT_THRESHOLDS[stat][scope])
        comp = "Champions League" if scope == "CL" else random.choice(["Premier League", "La Liga", "Serie A"])
        return f"Name a player who has {n_value}+ {stat.lower()} in {'his career' if scope == 'Global' else comp}"
    elif template_type == 11:
        nation = random.choice(["English", "Spanish", "French", "Brazilian", "Argentinian", "German"])
        comp = random.choice(["Premier League", "La Liga", "Bundesliga"])
        target = f"the {comp}" if comp == "Premier League" else comp
        return f"Name {'an' if nation[0].lower() in 'aeiou' else 'a'} {nation} player who has 50+ goals in {target}"
    elif template_type == 1:
        pair = random.sample(clubs_list, 2)
        return f"Name a player who played for both {pair[0]} & {pair[1]}"
    elif template_type == 2:
        n = random.choice(['Brazilian', 'French', 'Spanish', 'Dutch', 'Argentinian', 'Portuguese', 'German', 'Italian', 'Nigerian'])
        return articulate_task(n, random.choice(clubs_list))
    elif template_type == 3:
        target_club = random.choice(['Real Madrid', 'Chelsea', 'Bayern Munich', 'PSG', 'Juventus', 'Barcelona', 'Inter Milan', 'Man Utd', 'Liverpool', 'AC Milan'])
        return f"Name a manager who managed {target_club}"
    elif template_type == 4:
        return f"Name a stadium located in {random.choice(list(STADIUM_COUNTRIES.keys()))}"
    elif template_type == 5:
        return f"Name a football team whose primary home kit color is {random.choice(list(KIT_COLOR_MAP.keys()))}"
    elif template_type == 6:
        comp = random.choice(leagues_comps + ["Euros", "Copa America"])
        needs_the = ["Premier League", "Championship", "FA Cup", "Champions League", "Europa League", "World Cup", "Euros", "Copa America", "Ligue 1", "Serie A", "La Liga", "Bundesliga"]
        target = f"the {comp}" if comp in needs_the else comp
        return f"Name a team that has won {target}"
    elif template_type == 7:
        return articulate_task("player", random.choice(leagues_comps + ["Euros", "Copa America"]), action="has won")
    elif template_type == 8:
        comp = random.choice(["Euros", "Copa America", "World Cup", "Champions League", "Europa League"])
        valid_nation = random.choice(TROPHY_WINNERS.get(comp, EUROPEANS + SOUTH_AMERICANS))
        return articulate_task(valid_nation, comp, action="has won")
    else:
        comp = random.choice(leagues_comps + ["Euros", "Copa America"])
        nation = random.choice(EUROPEANS if comp == "Euros" else SOUTH_AMERICANS if comp == "Copa America" else all_nations)
        return articulate_task(nation, comp, action="has played in")

# ─────────────────────────────────────────────────────────────────────────────
# 7. STATE MANAGEMENT (unchanged)
# ─────────────────────────────────────────────────────────────────────────────

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
    board = [{"task": "KICK OFF", "assets": {"flags":[], "logos":[], "emojis":["🏁"]}}]
    unique_tasks = set()
    attempts = 0
    while len(unique_tasks) < (total_sq - 2) and attempts < 2000:
        new_task = generate_random_task(st.session_state.selected_categories)
        if new_task != "N/A": unique_tasks.add(new_task)
        attempts += 1
    if len(unique_tasks) < (total_sq - 2): return False
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
    return True

# ─────────────────────────────────────────────────────────────────────────────
# 8. UI
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(page_title="Football Path Trivia", layout="wide")

if st.session_state.winner:
    st.balloons()
    st.markdown(f"<div style='text-align:center; padding:100px;'><h1 style='font-size:5rem;'>🥇</h1><h2 style='color:{st.session_state.winner['color']};'>Congratulations {st.session_state.winner['name']}!</h2></div>", unsafe_allow_html=True)
    if st.button("🏟️ Return to Menu", use_container_width=True): reset_all_data()

elif not st.session_state.game_started:
    st.title("⚽ Football Grid Setup")
    with st.container(border=True):
        c1, c2 = st.columns(2)
        st.session_state.grid_size = c1.number_input("Grid Size", 3, 6, 4)
        st.session_state.num_players = c2.number_input("Players", 1, 4, 2)
        st.session_state.selected_categories = st.multiselect("Active Categories", 
            ["Club Connections", "Trophies", "N+ Stats", "Stadiums", "Kits"], 
            default=["Club Connections", "Trophies", "N+ Stats", "Stadiums", "Kits"], key="cat_filter")
        can_start = bool(st.session_state.selected_categories)
    cols = st.columns(st.session_state.num_players)
    st.session_state.player_names = [cols[i].text_input(f"Manager {i+1}", key=f"p{i}") for i in range(st.session_state.num_players)]
    if st.button("🚀 START MATCH", use_container_width=True, type="primary", disabled=not can_start):
        if start_game(): st.rerun()

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
        grid_display_text = grid_text_formatter(item["task"]) if i not in [0, len(st.session_state.grid_map)-1] else item["task"]
        grid_html += f'<div class="grid-item {active}"><div style="width:100%; color:#555; font-size:0.7rem; text-align:left;">#{i:02}</div>{format_header_icons(item["assets"])}<div style="color:#eee; font-weight:600; font-size:0.85rem; line-height:1.2;">{grid_display_text}</div><div style="min-height:35px; display:flex; justify-content:center; align-items:center;">{marks}</div></div>'
    st.markdown(grid_html + "</div>", unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(f"<h3 style='text-align:center; color:{player['color']}; margin-top: -30px; margin-bottom: 10px;'>{player['name']}</h3>", unsafe_allow_html=True)
        if not st.session_state.rolled:
            if st.button("🎲 ROLL DICE", use_container_width=True, type="primary"):
                st.session_state.current_roll = random.randint(1, 3)
                player['prev'], player['pos'] = player['pos'], min(player['pos'] + st.session_state.current_roll, len(st.session_state.grid_map)-1)
                if player['pos'] == len(st.session_state.grid_map)-1:
                    t = generate_random_task(st.session_state.selected_categories)
                    st.session_state.active_final_task = {"text": t, "assets": get_assets(t)}
                st.session_state.rolled = True; st.rerun()
        else:
            is_last = player['pos'] == len(st.session_state.grid_map) - 1
            if is_last:
                st.markdown(f"<div style='text-align:center; font-size:1.3rem; font-weight:800; color:#FFD700; margin-bottom:10px;'>⭐ BONUS QUESTION ⭐</div>", unsafe_allow_html=True)
                task_text = st.session_state.active_final_task['text']
                current_assets = st.session_state.active_final_task['assets']
                bonus_count = 5 if any(x in task_text.lower() for x in ["player who played", "stadium", "team whose", "team that has won"]) else 3
                display_text = smart_pluralize(task_text, bonus_count)
            else:
                st.markdown(f"<div style='text-align:center; font-size:3rem; font-weight:800; margin-bottom:5px;'>🎲 {st.session_state.current_roll}</div>", unsafe_allow_html=True)
                current_assets = st.session_state.grid_map[player['pos']]['assets']
                task_text = st.session_state.grid_map[player['pos']]['task']
                display_text = smart_pluralize(task_text, st.session_state.current_roll)

            with st.container(border=True):
                st.markdown(format_header_icons(current_assets, size_logos="30px", size_emojis="26px"), unsafe_allow_html=True)
                st.markdown(f"<div style='text-align:center; font-size:1.1rem; font-style:italic; font-weight:600; padding: 5px 15px 20px 15px; color:#fff; line-height:1.3;'>{display_text}</div>", unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            if c1.button("✅ Success", key="succ_btn", use_container_width=True):
                if is_last: st.session_state.winner = player
                else: 
                    st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players
                    st.session_state.rolled = False
                st.rerun()
            if c2.button("❌ Fail", key="fail_btn", use_container_width=True):
                player['pos'] = player['prev']
                st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players
                st.session_state.rolled = False
                st.rerun()

            # ── ANSWERS SECTION ──────────────────────────────────────────────
            ans_data = resolve_answers(task_text)
            raw_answers = ans_data.get("answers", [])
            note = ans_data.get("note", "")

            # Deduplicate: strip anything in parentheses before comparing so
            # "Louis van Gaal" and "Louis van Gaal (1st spell)" count as one.
            # Keep the first (most recent) occurrence, discard later duplicates.
            seen_keys = set()
            answers = []
            for ans in raw_answers:
                key = re.sub(r"\s*\(.*?\)", "", ans).strip().lower()
                if key not in seen_keys:
                    seen_keys.add(key)
                    answers.append(ans)

            expander_label = f"👁️ View Answers ({len(answers)})" if answers else "👁️ View Answers"

            with st.expander(expander_label):
                if answers:
                    if note:
                        st.caption(f"ℹ️ {note}")

                    rows_html = "".join(
                        f"<div style='background:#2a2d36; border-radius:6px; padding:6px 10px; margin:4px 0; font-size:0.85rem; color:#e0e0e0;'>⚽ {ans}</div>"
                        for ans in answers
                    )
                    st.markdown(rows_html, unsafe_allow_html=True)
                else:
                    st.info("No preset answers for this question type.")

                # Always show a Google fallback link at the bottom
                search_query = task_text.replace("Name a", "").replace("Name an", "").strip()
                st.markdown(
                    f"""<div style="margin-top:12px;">
                        <a href="https://www.google.com/search?q=football+{search_query.replace(' ', '+')}" target="_blank" style="text-decoration:none;">
                            <div style="background:#333; color:white; padding:10px; border-radius:5px; text-align:center; font-size:0.8rem; border:1px solid #555;">
                                🔍 Search Google for more answers
                            </div>
                        </a>
                    </div>""",
                    unsafe_allow_html=True
                )

        st.markdown("---")
        if not st.session_state.confirm_reset:
            if st.button("🚩 End Game", use_container_width=True): st.session_state.confirm_reset = True; st.rerun()
        else:
            st.warning("Confirm Reset?")
            rc1, rc2 = st.columns(2)
            if rc1.button("Confirm", type="primary", use_container_width=True): reset_all_data()
            if rc2.button("Cancel", use_container_width=True): st.session_state.confirm_reset = False; st.rerun()
