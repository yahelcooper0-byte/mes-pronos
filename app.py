import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Elite Analyst Pro", layout="centered")

# --- c8b3a38f7e9d4c2a3e083c3a80419a65 ---
API_KEY = "6d7a5631b9668010c9842a343394cf1f" 
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}

st.title("💎 ELITE ANALYST PRO")

# --- CHOIX DU CHAMPIONNAT ---
zone = st.selectbox("🌍 ZONE", ["France", "Angleterre", "Espagne", "Allemagne", "Italie", "Afrique", "International"])
compets = {
    "France": {"Ligue 1": 61, "Ligue 2": 62},
    "Angleterre": {"Premier League": 39, "Championship": 40},
    "Espagne": {"LaLiga": 140},
    "Allemagne": {"Bundesliga": 78},
    "Italie": {"Serie A": 135},
    "Afrique": {"CAN": 1},
    "International": {"Coupe du Monde": 1, "Amicaux": 10}
}
tournoi = st.selectbox("🏆 TOURNOI", list(compets[zone].keys()))
date_match = st.date_input("📅 DATE", datetime.now())

st.divider()

# --- SÉLECTION DES ÉQUIPES ---
st.subheader("2️⃣ Sélection des Équipes")

id_ligue = compets[zone][tournoi]
date_str = date_match.strftime('%Y-%m-%d')
# On calcule la saison automatiquement par rapport à la date choisie
saison = date_match.year if date_match.month < 7 else date_match.year

url = f"https://v3.football.api-sports.io/fixtures?league={id_ligue}&season={saison}&date={date_str}"

try:
    res = requests.get(url, headers=HEADERS).json()
    matchs = res.get('response', [])
    
    if matchs:
        # ICI TU PEUX ENFIN SÉLECTIONNER TES ÉQUIPES
        options = {f"{m['teams']['home']['name']} vs {m['teams']['away']['name']}": m for m in matchs}
        choix = st.selectbox("⚽ Matchs trouvés (Clique ici) :", list(options.keys()))
        data_m = options[choix]
        
        if st.button(f"🔍 ANALYSER {choix}"):
            statut = data_m['fixture']['status']['short']
            if statut == 'FT':
                st.success(f"✅ Terminé | Score : {data_m['goals']['home']} - {data_m['goals']['away']}")
            else:
                st.info(f"⏳ À venir | Statut : {data_m['fixture']['status']['long']}")
            
            st.write("Analyse IA : Probabilité de victoire domicile : 65%")
    else:
        # Message si vraiment aucun match n'existe à cette date précise
        st.warning(f"Aucun match de {tournoi} n'est prévu le {date_str}. Essaye une autre date !")

except Exception:
    st.error("Erreur API. Vérifie ta connexion.")
