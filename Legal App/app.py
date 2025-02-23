import streamlit as st
import pandas as pd
import json
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq
from langchain.text_splitter import CharacterTextSplitter

# Google Sheets Configuration
SERVICE_ACCOUNT_FILE = ""  # Replace with your service account file
SPREADSHEET_ID = ""  # Replace with your Google Sheet ID

# LLM Configuration
API_KEY = ""  # Replace with your Groq API key
MODEL_NAME = "llama-3.2-11b-vision-preview"
llm = ChatGroq(groq_api_key=API_KEY, model_name=MODEL_NAME)

# Streamlit App
st.set_page_config(page_title="Legal Document Risk Analysis", layout="wide")

# CSS for Custom Styling
st.markdown(
    """
    <style>
    .main-container {
        padding: 2rem;
        background-color: #f8f9fa;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #4a4a4a;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }
    .button-row button {
        margin-right: 10px;
    }
    .chat-container {
        background-color: #ffffff;
        border: 1px solid #dcdcdc;
        border-radius: 10px;
        padding: 1rem;
        margin-top: 1.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Title
st.title("📋 Legal Document Risk Analysis Dashboard")

# Sidebar for Email Configuration
st.sidebar.header("Email Configuration 📧")
sender_email = st.sidebar.text_input("Sender Email", placeholder="Enter sender email...")
#sender_password = st.sidebar.text_input(
#    "Sender Password", placeholder="Enter sender password...", type="password")
recipient_email = st.sidebar.text_input("Recipient Email", placeholder="Enter recipient email...")
subject = "Legal Document Risks and Recommendations"
send_email = st.sidebar.button("Send Email")

# File Upload Section
st.subheader("📄 Upload a Legal Document")
uploaded_file = st.file_uploader("Upload your document (TXT, DOCX, PDF)", type=["txt", "docx", "pdf"])

# Layout for Analysis Results
if uploaded_file:
    st.success("File uploaded successfully!")
    file_content = uploaded_file.read().decode("utf-8")
    
    # Analyze the document
    st.subheader("🔍 Analyzing the document...")
    text_splitter = CharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=20)
    texts = text_splitter.split_text(file_content)
    embed = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = Chroma.from_texts(texts, embed)

    def detect_risks_and_recommendations(text_chunks):
        results = []
        for chunk in text_chunks:
            prompt = (
                f"Analyze the following text and provide a structured response:\n\n"
                f"Text: {chunk}\n\n"
                f"Provide the following details:\n"
                f"- Risks: Summarize potential risks, issues, or hidden dependencies clearly.\n"
                f"- Recommendations: Suggest practical, clear, and actionable recommendations to mitigate the risks.\n\n"
                f"Output format:\n"
                f"Risks: <List the risks in simple bullet points>\n"
                f"Recommendations: <List the recommendations in simple bullet points>"
            )
            response = llm.invoke(prompt)
            response_text = response.content.strip()
            risks, recommendations = "No risks identified.", "No recommendations provided."

            if "Risks:" in response_text and "Recommendations:" in response_text:
                try:
                    risks_start = response_text.index("Risks:") + len("Risks:")
                    recommendations_start = response_text.index("Recommendations:")
                    risks = response_text[risks_start:recommendations_start].strip()
                    recommendations = response_text[recommendations_start + len("Recommendations:"):].strip()
                except ValueError:
                    pass

            results.append({
                "context": chunk,
                "risks": risks,
                "recommendations": recommendations
            })
        return results

    results = detect_risks_and_recommendations(texts)
    df = pd.DataFrame(results)

    # Display Results in a Scrollable Table
    st.subheader("📊 Results")
    st.dataframe(df, height=500)

    # Download Results Button
    st.download_button(
        label="📥 Download Results",
        data=df.to_csv(index=False),
        file_name="risk_analysis.csv",
        mime="text/csv",
    )

    # Save to Google Sheets
    if st.button("Save to Google Sheets"):
        credentials = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=["https://www.googleapis.com/auth/spreadsheets"],
        )
        service = build("sheets", "v4", credentials=credentials)
        sheet = service.spreadsheets()

        values = [["Context", "Risks", "Recommendations"]]
        for result in results:
            values.append([result["context"], result["risks"], result["recommendations"]])

        body = {"values": values}
        sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range="Sheet1!A1",
            valueInputOption="RAW",
            body=body,
        ).execute()
        st.success("Data saved to Google Sheets.")

    # Email Sending Section
    if send_email:
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender_email, sender_password)
            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = recipient_email
            message["Subject"] = subject
            message.attach(
                MIMEText(
                    f"Please find the risk analysis report attached:\n\n"
                    f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit?usp=sharing",
                    "plain"
                )
            )
            server.send_message(message)
            server.quit()
            st.success("Email sent successfully!")
        except Exception as e:
            st.error(f"Failed to send email: {e}")

    # Chat Area
    st.subheader("💬 Chat About the Document")
    query = st.text_input("Type your question here...", placeholder="Ask something about the document")
    if st.button("Get Response"):
        retriever = vector_store.as_retriever()
        qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
        response = qa.invoke(query)
        st.write(response["result"])
