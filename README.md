# Minimal RAG Chatbot

A simple, locally-embeddable Retrieval-Augmented Generation (RAG) chatbot using Streamlit, LangChain, and Groq.

## Features
- Minimalist, distraction-free UI.
- In-memory fast Vector Database (Chroma).
- Free local embeddings via HuggingFace `sentence-transformers`.
- Lightning fast LLM inference via Groq.
- Supports PDF, Docx, TXT, and Web URLs.

## Local Setup

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```
2. **Activate the virtual environment:**
   - **Windows:** `.\venv\Scripts\activate`
   - **Mac/Linux:** `source venv/bin/activate`
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure API Key:**
   Create a `.env` file in the root directory and add your Groq API key:
   ```env
   GROQ_API_KEY=your_key_here
   ```
5. **Run the App:**
   ```bash
   streamlit run app.py
   ```

## Deployment

### Option A: Streamlit Community Cloud (Easiest & Free)
1. Push this repository to a GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io) and create a new app connecting to your repository.
3. Before deploying, go to the **Advanced Settings** and add your API key to the **Secrets** section:
   ```toml
   GROQ_API_KEY="your_key_here"
   ```

### Option B: Docker
1. Build the Docker image:
   ```bash
   docker build -t minimal-rag .
   ```
2. Run the container:
   ```bash
   docker run -p 8501:8501 -e GROQ_API_KEY=your_key_here minimal-rag
   ```
