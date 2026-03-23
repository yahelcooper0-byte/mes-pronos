import streamlit as st
import requests
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="Elite Analyst Pro", layout="centered")

# --- API KEY ---
API_KEY = st.secrets["API_KEY"]
HEADERS = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': 'v3.football.api-sports.io'
}

st.title("💎 ELITE ANALYST PRO")

# --- 1. COMPÉTITION ---
st.subheader("1️⃣ Choisir la Compétition")

col1, col2 = st.columns(2)

with col1:
    zone = st.selectbox("🌍 ZONE", ["France", "Angleterre", "Espagne", "Allemagne", "Italie"])

with col2:
    date_match = st.date_input("📅 DATE", datetime.now())

compets = {
    "France": {"Ligue 1": 61},
    "Angleterre": {"Premier League": 39},
    "Espagne": {"LaLiga": 140},
    "Allemagne": {"Bundesliga": 78},
    "Italie": {"Serie A": 135}
}

tournoi = st.selectbox("🏆 TOURNOI", list(compets[zone].keys()))
st.divider()

# --- 2. SAISON CORRECTE ---
def get_season(date):
    """Retourne la saison en fonction du mois (Juillet → nouvelle saison)."""
    return date.year if date.month >= 7 else date.year - 1

season = get_season(date_match)

# --- 3. MATCHS ---
st.subheader("2️⃣ Sélectionner le Match")

id_ligue = compets[zone][tournoi]
date_str = date_match.strftime('%Y-%m-%d')
url = f"https://v3.football.api-sports.io/fixtures?league={id_ligue}&season={season}&date={date_str}"

try:
    with st.spinner("⏳ Recherche des matchs..."):
        res = requests.get(url, headers=HEADERS).json()
    matchs = res.get('response', [])

    if not matchs:
        st.warning(f"⚠️ Aucun match trouvé pour {tournoi} le {date_str}")
        st.stop()
    else:
        options = {f"{m['teams']['home']['name']} vs {m['teams']['away']['name']}": m for m in matchs}
        choix = st.selectbox("⚽ Match :", list(options.keys()))
        data_m = options[choix]

        if st.button("🔍 ANALYSER", use_container_width=True):
            statut = data_m['fixture']['status']['short']
            st.subheader("📌 Statut du match")
            st.write(data_m['fixture']['status']['long'])

            # --- PRÉ-MATCH ---
            not_started = ["NS", "TBD", "PST"]
            if statut in not_started:
                st.warning("⏳ Match pas encore joué → analyse limitée")
                st.subheader("💰 Conseil Pré-Match")
                st.info("👉 Double chance ou Under 3.5 conseillé (match incertain)")
                st.subheader("🎯 Combiné")
                st.write("🔒 Double chance")
                st.write("🔒 Under 3.5 buts")
                st.stop()

            # --- STATS ---
            fixture_id = data_m['fixture']['id']
            stats_url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={fixture_id}"
            stats_res = requests.get(stats_url, headers=HEADERS).json()
            stats = stats_res.get('response', [])

            if not stats or len(stats) < 2:
                st.warning("⚠️ Pas de statistiques disponibles")
                st.stop()

            def get_stat(team_stats, stat_name):
                for s in team_stats:
                    if s['type'] == stat_name and s['value'] is not None:
                        return s['value']
                return 0

            home = stats[0]['statistics']
            away = stats[1]['statistics']

            shots_home = get_stat(home, "Total Shots") or 0
            shots_away = get_stat(away, "Total Shots") or 0

            poss_home = get_stat(home, "Ball Possession") or "0%"
            poss_away = get_stat(away, "Ball Possession") or "0%"

            # --- AFFICHAGE STATS ---
            st.subheader("📊 Statistiques")
            c1, c2 = st.columns(2)
            c1.metric("Tirs domicile", shots_home)
            c2.metric("Tirs extérieur", shots_away)

            c3, c4 = st.columns(2)
            c3.metric("Possession domicile", poss_home)
            c4.metric("Possession extérieur", poss_away)

            # --- ANALYSE ---
            st.subheader("🧠 Analyse IA")
            if shots_home > shots_away:
                st.success("🏠 Avantage domicile")
            elif shots_away > shots_home:
                st.success("🚀 Avantage extérieur")
            else:
                st.success("⚖️ Match équilibré")

            # --- CONSEIL ---
            st.subheader("💰 Conseil")
            if shots_home > 10 and shots_away > 10:
                st.info("🔥 Over 2.5 buts")
            elif shots_home > shots_away:
                st.info("✅ Victoire domicile")
            else:
                st.info("⚠️ Double chance extérieur")

            # --- COMBINÉ ---
            st.subheader("🎯 Combiné")
            picks = []

            if shots_home > shots_away:
                picks.append("Victoire domicile")
            elif shots_away > shots_home:
                picks.append("Victoire extérieur")
            else:
                picks.append("Match nul")

            if shots_home + shots_away > 5:
                picks.append("Over 2.5 buts")
            elif shots_home + shots_away <= 2:
                picks.append("Under 2.5 buts")

            if abs(shots_home - shots_away) <= 3:
                picks.append("Double chance")

            for p in picks:
                st.write("✅", p)

            # --- SAFE ---
            st.subheader("🛡️ Combiné sécurisé")
            safe = [p for p in picks if "Double chance" in p or "Over" in p]

            if safe:
                for s in safe:
                    st.write("🔒", s)
            else:
                st.write("⚠️ Aucun combiné safe")

except Exception as e:
    st.error(f"⚠️ Erreur API ou connexion: {e}")
