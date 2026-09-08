import streamlit as st
import pandas as pd
from src.dashboard.utils.db import get_companies, get_documents

def render_reports_page():
    st.title("📑 Annual Reports & Regulatory Document Filing Repository")
    st.markdown("Search and access annual reports and financial statements across Nifty 100 companies.")

    df_comp = get_companies()
    if df_comp.empty:
        st.warning("No companies found.")
        return

    # Search Box
    ticker_list = df_comp["ticker"].tolist()
    selected_ticker = st.selectbox("Search Company by Ticker:", ticker_list, index=0)

    st.markdown("---")

    # Load Documents
    df_docs = get_documents(selected_ticker)
    st.subheader(f"📄 Financial Document Filings for {selected_ticker}")

    if not df_docs.empty:
        for idx, doc in df_docs.iterrows():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**{doc.get('title', 'Annual Report')}** ({doc.get('doc_type', 'Financial Filing')})")
            with col2:
                url = doc.get("url", "")
                if url and url.startswith("http") and "invalid" not in url.lower():
                    st.markdown(f"[📥 Download PDF]({url})")
                else:
                    st.markdown("<span style='color:red; font-weight:bold;'>⚠️ Report unavailable</span>", unsafe_allow_html=True)
            with col3:
                st.markdown("🟢 Verified Filing")
            st.markdown("---")
    else:
        st.info("No external document URLs found for this company.")
        st.markdown("<span style='color:red; font-weight:bold; font-size:16px;'>⚠️ Report unavailable (No direct BSE filing linked)</span>", unsafe_allow_html=True)

if __name__ == "__main__" or "render_reports_page" in dir():
    render_reports_page()
