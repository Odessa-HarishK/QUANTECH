import streamlit as st
from backend import semantic_search, answer_question

st.set_page_config(
    page_title="QuanTech – Integration Docs",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 QuanTech – Integration Documentation Copilot")
st.caption("HLD • Mapping • DOR (No Jira, No Code)")

query = st.text_input(
    "Ask a question",
    placeholder="Example: What is the SmartComm request/response flow?"
)

if query:
    with st.spinner("Searching documents..."):
        results = semantic_search(query)

    with st.spinner("Generating answer..."):
        answer = answer_question(query, results)

    st.markdown("### ✅ Answer")
    st.markdown(answer)

    with st.expander("🔍 Retrieved Context"):
        for r in results:
            st.markdown(f"**{r['meta']['doc_type']} | {r['meta']['path']}**")
            st.markdown(r["text"][:500] + "…")
            st.divider()