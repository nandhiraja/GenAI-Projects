import warnings
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

# Suppress warnings
def warn(*args, **kwargs):
    pass

warnings.warn = warn
warnings.filterwarnings('ignore')




# Function to read a file and display its content
def read_file(filename):
    with open(filename, 'r') as document:
        content = document.read()
        print(content)

# Function to process the pipeline
def pipe_line(file_path):
    loader = TextLoader(file_path)
    documents = loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)
    print(f"Number of document chunks: {len(texts)}")

    embed = HuggingFaceEmbeddings()
    data = Chroma.from_documents(texts, embed)
    print("Embedding and data preparation: DONE")

    while True:
        query = input('--: Ask the Question : ')
        print('RESPONSE : - \n', get_response(query, data))

# Function to get a response from the model
def get_response(query, data):
    load_dotenv()
    api_key = os.environ.get("GROQ_API_KEY")
    My_llm = ChatGroq(groq_api_key=api_key, model_name="llama-3.2-11b-vision-preview")

    qa = RetrievalQA.from_chain_type(
        llm=My_llm,
        chain_type="stuff",
        retriever=data.as_retriever(),
    )
    qa.return_source_documents = False
    response = qa.invoke(query)
    return response['result']

# Main execution
if __name__ == "__main__":
    doc_path = input(': Enter the file path :_')
    read_file(doc_path)
    pipe_line(doc_path)
