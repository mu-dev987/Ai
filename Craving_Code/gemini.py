import os 
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import streamlit as st
os.environ['GEMINI_API_KEY'] = st.secrets["YOUR_API_KEY"]
output_cleaner = StrOutputParser()
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)
# translation_prompt = ChatPromptTemplate.from_messages([
#     ("system","You are a urdu-english expert. You are to take any line written in english and output the urdu trnaslation in the same script as english "),
#     ("human","{text}")
# ])
answer_prompt = ChatPromptTemplate.from_messages([
    ("system","you are to take into account the text and produce an appropiate response in the urdu language with the english script. Make sure that the response is only in the english script. Make the response adequately matching the prompt of the user and try to be precise in giving the answer. if it is a logical or memory question be precise and dont hallucinate , but if its another type of question you are allowd to be creative, but do not go away from the actual prommpt"),
    ("human","{text}")
])
# translation_prompt | llm | output_cleaner | {"text": lambda x: x} | 
chain = answer_prompt | llm | output_cleaner
st.title(":red[Urdu AI Assistant]")
input = st.text_area("",placeholder="What can I asssit you with today?")
response_area = st.empty()
if st.button("ANSWER"):
    response_area = st.empty()
    if len(input.strip()) <= 0:
        response_area.write("WRITE SOMETHING!")
    else:
        with st.spinner("Thinking..."): 
            try:
                response = chain.invoke(input)
                response_area.write(response)
            except Exception as e:
                if "429" in str(e):
                    st.error( "AW SNAP! our Ai tokens are finished :(")
                else:    
                    st.error(f"OOPS! something went wrong {type(e).__name__}")
else:
    response_area.write("")