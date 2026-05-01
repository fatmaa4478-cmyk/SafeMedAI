import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables (works on Streamlit Cloud via secrets)
load_dotenv()

from modules.search import search_medicine_info
from modules.llm import summarize_with_llm
from modules.translator import translate_to_urdu
from modules.ui_helpers import display_medicine_report, show_sidebar

st.set_page_config(
    page_title="SafeMedAI",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

show_sidebar()

st.title("💊 SafeMedAI")
st.subheader("Safe Medicine Information Assistant")
st.markdown("---")

col1, col2 = st.columns([3, 1])
with col1:
    medicine_name = st.text_input(
        "Enter Medicine Name",
        placeholder="e.g., Paracetamol, Metformin, Amoxicillin..."
    )
with col2:
    language = st.selectbox("Language", ["English", "Urdu (اردو)"])

if st.button("🔍 Analyze Medicine"):
    if not medicine_name.strip():
        st.warning("⚠️ Please enter a medicine name.")
        st.stop()

    groq_api_key = os.getenv("GROQ_API_KEY", "")

    if not groq_api_key:
        st.error("❌ GROQ_API_KEY not set. Please add it in Streamlit secrets.")
        st.stop()

    with st.spinner("🔎 Searching trusted medical sources..."):
        search_results = search_medicine_info(medicine_name.strip())

    if not search_results:
        st.error(f"❌ Could not find information about {medicine_name}. Try the generic name.")
        st.stop()

    with st.spinner("🧠 Analyzing information..."):
        report = summarize_with_llm(medicine_name, search_results, groq_api_key)

    if not report:
        st.error("❌ AI summarization failed. Check your API key and try again.")
        st.stop()

    urdu_report = None
    if "Urdu" in language:
        with st.spinner("🌐 Translating to Urdu..."):
            urdu_report = translate_to_urdu(report, groq_api_key)

    display_medicine_report(medicine_name, report, urdu_report)
