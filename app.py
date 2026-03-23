import streamlit as st
import requests
from datetime import datetime

# CONFIG
st.set_page_config(page_title="Elite Analyst Pro", layout="centered")

# 🔐 API KEY (Streamlit secrets)
API_KEY = st.secrets["6d7a5631b9668010c9842a343394cf1f"]
HEADERS = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': 'v3.football.api-sports.io'
}

st.title("💎 ELITE ANALYST PRO")

# --- 1. CHOIX COMPÉTITION ---
st.subheader("1️⃣ Choisir la Compétition")

col1, col2 = st.columns(2)

with col1:
    zone = st.selectbox("🌍 ZONE / PAYS", [
        "France", "Angleterre", "Espagne", "Allemagne", "Italie",
        "Portugal", "Pays-Bas", "Turquie", "Afrique", "Amérique", "International"
    ])

with col2:
    date_match = st.date_input("📅 DATE DU MATCH", datetime.now())

compets = {
    "France": {"Ligue 1": 61, "Ligue 2": 62},
    "Angleterre": {"Premier League": 39, "Championship": 40},
    "Espagne": {"LaLiga": 140},
    "Allemagne": {"Bundesliga": 78},
    "Italie": {"Serie A": 135},
    "Portugal": {"Primeira Liga": 94},
    "Pays-Bas": {"Eredivisie": 88},
    "Turquie": {"Süper Lig": 203},
    "Afrique": {"CAN": 1},
    "Amérique": {"Copa America": 9},
    "International": {"Coupe du Monde": 1}
}

tournoi = st.selectbox("🏆 TOURNOI", list(compets[zone].keys()))
st.divider()

# --- 2. MATCHS ---
st.subheader("2️⃣ Sélectionner le Match")

id_ligue = compets[zone][tournoi]
date_str = date_match.strftime('%Y-%m-%d')

url = f"https://v3.football.api-sports.io/fixtures?league={id_ligue}&season=2025&date={date_str}"

try:
    res = requests.get(url, headers=HEADERS).json()
    matchs = res.get('response', [])

    if not matchs:
        st.info("Aucun match trouvé à cette date.")
    else:
        options = {
            f"{m['teams']['home']['name']} vs {m['teams']['away']['name']}": m
            for m in matchs
        }

        choix = st.selectbox("⚽ Match :", list(options.keys()))
        data_m = options[choix]

        if st.button("🔍 ANALYSER", use_container_width=True):

            fixture_id = data_m['fixture']['id']

            # --- STATS MATCH ---
            stats_url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={fixture_id}"
            stats_res = requests.get(stats_url, headers=HEADERS).json()
            stats = stats_res.get('response', [])

            def get_stat(team_stats, stat_name):
                for s in team_stats:
                    if s['type'] == stat_name:
                        return s['value']
                return 0

            if len(stats) == 2:
                home = stats[0]['statistics']
                away = stats[1]['statistics']

                shots_home = get_stat(home, "Total Shots") or 0
                shots_away = get_stat(away, "Total Shots") or 0

                poss_home = get_stat(home, "Ball Possession") or "0%"
                poss_away = get_stat(away, "Ball Possession") or "0%"

                st.subheader("📊 Statistiques Réelles")

                c1, c2 = st.columns(2)
                c1.metric("Tirs domicile", shots_home)
                c2.metric("Tirs extérieur", shots_away)

                c3, c4 = st.columns(2)
                c3.metric("Possession domicile", poss_home)
                c4.metric("Possession extérieur", poss_away)

                # --- ANALYSE IA ---
                st.subheader("🧠 Analyse IA")

                if shots_home > shots_away:
                    prediction = "🏠 Avantage domicile"
                elif shots_away > shots_home:
                    prediction = "🚀 Avantage extérieur"
                else:
                    prediction = "⚖️ Match équilibré"

                st.success(prediction)

                # --- CONSEIL PARI ---
                st.subheader("💰 Conseil Pari")

                if shots_home > 10 and shots_away > 10:
                    bet = "🔥 Over 2.5 buts"
                elif shots_home > shots_away:
                    bet = "✅ Victoire domicile"
                else:
                    bet = "⚠️ Double chance extérieur"

                st.info(bet)

                # --- COMBINÉ INTELLIGENT ---
                st.subheader("🎯 Suggestions pour Combiné")

                picks = []

                if shots_home > shots_away:
                    picks.append(f"{choix} → Victoire Domicile")

                if shots_away > shots_home:
                    picks.append(f"{choix} → Victoire Extérieur")

                if shots_home > 8 and shots_away > 8:
                    picks.append(f"{choix} → Over 2.5 buts")

                if shots_home > 10 and shots_away > 5:
                    picks.append(f"{choix} → Les deux équipes marquent")

                if abs(shots_home - shots_away) <= 3:
                    picks.append(f"{choix} → Match serré (Double chance)")

                if picks:
                    for p in picks:
                        st.write("✅", p)
                else:
                    st.write("⚠️ Aucun pick fiable")

                # --- COMBINÉ SAFE ---
                st.subheader("🛡️ Combiné Sécurisé")

                safe_picks = [p for p in picks if "Double chance" in p or "Over" in p]

                if safe_picks:
                    for sp in safe_picks:
                        st.write("🔒", sp)
                else:
                    st.write("⚠️ Pas de combiné safe dispo")

            else:
                st.warning("Pas assez de stats disponibles.")

except:
    st.error("⚠️ Erreur API. Vérifie ta clé.")
