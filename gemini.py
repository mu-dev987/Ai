import os 
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate 
from langchain_core.output_parsers import StrOutputParser
import streamlit as st
os.environ['GEMINI_API_KEY'] = st.secrets["MY_API_KEY"]
output_cleaner = StrOutputParser()
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)
translation_prompt = ChatPromptTemplate.from_messages([
    ("system","You are a urdu-english expert. You are to take any line written in english and output the urdu trnaslation in the same script as english "),
    ("human","{text}")
])
answer_prompt = ChatPromptTemplate.from_messages([
    ("system","you are to take into account the text and produce an appropiate response in the urdu language with the english script. Make sure that the response is only in the english script."),
    ("human","{text}")
])
chain = translation_prompt | llm | output_cleaner | {"text": lambda x: x} | answer_prompt | llm | output_cleaner
st.title(":red[Urdu AI Assistant]")
input = st.text_area("",placeholder="What can I asssit you with today @fasih.y331 ?")
if st.button("ANSWER"):
    if input == "":
        st.write("WRITE SOMETHING!")
    else:
        with st.spinner("Processing your request..."):
            try:
                response = chain.invoke(input)
                st.write(response)
            except Exception as e:
                if "429" in str(e):
                    st.error( "AW SNAP! our Ai tokens are finished :(")
                else:    
                    st.error(f"OOPS! something went wrong {type(e).__name__}")
        
else:
    st.write("")