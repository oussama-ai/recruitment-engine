import streamlit as st
import requests
import pandas as pd

# 1. Configuration de la page (Toujours au sommet)
st.set_page_config(
    page_title="AI Recruitment Dashboard", 
    page_icon="📊", 
    layout="wide"  # Mode large pour une meilleure disposition des graphiques
)

# Style CSS personnalisé pour harmoniser les couleurs de l'interface
st.markdown("""
    <style>
    .stProgress > div > div > div > div { background-color: #2ecc71; }
    div[data-testid="stMetricValue"] { font-size: 28px; color: #1abc9c; }
    .job-card { padding: 20px; border-radius: 10px; background-color: #f8f9fa; margin-bottom: 15px; }
    </style>""", unsafe_allow_html=True)

# 2. En-tête de l'application
st.title("💼 AI Smart Recruitment Engine")
st.markdown("Propulsez votre recherche de talents ou d'opportunités grâce à l'analyse sémantique et vectorielle.")
st.divider()

# 3. Zone d'importation du CV
col_input, col_tip = st.columns([3, 1])
with col_input:
    uploaded_file = st.file_uploader("Déposez votre CV au format PDF", type=["pdf"])
with col_tip:
    st.info("💡 **Analyse Locale :** Les compétences et les diplômes sont isolés de manière déterministe et respectueuse de la vie privée.")

# 4. Traitement principal
if uploaded_file is not None:
    if st.button("🔍 Lancer l'Analyse du Profil & Matching", type="primary", use_container_width=True):
        
        with st.spinner("Analyse sémantique du document et interrogation de l'index vectoriel..."):
            try:
                # Appel à l'API FastAPI locale
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                response = requests.post("http://localhost:8000/api/recommend", files=files)
                
                if response.status_code == 200:
                    results = response.json()
                    
                    if not results:
                        st.warning("⚠️ Aucun poste ne correspond de manière significative à ce profil pour le moment.")
                    else:
                        st.success("Analyse terminée avec succès !")
                        
                        # --- PRÉPARATION DES DONNÉES STATISTIQUES ---
                        # Étape A : Calcul des scores de matching
                        scores = [res['score'] for res in results]
                        avg_score = sum(scores) / len(scores)
                        max_score = max(scores)
                        
                        # Étape B : Agrégation des compétences matchées
                        all_matched_skills = []
                        for res in results:
                            all_matched_skills.extend(res.get('matched_skills', []))
                        
                        # Comptage des fréquences pour identifier les compétences clés demandées
                        skill_counts = pd.Series(all_matched_skills).value_counts().reset_index()
                        skill_counts.columns = ['Compétence', 'Fréquence']
                        
                        # --- ARCHITECTURE DU DASHBOARD VIA LES TABS ---
                        tab_analytics, tab_jobs = st.tabs(["📊 Statistiques & Insights Marché", "🎯 Offres d'Emploi Recommandées"])
                        
                        # =========================================================
                        # TAB 1 : ANALYTICS & INSIGHTS
                        # =========================================================
                        with tab_analytics:
                            st.subheader("📈 Vue d'Ensemble Analytique")
                            
                            # Ligne d'indicateurs de performance (KPI Metrics)
                            m1, m2, m3 = st.columns(3)
                            with m1:
                                st.metric(label="Meilleur Match Détecté", value=f"{int(max_score * 100)} %")
                            with m2:
                                st.metric(label="Score de Match Moyen", value=f"{int(avg_score * 100)} %")
                            with m3:
                                st.metric(label="Total Postes Compatibles", value=f"{len(results)} Postes")
                            
                            st.divider()
                            
                            # Section Graphiques : Distribution et Demande Compétences
                            g1, g2 = st.columns(2)
                            
                            with g1:
                                st.markdown("### 🔝 Compétences Clés Valorisées")
                                st.markdown("_Ces compétences présentes dans votre profil maximisent vos scores de matching avec les offres actuelles._")
                                if not skill_counts.empty:
                                    # Graphique à barres horizontal natif Streamlit
                                    st.bar_chart(data=skill_counts.set_index('Compétence').head(8), use_container_width=True)
                                else:
                                    st.caption("Aucune donnée de compétence disponible.")
                                    
                            with g2:
                                st.markdown("### 🎯 Distribution des Scores de Recommandation")
                                st.markdown("_Aperçu de l'adéquation de votre profil vis-à-vis des exigences de notre base de données._")
                                score_df = pd.DataFrame({"Scores": [s * 100 for s in scores]})
                                # Graphique d'adéquation global
                                st.area_chart(score_df, use_container_width=True)
                                
                        # =========================================================
                        # TAB 2 : RECOMMENDED JOBS
                        # =========================================================
                        MIN_SCORE_THRESHOLD = 0.70
                        displayed_jobs = 0
                        with tab_jobs:
                            st.subheader("🎯 Recommandations de Postes Sur-Mesure")
                            st.markdown("Ces rôles ont été extraits par proximité sémantique en fonction de vos compétences.")
                            
                            for index, res in enumerate(results):
                                score_pct = int(res['score'] * 100)
                                
                                # Création d'une carte visuelle pour chaque offre
                                with st.container(border=True):
                                    c1, c2 = st.columns([3, 1])
                                    
                                    with c1:
                                        st.subheader(f"{res['title']}")
                                        st.markdown(f"🏢 **Entreprise :** {res['company']}")
                                        
                                        # Badges de compétences stylisés sous forme de code inline
                                        skills_formatted = " ".join([f"`{skill}`" for skill in res.get('matched_skills', [])])
                                        st.markdown(f"**Compétences Validées :** {skills_formatted}")
                                        
                                    with c2:
                                        # Widget métrique natif pour l'affichage de l'indice de confiance
                                        st.metric(label="Adéquation", value=f"{score_pct}%")
                                        st.progress(res['score'])
                                        
                                    # Zone d'expansion masquant le détail pour ne pas encombrer l'écran
                                    with st.expander("📝 Consulter la description & Postuler"):
                                        st.write(f"Ce poste chez {res['company']} correspond aux critères identifiés lors du parsing sémantique de votre dossier.")
    
                                        # Remplacement du st.button classique par un bouton de redirection web natif
                                        st.link_button("👉 Postuler sur le site de l'entreprise", url=res['url'], type="secondary", use_container_width=True)
                                if res['score'] < MIN_SCORE_THRESHOLD:
                                    continue  # On ignore le poste s'il est en dessous du seuil
        
                                    displayed_jobs += 1
                                    score_pct = int(res['score'] * 100)
                                    # ... (le reste de ton code d'affichage de la carte de job)

                            if displayed_jobs == 0:
                                st.info("💡 Aucun poste ne correspond à votre profil avec un score supérieur à 70%.")
                                        
                else:
                    st.error(f"⚠️ Erreur de communication avec le serveur backend (Code d'état : {response.status_code}).")
                    
            except requests.exceptions.RequestException:
                st.error("🔌 Connexion réseau impossible. Veuillez vérifier que l'API FastAPI tourne correctement sur le port 8000.")