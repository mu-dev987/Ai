# IMPORTING

import os
import re
import streamlit as st
from Agent import agent


# HEADING

st.title(":red[CRAVING CRUST] :pizza:")

# QUESTION

query = st.text_area("", placeholder="How can I assist you with the menu ?")

#  EXECUTION AND RESPONSE

response_area = st.empty()

if st.button("ASK"):

    # EMPTY PROMPT CHECK

    if len(query.strip()) <= 0:
        st.write("NO QUESTION ASKED")
    else:

        # THINKING SPINNER

        with st.spinner("Thinking..."):
            config = {"configurable": {"thread_id": st.session_state["store_thread_id"]}}

            # ERROR HANDLING

            result = agent.invoke({"messages": [{"role": "user", "content": query}]}, config=config)
            reply = result["messages"][-1].text
            response_area.write(reply)
            
 

        # INVOICE CHECKING & GENERATION

            receipt_file = None
            try:
                for msg in result["messages"]:
                    if getattr(msg, "name", None) == "order":
                        match = re.search(r"Invoice generated as (\S+)", msg.content)
                        if match:
                            receipt_file = match.group(1)

                        if os.path.exists(receipt_file):
                            with open(receipt_file, "rb") as pdf_file:
                                st.download_button(
                                    label="📄 Download Your Receipt (PDF)",
                                    data=pdf_file,
                                    file_name=f"craving_crust_{receipt_file}",
                                    mime="application/pdf",
                                )
            except Exception as e:
                print(e)