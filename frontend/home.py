import streamlit as st
import requests

# 1. Page Configuration (Keep this at the very top)
st.set_page_config(
    page_title="AI Job Matcher", 
    page_icon="💼", 
    layout="centered" # 'centered' often looks cleaner for focused forms
)

# Optional: Add a little custom CSS to color the progress bar green
st.markdown("""
    <style>
    .stProgress > div > div > div > div { background-color: #4CAF50; }
    </style>""", unsafe_allow_html=True)

# 2. Header Section
st.title("💼 AI Recruitment Engine")
st.markdown("Upload your CV to discover roles that perfectly match your skills and experience.")
st.divider()

# 3. Input Section
col1, col2 = st.columns([3, 1])
with col1:
    uploaded_file = st.file_uploader("Upload your CV (PDF format)", type=["pdf"])
with col2:
    # Adds a helpful professional tip next to the uploader
    st.info("💡 **Tip:** Ensure your CV is up-to-date and clearly lists your technical skills for the best match.")

# 4. Action & Processing
if uploaded_file is not None:
    # Use a button to give the user control over when the API is called
    if st.button("🔍 Analyze Profile & Find Matches", type="primary", use_container_width=True):
        
        with st.spinner("Analyzing your profile and querying the database..."):
            try:
                # Actual API Call
                files = {"file": uploaded_file.getvalue()}
                response = requests.post("http://localhost:8000/api/recommend", files={"file": uploaded_file})
                
                if response.status_code == 200:
                    results = response.json()
                    
                    st.success("Analysis complete! Here are your top matches:")
                    st.markdown("<br>", unsafe_allow_html=True) # Adding a little breathing room
                    
                    # 5. Professional Results Display
                    for index, res in enumerate(results):
                        score_pct = int(res['score'] * 100)
                        
                        # Use a bordered container to create a "Card" effect
                        with st.container(border=True):
                            c1, c2 = st.columns([3, 1])
                            
                            with c1:
                                st.subheader(f"{res['title']}")
                                st.markdown(f"🏢 **Company:** {res['company']}")
                                
                                # Format skills as clean code-style badges
                                skills_formatted = " ".join([f"`{skill}`" for skill in res['matched_skills']])
                                st.markdown(f"**Matched Skills:** {skills_formatted}")
                                
                            with c2:
                                # Use Streamlit's native metric component for a dashboard feel
                                st.metric(label="Match Score", value=f"{score_pct}%")
                                st.progress(res['score'])
                                
                            # Optional: Use an expander to keep the UI clean but offer more depth
                            with st.expander("View Details / Apply"):
                                st.write("Job description summary and next steps can go here.")
                                # Use a unique key for each button
                                st.button("Apply Now", key=f"apply_{index}", type="secondary")
                                
                else:
                    st.error(f"⚠️ We encountered an issue (Status code: {response.status_code}). Please try again later.")
                    
            except requests.exceptions.RequestException as e:
                # Catch connection errors (e.g., if localhost:8000 isn't running)
                st.error("🔌 Connection error. Please ensure the backend server is running.")