
import streamlit as st


def show_sidebar():
    """Render the sidebar with app info and trusted sources."""
    with st.sidebar:
        st.title("ðŸ’Š SafeMedAI")
        st.markdown("---")
        st.header("ðŸ“– About")
        st.write(
            "SafeMedAI helps you understand medicines safely. "
            "It searches trusted medical sources and uses AI to "
            "give you clear, simple information."
        )
        st.markdown("---")
        st.header("ðŸŒ Trusted Sources")
        for source in ["ðŸ¥ WHO", "ðŸ‡ºðŸ‡¸ FDA", "ðŸ‡¬ðŸ‡§ NHS", "ðŸ¥ Mayo Clinic",
                        "ðŸ“š MedlinePlus", "ðŸ’Š WebMD", "ðŸ’Š Drugs.com"]:
            st.write(source)
        st.markdown("---")
        st.header("âš™ï¸ Setup")
        st.markdown("""
**Free Groq API Key:**
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up (free)
3. Create an API key
4. Paste it in Cell 9
        """)
        st.markdown("---")
        st.caption(
            "âš•ï¸ Educational use only. "
            "Consult a doctor before taking any medicine."
        )


def display_medicine_report(medicine_name: str, report: dict, urdu_report: dict = None):
    """Display the complete medicine report in organized sections."""
    if not report:
        st.error("âŒ Could not generate a report. Please try again.")
        return

    actual_name = report.get("medicine_name", medicine_name)
    st.success(f"âœ… Report ready for: **{actual_name}**")

    summary = report.get("summary", "")
    if summary:
        st.info(f"ðŸ“‹ **Quick Overview:** {summary}")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("âœ… What It Is Used For")
        st.write(report.get("used_for", "Information not available."))

        st.subheader("ðŸ½ï¸ Food Interactions")
        st.write(report.get("food_interactions", "Information not available."))

        st.subheader("ðŸ“¦ Storage Instructions")
        st.write(report.get("storage", "Store as directed on the packaging."))

    with col2:
        st.subheader("âš ï¸ Common Side Effects")
        st.write(report.get("side_effects", "Information not available."))

        st.subheader("ðŸš¨ Important Warnings")
        st.write(report.get("warnings", "Consult your doctor or pharmacist."))

        st.subheader("ðŸ‘¨â€âš•ï¸ When To Consult Doctor")
        st.write(report.get("consult_doctor", "Before starting any new medicine."))

    # Urdu section (if translated)
    if urdu_report:
        st.markdown("---")
        st.subheader("ðŸŒ Ø§Ø±Ø¯Ùˆ Ø±Ù¾ÙˆØ±Ù¹ (Urdu Report)")
        urdu_sections = [
            ("Ø§Ø³ØªØ¹Ù…Ø§Ù„",        urdu_report.get("used_for", "")),
            ("Ù…Ø¶Ø± Ø§Ø«Ø±Ø§Øª",      urdu_report.get("side_effects", "")),
            ("Ø§ÛÙ… Ø§Ø­ØªÛŒØ§Ø·ÛŒÚº",   urdu_report.get("warnings", "")),
            ("Ú©Ú¾Ø§Ù†Û’ Ø³Û’ Ù¾Ø±ÛÛŒØ²", urdu_report.get("food_interactions", "")),
            ("Ø°Ø®ÛŒØ±Û Ú©Ø±Ù†Ø§",    urdu_report.get("storage", "")),
            ("ÚˆØ§Ú©Ù¹Ø± Ø³Û’ Ù…Ù„ÛŒÚº",  urdu_report.get("consult_doctor", "")),
        ]
        for label, content in urdu_sections:
            if content:
                st.markdown(f"**{label}**")
                st.markdown(
                    f'<div style="direction:rtl; text-align:right; font-size:1.05rem; line-height:2; background:#f0fdf4; padding:0.6rem 1rem; border-radius:6px;">{content}</div>',
                    unsafe_allow_html=True
                )

    # Disclaimer
    st.markdown("---")
    st.warning(
        "âš•ï¸ **Medical Disclaimer:** This information is for educational purposes only "
        "and does not constitute medical advice. Always consult a qualified doctor, "
        "pharmacist, or healthcare professional before taking any medication."
    )
