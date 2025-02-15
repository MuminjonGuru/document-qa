import streamlit as st
from openai import OpenAI
import pdfplumber
import docx

# Set page title
st.set_page_config(page_title="📄 Document Question Answering")

# Sidebar for API key
st.sidebar.title("Settings")
openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")

if not openai_api_key:
    st.sidebar.info("Please enter your OpenAI API key.", icon="🗝️")
    st.stop()

# Create OpenAI client
client = OpenAI(api_key=openai_api_key)

# Main UI
st.title("📄 Document Question Answering")
st.write("Upload a document and ask a question about it – GPT will answer!")

# File uploader
uploaded_file = st.file_uploader(
    "Upload a document (TXT, MD, PDF, DOCX)", 
    type=["txt", "md", "pdf", "docx"]
)

# Function to extract text from different file types
def extract_text(file):
    if file.type == "text/plain":  # TXT
        return file.read().decode("utf-8")
    elif file.type == "text/markdown":  # Markdown
        return file.read().decode("utf-8")
    elif file.type == "application/pdf":  # PDF
        with pdfplumber.open(file) as pdf:
            return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":  # DOCX
        doc = docx.Document(file)
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)
    return ""

if uploaded_file:
    document_text = extract_text(uploaded_file)
    st.success(f"Uploaded: {uploaded_file.name}")

    # Question input
    question = st.text_area("Ask a question about the document", placeholder="Can you give me a short summary?")

    if question:
        with st.spinner("Generating response..."):
            messages = [
                {"role": "user", "content": f"Here's a document: {document_text[:2000]} \n\n---\n\n {question}"}
            ]

            try:
                stream = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    stream=True,
                )
                st.write_stream(stream)
            except Exception as e:
                st.error(f"Error: {e}")
