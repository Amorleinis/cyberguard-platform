import streamlit as st

st.set_page_config(page_title="Spectra Sentry Demo", layout="wide")
st.title("Spectra Sentry: Intrusion Prevention & Detection Demo")

st.sidebar.header("Navigation")
st.sidebar.markdown("- Dashboard\n- Alerts\n- Asset Risk\n- Knowledge Graph View")

st.write("""
Welcome to the Spectra Sentry demo! This dashboard showcases real-time intrusion detection, asset risk scoring, and knowledge graph analytics. For production, see our FastAPI+React version.
""")
