import os
import tempfile
import streamlit as st
from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader, WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

st.set_page_config(page_title="Minimal RAG", page_icon="📓", layout="centered")

# Custom CSS removed to prevent black screen / theme conflicts

@st.cache_resource(show_spinner=False)
def get_embeddings():
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def process_documents(uploaded_files, web_url):
    docs = []
    
    if uploaded_files:
        for file in uploaded_files:
            ext = os.path.splitext(file.name)[1].lower()
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
                temp_file.write(file.read())
                temp_path = temp_file.name
                
            try:
                if ext == '.pdf':
                    loader = PyPDFLoader(temp_path)
                elif ext == '.docx':
                    loader = Docx2txtLoader(temp_path)
                elif ext == '.txt':
                    loader = TextLoader(temp_path, encoding='utf-8')
                else:
                    st.warning(f"Unsupported file type: {ext}")
                    continue
                
                docs.extend(loader.load())
            except Exception as e:
                st.error(f"Error loading {file.name}: {e}")
            finally:
                os.remove(temp_path)
                
    if web_url:
        try:
            loader = WebBaseLoader(web_url)
            docs.extend(loader.load())
        except Exception as e:
            st.error(f"Error loading URL: {e}")
            
    if not docs:
        return None
        
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    
    embeddings = get_embeddings()
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
    return vectorstore

def create_rag_chain(vectorstore, groq_api_key):
    llm = ChatGroq(
        api_key=groq_api_key,
        model_name="llama-3.3-70b-versatile",
        temperature=0.3
    )
    
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    
    system_prompt = (
        "You are an intelligent, concise assistant. Use the following pieces of retrieved context "
        "to answer the question. If you don't know the answer based on the context, say so gracefully.\n\n"
        "Context:\n{context}"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])
    
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
        
    rag_chain = (
        {"context": retriever | format_docs, "input": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain

st.title("Knowledge Base")
st.markdown("Upload documents or provide a URL, then ask questions.")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "chain" not in st.session_state:
    st.session_state.chain = None

with st.sidebar:
    st.header("Settings & Data")
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets["GROQ_API_KEY"]
        except Exception:
            pass
    if not api_key:
        api_key = st.text_input("Enter Groq API Key:", type="password", help="Get this from console.groq.com")
        
    st.divider()
    
    uploaded_files = st.file_uploader(
        "Upload Files", 
        type=["txt", "pdf", "docx"], 
        accept_multiple_files=True
    )
    
    web_url = st.text_input("Or enter a Web URL:")
    
    if st.button("Process Knowledge", use_container_width=True):
        if not api_key:
            st.error("Please provide a Groq API Key.")
        elif not uploaded_files and not web_url:
            st.warning("Please upload files or provide a URL.")
        else:
            with st.spinner("Processing documents..."):
                vectorstore = process_documents(uploaded_files, web_url)
                if vectorstore:
                    st.session_state.vectorstore = vectorstore
                    st.session_state.chain = create_rag_chain(vectorstore, api_key)
                    st.success("Knowledge base ready!")
                else:
                    st.error("Failed to extract content.")
                    
    st.divider()
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if st.session_state.chain is None:
    st.info("Please add data in the sidebar and click 'Process Knowledge' to begin.")
else:
    if prompt := st.chat_input("Ask a question about your documents..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    answer = st.session_state.chain.invoke(prompt)
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"Error generating response: {e}")
