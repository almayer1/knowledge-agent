import json
from pathlib import Path
import streamlit as st
import requests

from config import Settings

settings = Settings()
API_URL = settings.api_url

st.set_page_config(
    page_title="Knowledge Agent",
    page_icon="ᚦ",
    layout="wide"
)

def token_stream(response):
    for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
        if chunk.startswith("{"):
            st.session_state.sources = json.loads(chunk)["sources"]
        else:
            yield chunk

# Sidebar
with st.sidebar:
    st.markdown("<h2 style='font-size:1.3rem; letter-spacing:0.3em; color:#C084FC; margin-bottom:0.2rem;'>ᚦ TERMINAL</h2>", unsafe_allow_html=True)
    st.divider()
    st.markdown("<p style='letter-spacing:0.18em; opacity:0.45; font-size:0.72rem; color:#C084FC;'>⟁ LOAD CORPUS</p>", unsafe_allow_html=True)
    # Ingest
    uploaded_files = st.file_uploader(
        "Upload documents",
        type=["txt", "pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )
    if st.button("⟁ ENCODE INTO VAULT", use_container_width=True):
        if uploaded_files is not None:
            for file in uploaded_files:
                save_path = settings.data_dir / "raw" / file.name
                save_path.write_bytes(file.getvalue())
            try:
                response = requests.post(f"{API_URL}/ingest", json={})

                # Response message
                chunks_added = response.json()["chunks_added"]
                files_processed = response.json()["files_processed"]
                st.success(f"{chunks_added} chunks ingested from {files_processed} files")

                # Warnings
                for warning in response.json()["warnings"]:
                    st.warning(f"Warning: {warning}")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to API — is the server running?")

            
    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()
    st.markdown("<p style='letter-spacing:0.18em; opacity:0.45; font-size:0.72rem; color:#C084FC;'>◈ VAULT STATUS</p>", unsafe_allow_html=True)
    # Stats
    try:
        response = requests.get(f"{API_URL}/stats")
        st.metric("Encoded Nodes", response.json()["chunk_count"])
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to API — is the server running?")

# Main area
st.markdown("""
    <div style='margin-bottom: 0.5rem;'>
        <span style='font-size:0.75rem; letter-spacing:0.5em; color:#C084FC; opacity:0.5;'>⟁ — VAULT ONLINE — ⟁</span>
    </div>
    <h1 style='font-size:3.8rem; letter-spacing:0.35em; margin-bottom:0.2rem; background: linear-gradient(90deg, #C084FC, #818CF8); -webkit-background-clip:text; -webkit-text-fill-color:transparent;'>ᚦ KNOWLEDGE AGENT</h1>
    <p style='font-size:0.85rem; letter-spacing:0.25em; opacity:0.4; margin-bottom:1.5rem; color:#C084FC;'>transmit a query. retrieve wisdom from the vault.</p>
""", unsafe_allow_html=True)
st.divider()
st.markdown("<br>", unsafe_allow_html=True)
question = st.text_input("transmit query")

if "history" not in st.session_state:
    st.session_state.history = []

if "answer" not in st.session_state:
    st.session_state.answer = None

if "sources" not in st.session_state:
    st.session_state.sources = None


if st.button("⟁ TRANSMIT", use_container_width=False):
    if not question:
        st.error("Please enter a question")
    else:
        with st.spinner("ᚦ scanning vault..."): 
            try:
                response = requests.post(
                    f"{API_URL}/ask/stream", 
                    json={
                        "question": question,
                        "history": st.session_state.history[-6:]
                    }, 
                    stream=True
                )
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to API — is the server running?")
        if response.status_code == 200:
            st.session_state.answer = st.write_stream(token_stream(response))
            st.session_state.history.append({"role": "user", "content": question})
            st.session_state.history.append({"role": "assistant", "content": st.session_state.answer}) 
        else:
            st.error(response.json().get("detail", "Something went wrong"))

if st.session_state.answer is not None: 
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("◈ SOURCE NODES — expand to inspect"):
        if st.session_state.sources:
            for i, source in enumerate(st.session_state.sources):
                st.write(f"[Source {i+1}] {source['chunk']['metadata']['source']}")