import streamlit as st

st.set_page_config(page_title="Spectra Guardian Demo", layout="wide")
st.title("Spectra Guardian: Intrusion Response & Mitigation Demo")

st.sidebar.header("Navigation")
st.sidebar.markdown("- Response Dashboard\n- Mitigation Actions\n- Incident Timeline\n- Knowledge Graph View")

st.write("""
Welcome to the Spectra Guardian demo! This dashboard showcases automated and guided response orchestration, mitigation planning, and incident analytics. For production, see our FastAPI+React version.
""")
