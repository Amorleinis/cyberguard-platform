import streamlit as st

st.set_page_config(page_title="Spectra Phoenix Demo", layout="wide")
st.title("Spectra Phoenix: Intrusion Recovery & Self-Healing Demo")

st.sidebar.header("Navigation")
st.sidebar.markdown("- Recovery Dashboard\n- Self-Healing Actions\n- System Status\n- Knowledge Graph View")

st.write("""
Welcome to the Spectra Phoenix demo! This dashboard showcases automated recovery, self-healing orchestration, and system restoration analytics. For production, see our FastAPI+React version.
""")
