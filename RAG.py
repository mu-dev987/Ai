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

# LOAGIND WIDGET WHILE DOCUMENT AND AI SETUP

def format_docs(docs):
    return "\n\n---\n\n".join(doc.page_content for doc in docs)

with st.spinner("Loading Menu Database and AI Assistant...PLease Wait..."):

    # INITIAL SETUP

    os.environ["GEMINI_API_KEY"] = st.secrets["MY_API_KEY"]
    output_cleaner = StrOutputParser()
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)
    PDF_path = "CRAVING_CRUST.pdf"
    st.title(":red[CRAVING CRUST AI]")
    st.spinner("loading...")




    st.spinner("Loading...")
    # LOADING DOCUMENT

    loader = PyPDFLoader(PDF_path)
    pages = loader.load()

    # CHUNKING

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600, chunk_overlap=100, separators=["/n/n", "/n", ".", ""]
    )
    chunks = splitter.split_documents(pages)

    # EMBEDDING

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    v_db = Chroma.from_documents(documents=chunks, embedding=embeddings)
    retriever = v_db.as_retriever(search_kwargs={"k": 6})
    query = st.text_area("", placeholder="Ask Anything About the Menu")

# PROMPT ENGINEERING

system_prompt = """
you are an restaurant AI. 
Your job is to answer the customer questions on the menu.
Be smart about the questions and try to understand and grasp the user intent as they will not always be clear , they may ask for (price of burger) but not specify which one.
In such cases behave smartly and ouput something related from the menu.
If asked for the whole menu or too many things at once, explain to the user why you cannot answer that question.
The customer may ask for information on a category like (how many deals or how many pizza flavours), in such case you have access to the material , output according to the chunk you have.
The user may ask a question not knowing the exact wording in the menu, in such case behave intelligently and understand the user intent and output the closest you can get from the menu.
They may ask for groups in the menu (like the deals or traditional flavours), in suhc cases understand deals mean combo deals and tradtional means pizza flavours.
Only say that you dont have info if there really is nothing in the document about the query.
If the answer uses more than 1 chunk, you are allowed to use them.
If the answer is long, still output the complete answer regardless of the length.
Use ONLY THE PROVIDED INFORMATION, do not hallucinate. 
If you cannot find the answer in the documents, tell that to the customer directly and clearly.(however if it matches a little still give them the output)
Only accept questions in english/latin script.
If they are in this script but another language like roman urdu or hindi (e.g kese ho app , is cheez ki kya qeemat hai) , acceot and answer in the same style.
BEHAVE INTELLIGENTLY
context: {context}
"""
prompt = ChatPromptTemplate.from_messages([("system", system_prompt), ("human", query)])

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