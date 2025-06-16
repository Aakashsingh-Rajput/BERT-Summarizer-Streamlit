from summarizer import Summarizer
import streamlit as st
from PyPDF2 import PdfReader

# Initialize model
model = Summarizer()

# Page config
st.set_page_config(page_title="BERT Text Summarizer", layout="wide")

# Session state for summary history
if "history" not in st.session_state:
    st.session_state.history = []

# --- TITLE + INFO ---
st.title("🧠 BERT-based Text Summarizer")
st.markdown(
    "This app uses a **pre-trained BERT model** to extract key sentences and generate a concise summary. "
    "Paste text or upload a file, then click **Summarize**!"
)

# --- TEXT INPUT SECTION ---
st.subheader("📄 Input Options")
input_type = st.radio("Choose input method:", ["Paste Text", "Upload File (TXT/PDF)"])

text_input = ""
if input_type == "Paste Text":
    text_input = st.text_area("Paste your article or paragraph here:", height=300)
else:
    uploaded_file = st.file_uploader("Upload a .txt or .pdf file", type=["txt", "pdf"])
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            reader = PdfReader(uploaded_file)
            text_input = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
        else:
            text_input = uploaded_file.read().decode("utf-8")

if text_input:
    st.markdown(f"✏️ **Word Count:** {len(text_input.split())} words")

# --- SETTINGS SECTION ---
with st.expander("⚙️ Settings", expanded=False):
    summary_type = st.radio("Choose summary type:", ["Minimum Length (chars)", "Number of Sentences", "Ratio"])
    if summary_type == "Minimum Length (chars)":
        min_len = st.slider("Minimum Summary Length (in characters):", 20, 500, 50, 10)
    elif summary_type == "Number of Sentences":
        num_sent = st.slider("Number of Sentences:", 1, 10, 3)
    else:
        ratio = st.slider("Summary Ratio (0.1 = 10%, 1.0 = 100%):", 0.1, 1.0, 0.3)

# --- SUMMARY BUTTONS ---
summary_text = ""
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("✂️ Summarize"):
        if not text_input.strip():
            st.warning("⚠️ Please enter or upload some text.")
        elif len(text_input.split()) < 20:
            st.info("ℹ️ Please enter at least 20 words.")
        else:
            with st.spinner("Summarizing..."):
                if summary_type == "Minimum Length (chars)":
                    summary_text = model(text_input, min_length=min_len)
                elif summary_type == "Number of Sentences":
                    summary_text = model(text_input, num_sentences=num_sent)
                else:
                    summary_text = model(text_input, ratio=ratio)

                st.subheader("📝 Summary Output")
                st.success(summary_text)

                st.markdown("📊 **Summary Stats**")
                st.write(f"- Original Length: {len(text_input.split())} words")
                st.write(f"- Summary Length: {len(summary_text.split())} words")

                st.download_button(
                    label="📥 Download Summary",
                    data=summary_text,
                    file_name="summary.txt",
                    mime="text/plain",
                )

                # Store in history
                st.session_state.history.append({
                    "input": text_input,
                    "summary": summary_text
                })

with col2:
    if st.button("🔁 Reset App"):
        st.session_state.clear()
        st.experimental_rerun()

with col3:
    st.caption("Built with ❤️ by Aakashsingh Rajput using Streamlit + BERT")

# --- HISTORY ---
if st.session_state.history:
    with st.expander("📚 Summary History", expanded=False):
        for i, item in enumerate(st.session_state.history[::-1], 1):
            st.markdown(f"**{i}. Original Text (preview):** {item['input'][:150]}...")
            st.markdown(f"**Summary:** {item['summary']}")
            st.markdown("---")

st.markdown("---")
