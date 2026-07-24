# IMPORTING

import os
import uuid
import re
import streamlit as st
from Agent import agent


# HEADING

st.title(":red[CRAVING CRUST] :pizza:")

# MEMORY HANDLING

if "store_thread_id" not in st.session_state:
    st.session_state["store_thread_id"] = str(uuid.uuid4())
receipt_file = None

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

        with st.spinner("Processing..."):
            config = {"configurable": {"thread_id": st.session_state["store_thread_id"]}}

            # EXECUTION
            
            try:
                result = agent.invoke({"messages": [{"role": "user", "content": query}]}, config=config)
                reply = result["messages"][-1].text
                response_area.write(reply)
            except Exception as e:
                if "429" in str(e):
                    print(str(e))
                    st.error("AW SNAP! Our AI Tokens are Finished :(")
                else:
                    print(str(e))
                    st.error("We are encountering a technical issue, please try later")
 

        # INVOICE CHECKING & GENERATION

            receipt_file = None
            bill_no_shown = False
            try:
                for msg in result["messages"]:
                    if getattr(msg, "name", None) == "order":
                        match = re.search(r"Invoice generated as (\S+)", msg.content)
                        if match:
                            receipt_file = match.group(1)
                            bill_no_match = re.search(r"receipt_(\d+)\.pdf", receipt_file)
                            if bill_no_match:
                                bill_no_shown = bill_no_match.group(1)
            except Exception as e:
                        print(str(e))

            if bill_no_shown:
                        st.success(f"✅ Your order was placed. Bill No: {bill_no_shown}")

            if receipt_file:
                try:
                    if os.path.exists(receipt_file):
                        with open(receipt_file, "rb") as pdf_file:
                            st.download_button(
                                        label="📄 Download Your Receipt (PDF)",
                                        data=pdf_file,
                                        file_name=f"craving_crust_{receipt_file}",
                                        mime="application/pdf",
                                    )
                    else:
                        st.warning("Your order was saved, but the receipt file couldn't be found. Please note your bill number above.")
                except Exception as e:
                    print(str(e))
                    st.warning("Your order was saved, but there was an issue preparing your receipt for download. Please note your bill number above.")