# IMPORTING

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.runnables import RunnablePassthrough
import streamlit as st

# AI SETUP

os.environ["GEMINI_API_KEY"] = st.secrets["EXTRA_API_KEY"]
output_cleaner = StrOutputParser()
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)

# DOCUMENT CLEANER

def format_docs(docs):
    return "\n\n---\n\n".join(doc.page_content for doc in docs)

# LOADING WIDGET

@st.cache_resource(show_spinner=False)
def initialize_retriever():

    with st.spinner("Loading Menu Database and AI Assistant.......PLease Wait..."):

        # LOADING DOCUMENT

        PDF_path = "CRAVING_CRUST.pdf"
        st.title(":red[CRAVING CRUST AI]")
        loader = PyPDFLoader(PDF_path)
        pages = loader.load()

        # CHUNKING

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=3000, chunk_overlap=400, separators=["\n\n", "\n", " ", ""]
        )
        chunks = splitter.split_documents(pages)

        # EMBEDDING

        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        vector_db = Chroma.from_documents(documents=chunks, embedding=embeddings)
        retriever = vector_db.as_retriever(search_type="mmr",search_kwargs={"k": 5,"fetch_k": 15})
        return retriever

# DATABASE INITIALIZING 

try:
    retriever = initialize_retriever()
except Exception as e:
    st.error(f"Failed to load PDF database: {e}")
    st.stop()   

# QUESTION 

query = st.text_area("", placeholder="Ask Anything About the Menu")

# PROMPT ENGINEERING

system_prompt = """
you are an restaurant AI fluent in english and urdu. 
Your job is to answer the customer questions on the menu.
Be smart about the questions and try to understand and grasp the user intent as they will not always be clear , they may ask for (price of burger) but not specify which one.
In such cases behave smartly and ouput something related from the menu.
If the answer is long, still output the complete answer regardless of the length.
Use ONLY THE PROVIDED INFORMATION, do not hallucinate. 
If you cannot find the answer in the documents, tell that to the customer directly and clearly.(however if it matches a little still give them the output)
Only accept questions in english/latin script.
If they are in this script but another language like roman urdu or hindi (e.g kese ho app , is cheez ki kya qeemat hai) , accept and answer in the same style.
BEHAVE INTELLIGENTLY
context: {context}
"""
prompt = ChatPromptTemplate.from_messages([("system", system_prompt), ("human", "{question}")])

# CHAINING

chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | output_cleaner
)

# CALLING

response_area = st.empty()
if st.button("ASK"):
    response_area = st.empty()
    with st.spinner("Thinking..."):
        if len(query.strip()) <= 0:
            response_area.write("NO QUESTION ASKED")
        else:
            try:
                response = chain.invoke(query)
                response_area.write(response)
            except Exception as e:
                if "429" in str(e): 
                        st.error( "AW SNAP! our Ai tokens are finished :(")
                else:    
                    st.error(f"OOPS! something went wrong {type(e).__name__}")
else:
    response_area.write("")