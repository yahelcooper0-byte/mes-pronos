import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Elite Analyst Pro", layout="centered")

# TA CLÉ (Vérifiée sur tes photos)
API_KEY = "6d7a5631b9668010c9842a343394cf1f" 
HEADERS = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': 'v3.football.api-sports.io'}

st.title("💎 ELITE ANALYST PRO")

# --- ÉTAPE 1 : CHOIX ---
zone = st.selectbox("🌍 ZONE", ["France", "Angleterre", "Espagne", "Allemagne", "Italie"])
compets = {
    "France": {"Ligue 1": 61}, "Angleterre": {"Premier League": 39},
    "Espagne": {"LaLiga": 140}, "Allemagne": {"Bundesliga": 78}, "Italie": {"Serie A": 135}
}
tournoi = st.selectbox("🏆 TOURNOI", list(compets[zone].keys()))
date_match = st.date_input("📅 DATE", datetime.now())

# --- ÉTAPE 2 : CALCUL AUTO DE LA SAISON ---
# Si on est entre Janvier et Juin, la saison "officielle" pour l'API est souvent l'année d'avant (ex: Saison 2025 pour un match en Mars 2026)
saison_api = date_match.year - 1 if date_match.month < 7 else date_match.year

id_ligue = compets[zone][tournoi]
date_str = date_match.strftime('%Y-%m-%d')
url = f"https://v3.football.api-sports.io/fixtures?league={id_ligue}&season={saison_api}&date={date_str}"

try:
    res = requests.get(url, headers=HEADERS).json()
    matchs = res.get('response', [])
    
    if matchs:
        # LA SÉLECTION D'ÉQUIPES QUE TU VOULAIS
        options = {f"{m['teams']['home']['name']} vs {m['teams']['away']['name']}": m for m in matchs}
        choix = st.selectbox("⚽ CHOISIS TON MATCH :", list(options.keys()))
        
        if st.button("🚀 LANCER L'ANALYSE"):
            st.success(f"Analyse Elite Analyst pour {choix} lancée !")
    else:
        st.warning(f"Rien trouvé pour le {date_str} (Saison API {saison_api}). Essaie un samedi ou un dimanche !")

except Exception:
    st.error("Erreur de connexion. Vérifie ta clé.")
