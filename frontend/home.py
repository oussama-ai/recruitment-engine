import streamlit as st
import requests
import pandas as pd

# 1. Configuration de la page
st.set_page_config(
    page_title="AI Smart Engine",
    page_icon="🧠",
    layout="wide", # Supprime les marges étroites génériques
    initial_sidebar_state="expanded"
)

# =========================================================
# STYLE CSS PERSONNALISÉ (KPIs, Badges et Éléments de l'UI)
# =========================================================
st.markdown("""
<style>
    /* Style global des cartes KPI */
    .kpi-card {
        background-color: #f8f9fa;
        padding: 25px 10px !important;
        border-radius: 8px;
        box-shadow: 2px 2px 6px rgba(0,0,0,0.04);
        text-align: center;
        margin-bottom: 15px;
        border-left: 5px solid #6c757d; /* Bordure par défaut */
    }
    .kpi-value {
        font-size: 54px !important;    /* Taille percutante pour le jury */
        font-weight: 800 !important;   /* Ultra-bold */
        color: #1d3557 !important;     /* Bleu foncé contrasté */
        margin: 0 !important;
        line-height: 1.0 !important;
    }
    .kpi-label {
        font-size: 13px !important;
        color: #7f8c8d !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600 !important;
        margin: 0 0 10px 0 !important;
        line-height: 1.2 !important;
    }
    
    /* 🚀 CORRECTIF : Style pour les badges de compétences détectées */
    .skill-badge {
        background-color: #e6f4ea !important; 
        color: #137333 !important; 
        padding: 5px 12px !important; 
        border-radius: 12px !important; 
        font-size: 12px !important; 
        font-weight: 600 !important; 
        margin-right: 6px !important; 
        display: inline-block !important;
        margin-bottom: 6px !important;
        border: 1px solid #ceead6 !important;
        text-transform: capitalize;
    }
</style>
""", unsafe_allow_html=True)

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
            <h4 style="margin: 0; color: #1e466e; font-size: 15px;">💡 Analyse Sémantique Locale</h4>
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
if st.session_state.api_results is None:
    st.title("💼 AI Smart Recruitment Engine")
    st.subheader("Bienvenue dans l'interface d'évaluation sémantique.")
    st.markdown("""
    Veuillez utiliser la barre latérale gauche pour charger un curriculum vitae au format PDF. 
    Le moteur calculera instantanément la proximité sémantique avec les offres d'emploi indexées dans la base de données.
    """)
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

    # Création des onglets principaux
    tab_analytics, tab_jobs = st.tabs(["📈 Statistiques & Alignement", "🎯 Offres Recommandées"])

    # -----------------------------------------------------
    # ONGLET 1 : ANALYTICS & INSIGHTS
    # -----------------------------------------------------
    with tab_analytics:
        m1, m2, m3 = st.columns(3)

        with m1:
            st.markdown(f"""
            <div class="kpi-card" style="border-left: 5px solid #e63946;">
                <div class="kpi-label">Meilleur Score de Match</div>
                <div class="kpi-value">{int(max_score * 100)} %</div>
            </div>
            """, unsafe_allow_html=True)

        with m2:
            st.markdown(f"""
            <div class="kpi-card" style="border-left: 5px solid #457b9d;">
                <div class="kpi-label">Adéquation Moyenne</div>
                <div class="kpi-value">{int(avg_score * 100)} %</div>
            </div>
            """, unsafe_allow_html=True)

        with m3:
            st.markdown(f"""
            <div class="kpi-card" style="border-left: 5px solid #2a9d8f;">
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
            
            # Encapsulation dans un container natif stylisé
            with st.container(border=True):
                c1, c2, c3 = st.columns([3.2, 1, 2.5])
                
                with c1:
                    st.subheader(res['title'])
                    st.markdown(f"🏢 **Entreprise :** `{res['company']}`")
                    
                    #  RENDU VISUEL CORRIGÉ : Les compétences ont maintenant des espaces et un style badge vert
                    matched_skills = res.get('matched_skills', [])
                    if matched_skills:
                        skills_html = "".join([f'<span class="skill-badge">{skill.strip()}</span>' for skill in matched_skills])
                        st.markdown(f"**Compétences Détectées :**<br>{skills_html}", unsafe_allow_html=True)
                    else:
                        st.markdown("**Compétences Détectées :**<br>_Aucune correspondance directe._", unsafe_allow_html=True)
                    
                with c2:
                    st.metric(label="Indice de match", value=f"{score_pct}%")
                    st.progress(res['score'])
                
                with c3:
                    # SECTION SKILL GAP ANALYSIS
                    st.markdown("##### 🔍 Analyse des Écarts (Skill Gap)")
                    missing = res.get('missing_skills', [])
                    
                    if missing:
                        st.warning("Compétences clés à acquérir pour cette offre :")
                        
                        badges_html = ""
                        for skill in missing:
                            badges_html += f"""
                            <span style="
                                background-color: #fceade; 
                                color: #d9381e; 
                                padding: 4px 10px; 
                                border-radius: 12px; 
                                font-size: 12px; 
                                font-weight: 600; 
                                margin-right: 6px; 
                                display: inline-block;
                                margin-bottom: 6px;
                                border: 1px solid #f5c2b8;
                            ">{skill.strip()}</span>
                            """
                        st.markdown(badges_html, unsafe_allow_html=True)
                    else:
                        st.success("✨ Excellent ! Votre profil couvre l'intégralité des compétences clés de cette offre.")
                
                # Descriptif masqué pour ne pas encombrer la vue globale
                with st.expander("📝 Voir les détails de l'opportunité"):
                    st.markdown("**Description sommaire de l'offre :**")
                    st.write(f"Ce poste chez {res['company']} requiert l'alignement sur les compétences validées ci-dessus.")
                    st.divider()
                    st.link_button("👉 Ouvrir l'offre d'emploi originale", url=res['url'], use_container_width=True)
                    
        if displayed_jobs == 0:
            st.info("💡 Aucun poste ne correspond au profil avec un score supérieur au seuil minimal.")