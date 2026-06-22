# import streamlit as st
# import requests
# import pandas as pd

# # 1. Configuration de la page (Toujours au sommet)
# st.set_page_config(
#     page_title="AI Recruitment Dashboard", 
#     page_icon="📊", 
#     layout="wide"  # Mode large pour une meilleure disposition des graphiques
# )

# # Style CSS personnalisé pour harmoniser les couleurs de l'interface
# st.markdown("""
#     <style>
#     .stProgress > div > div > div > div { background-color: #2ecc71; }
#     div[data-testid="stMetricValue"] { font-size: 28px; color: #1abc9c; }
#     .job-card { padding: 20px; border-radius: 10px; background-color: #f8f9fa; margin-bottom: 15px; }
#     </style>""", unsafe_allow_html=True)

# # 2. En-tête de l'application
# st.title("💼 AI Smart Recruitment Engine")
# st.markdown("Propulsez votre recherche de talents ou d'opportunités grâce à l'analyse sémantique et vectorielle.")
# st.divider()

# # 3. Zone d'importation du CV
# col_input, col_tip = st.columns([3, 1])
# with col_input:
#     uploaded_file = st.file_uploader("Déposez votre CV au format PDF", type=["pdf"])
# with col_tip:
#     st.info("💡 **Analyse Locale :** Les compétences et les diplômes sont isolés de manière déterministe et respectueuse de la vie privée.")

# # 4. Traitement principal
# if uploaded_file is not None:
#     if st.button("🔍 Lancer l'Analyse du Profil & Matching", type="primary", use_container_width=True):
        
#         with st.spinner("Analyse sémantique du document et interrogation de l'index vectoriel..."):
#             try:
#                 # Appel à l'API FastAPI locale
#                 files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
#                 response = requests.post("http://localhost:8000/api/recommend", files=files)
                
#                 if response.status_code == 200:
#                     results = response.json()
                    
#                     if not results:
#                         st.warning("⚠️ Aucun poste ne correspond de manière significative à ce profil pour le moment.")
#                     else:
#                         st.success("Analyse terminée avec succès !")
                        
#                         # --- PRÉPARATION DES DONNÉES STATISTIQUES ---
#                         # Étape A : Calcul des scores de matching
#                         scores = [res['score'] for res in results]
#                         avg_score = sum(scores) / len(scores)
#                         max_score = max(scores)
                        
#                         # Étape B : Agrégation des compétences matchées
#                         all_matched_skills = []
#                         for res in results:
#                             all_matched_skills.extend(res.get('matched_skills', []))
                        
#                         # Comptage des fréquences pour identifier les compétences clés demandées
#                         skill_counts = pd.Series(all_matched_skills).value_counts().reset_index()
#                         skill_counts.columns = ['Compétence', 'Fréquence']
                        
#                         # --- ARCHITECTURE DU DASHBOARD VIA LES TABS ---
#                         tab_analytics, tab_jobs = st.tabs(["📊 Statistiques & Insights Marché", "🎯 Offres d'Emploi Recommandées"])
                        
#                         # =========================================================
#                         # TAB 1 : ANALYTICS & INSIGHTS
#                         # =========================================================
#                         with tab_analytics:
#                             st.subheader("📈 Vue d'Ensemble Analytique")
                            
#                             # Ligne d'indicateurs de performance (KPI Metrics)
#                             m1, m2, m3 = st.columns(3)
#                             with m1:
#                                 st.metric(label="Meilleur Match Détecté", value=f"{int(max_score * 100)} %")
#                             with m2:
#                                 st.metric(label="Score de Match Moyen", value=f"{int(avg_score * 100)} %")
#                             with m3:
#                                 st.metric(label="Total Postes Compatibles", value=f"{len(results)} Postes")
                            
#                             st.divider()
                            
#                             # Section Graphiques : Distribution et Demande Compétences
#                             g1, g2 = st.columns(2)
                            
#                             with g1:
#                                 st.markdown("### 🔝 Compétences Clés Valorisées")
#                                 st.markdown("_Ces compétences présentes dans votre profil maximisent vos scores de matching avec les offres actuelles._")
#                                 if not skill_counts.empty:
#                                     # Graphique à barres horizontal natif Streamlit
#                                     st.bar_chart(data=skill_counts.set_index('Compétence').head(8), use_container_width=True)
#                                 else:
#                                     st.caption("Aucune donnée de compétence disponible.")
                                    
#                             with g2:
#                                 st.markdown("### 🎯 Distribution des Scores de Recommandation")
#                                 st.markdown("_Aperçu de l'adéquation de votre profil vis-à-vis des exigences de notre base de données._")
#                                 score_df = pd.DataFrame({"Scores": [s * 100 for s in scores]})
#                                 # Graphique d'adéquation global
#                                 st.area_chart(score_df, use_container_width=True)
                                
#                         # =========================================================
#                         # TAB 2 : RECOMMENDED JOBS
#                         # =========================================================
#                         MIN_SCORE_THRESHOLD = 0.70
#                         displayed_jobs = 0
#                         with tab_jobs:
#                             st.subheader("🎯 Recommandations de Postes Sur-Mesure")
#                             st.markdown("Ces rôles ont été extraits par proximité sémantique en fonction de vos compétences.")
                            
#                             for index, res in enumerate(results):
#                                 score_pct = int(res['score'] * 100)
                                
#                                 # Création d'une carte visuelle pour chaque offre
#                                 with st.container(border=True):
#                                     c1, c2 = st.columns([3, 1])
                                    
#                                     with c1:
#                                         st.subheader(f"{res['title']}")
#                                         st.markdown(f"🏢 **Entreprise :** {res['company']}")
                                        
#                                         # Badges de compétences stylisés sous forme de code inline
#                                         skills_formatted = " ".join([f"`{skill}`" for skill in res.get('matched_skills', [])])
#                                         st.markdown(f"**Compétences Validées :** {skills_formatted}")
                                        
#                                     with c2:
#                                         # Widget métrique natif pour l'affichage de l'indice de confiance
#                                         st.metric(label="Adéquation", value=f"{score_pct}%")
#                                         st.progress(res['score'])
                                        
#                                     # Zone d'expansion masquant le détail pour ne pas encombrer l'écran
#                                     with st.expander("📝 Consulter la description & Postuler"):
#                                         st.write(f"Ce poste chez {res['company']} correspond aux critères identifiés lors du parsing sémantique de votre dossier.")
    
#                                         # Remplacement du st.button classique par un bouton de redirection web natif
#                                         st.link_button("👉 Postuler sur le site de l'entreprise", url=res['url'], type="secondary", use_container_width=True)
#                                 if res['score'] < MIN_SCORE_THRESHOLD:
#                                     continue  # On ignore le poste s'il est en dessous du seuil
        
#                                     displayed_jobs += 1
#                                     score_pct = int(res['score'] * 100)
#                                     # ... (le reste de ton code d'affichage de la carte de job)

#                             if displayed_jobs == 0:
#                                 st.info("💡 Aucun poste ne correspond à votre profil avec un score supérieur à 70%.")
                                        
#                 else:
#                     st.error(f"⚠️ Erreur de communication avec le serveur backend (Code d'état : {response.status_code}).")
                    
#             except requests.exceptions.RequestException:
#                 st.error("🔌 Connexion réseau impossible. Veuillez vérifier que l'API FastAPI tourne correctement sur le port 8000.")


import streamlit as st
import requests
import pandas as pd

# 1. Configuration de la page
st.set_page_config(
    page_title="AI Smart Engine",
    page_icon="🧠",
    layout="wide", # This removes the generic narrow margins
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé pour moderniser l'aspect visuel (Cartes et Ombres)
import streamlit as st

# Custom CSS for KPI Cards
st.markdown("""
<style>
    .kpi-card {
        background-color: #f8f9fa;
        border-left: 5px solid #e63946;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
        text-align: center;
        margin-bottom: 15px;
    }
    .kpi-value {
        font-size: 48px;
        font-weight: bold;
        color: #1d3557;
        margin: 0;
    }
    .kpi-label {
        font-size: 13px;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 5px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)
# Render your metrics inside columns using the styles

# Initialisation du Session State pour éviter que l'affichage ne disparaisse au clic sur les onglets
if "api_results" not in st.session_state:
    st.session_state.api_results = None

# =========================================================
# BARRE LATÉRALE (SIDEBAR) : Zone de contrôle et d'import
# =========================================================
with st.sidebar:
    st.image("https://img.icons8.com/fluent/96/000000/brain.png", width=80)
    st.title("AI Smart Engine")
    st.markdown("Structurez vos processus de recrutement par IA sémantique.")
    st.divider()
    
    st.subheader("📥 Importer le Profil")
    uploaded_file = st.file_uploader("Déposez le CV (Format PDF)", type=["pdf"], label_visibility="collapsed")
    
    st.divider()
    st.sidebar.markdown("""
        <div style="background-color: #eef4f8; border-radius: 8px; padding: 15px; border-left: 4px solid #3a86c8; margin-top: 20px;">
            <h4 style="margin-0; color: #1e466e; font-size: 15px;">💡 Analyse Sémantique Locale</h4>
            <p style="font-size: 13px; color: #4a5568; line-height: 1.4; margin-bottom: 0;">
                L'extraction de l'arbre de compétences s'effectue via des modèles de deep learning <strong>(GLiNER & SpaCy)</strong> respectueux de la confidentialité de vos données.
            </p>
        </div>
        """, unsafe_allow_html=True)
    # Bouton de traitement principal dans la sidebar
    if uploaded_file is not None:
        if st.button("🔍 Lancer le Matching", type="primary", use_container_width=True):
            with st.spinner("Analyse sémantique et calcul vectoriel en cours..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    response = requests.post("http://localhost:8000/api/recommend", files=files)
                    
                    if response.status_code == 200:
                        st.session_state.api_results = response.json()
                        if not st.session_state.api_results:
                            st.warning("⚠️ Aucun poste ne correspond de manière significative.")
                    else:
                        st.error(f"❌ Erreur Serveur Backend ({response.status_code})")
                except requests.exceptions.RequestException:
                    st.error("🔌 API locale introuvable sur le port 8000.")

# =========================================================
# PANNEAU CENTRAL : Dashboard Analytique & Résultats
# =========================================================
# Titre dynamique selon l'état de l'application
if st.session_state.api_results is None:
    st.title("💼 AI Smart Recruitment Engine")
    st.subheader("Bienvenue dans l'interface d'évaluation sémantique.")
    st.markdown("""
    Veuillez utiliser la barre latérale gauche pour charger un curriculum vitae au format PDF. 
    Le moteur calculera instantanément la proximité sémantique avec les offres d'emploi indexées dans la base de données.
    """)
    
    # Placeholder visuel propre avant chargement
    st.image("https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=1200", use_container_width=True)

else:
    results = st.session_state.api_results
    
    # Traitement des données statistiques
    scores = [res['score'] for res in results]
    avg_score = sum(scores) / len(scores) if scores else 0
    max_score = max(scores) if scores else 0
    
    all_matched_skills = []
    for res in results:
        all_matched_skills.extend(res.get('matched_skills', []))
    
    skill_counts = pd.Series(all_matched_skills).value_counts().reset_index()
    skill_counts.columns = ['Compétence', 'Fréquence']

    # En-tête du Dashboard de résultats
    st.title("📊 Analyse du Profil & Insights")
    st.markdown("Résultats de l'alignement sémantique du profil importé avec le marché cible.")
    st.divider()

    # Création des onglets principaux (hors du st.button pour stabiliser l'UI)
    tab_analytics, tab_jobs = st.tabs(["📈 Statistiques & Alignement", "🎯 Offres Recommandées"])

    # -----------------------------------------------------
    # ONGLET 1 : ANALYTICS & INSIGHTS
    # -----------------------------------------------------
    with tab_analytics:
        # Ligne d'indicateurs de performance clés (KPIs)
        m1, m2, m3 = st.columns(3)

        with m1:
            st.markdown(f"""
            <div class="kpi-card" style="border-left-color: #e63946;">
                <div class="kpi-label">Meilleur Score de Match</div>
                <div class="kpi-value">{int(max_score * 100)} %</div>
            </div>
            """, unsafe_allow_html=True)

        with m2:
            st.markdown(f"""
            <div class="kpi-card" style="border-left-color: #457b9d;">
                <div class="kpi-label">Adéquation Moyenne</div>
                <div class="kpi-value">{int(avg_score * 100)} %</div>
            </div>
            """, unsafe_allow_html=True)

        with m3:
            st.markdown(f"""
            <div class="kpi-card" style="border-left-color: #2a9d8f;">
                <div class="kpi-label">Postes Identifiés</div>
                <div class="kpi-value">{len(results)} Rôles</div>
            </div>
            """, unsafe_allow_html=True)

            st.divider()
        # Section Graphiques
        g1, g2 = st.columns([1, 1])
        with g1:
            st.markdown("### 🔝 Compétences Clés Valorisées")
            if not skill_counts.empty:
                st.bar_chart(data=skill_counts.set_index('Compétence').head(8), use_container_width=True, color="#1abc9c")
            else:
                st.caption("Aucune donnée de compétence disponible.")
                
        with g2:
            st.markdown("### 🎯 Distribution de Densité de Correspondance")
            score_df = pd.DataFrame({"Score de correspondance (%)": [s * 100 for s in scores]})
            st.area_chart(score_df, use_container_width=True, color="#34495e")

    # -----------------------------------------------------
    # ONGLET 2 : OFFRES RECOMMANDÉES
    # -----------------------------------------------------
    with tab_jobs:
        st.markdown(f"### {len(results)} Postes filtrés triés par ordre de pertinence sémantique")
        
        MIN_SCORE_THRESHOLD = 0.40
        displayed_jobs = 0
        
        for res in results:
            if res['score'] < MIN_SCORE_THRESHOLD:
                continue
                
            displayed_jobs += 1
            score_pct = int(res['score'] * 100)
            
            # Encapsulation dans un container natif stylisé avec bordure douce
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                
                with c1:
                    st.subheader(res['title'])
                    st.markdown(f"🏢 **Entreprise :** `{res['company']}`")
                    
                    # Rendu visuel propre des badges de compétences
                    skills_html = "".join([f'<span class="skill-badge">{skill}</span>' for skill in res.get('matched_skills', [])])
                    st.markdown(f"**Compétences Détectées :** <br>{skills_html}", unsafe_allow_html=True)
                    
                with c2:
                    st.metric(label="Indice de confiance", value=f"{score_pct}%")
                    st.progress(res['score'])
                
                # Descriptif masqué pour ne pas encombrer la vue globale
                with st.expander("📝 Voir les détails de l'opportunité"):
                    st.markdown("**Description sommaire de l'offre :**")
                    st.write(f"Ce poste chez {res['company']} requiert l'alignement sur les compétences validées ci-dessus.")
                    st.divider()
                    st.link_button("👉 Ouvrir l'offre d'emploi originale", url=res['url'], use_container_width=True)
                    
        if displayed_jobs == 0:
            st.info("💡 Aucun poste ne correspond au profil avec un score suffisant.")