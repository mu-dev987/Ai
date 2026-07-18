# IMPORTING

import os
from langchain.tools import tool
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from fpdf import FPDF
import random
from datetime import datetime
import streamlit as st
from typing import List, Dict
from RAG import chain

# PDF CLASS

class ThermalReceipt(FPDF):

    def __init__(self):

        # 80mm width is the standard size for thermal receipt rolls

        super().__init__(orientation='P', unit='mm', format=(80, 180))
        self.set_margins(5, 5, 5)
        self.set_auto_page_break(auto=True, margin=5)

    def draw_divider(self):
        self.ln(1)
        self.set_font("Arial", "", 10)

        # Replicating the exact receipt divider style from the image

        self.cell(
            0, 3, "--------------------------------------------------------", ln=True, align="C"
        )
        self.ln(1)

# AI SETUP

os.environ["GEMINI_API_KEY"] = st.secrets["BACKUP_API_KEY"]

# CHATBOT TOOL

@tool
def menu_assistant(query: str) -> str:
    
    """USE THIS TOOL FIRST for any general questions, menu browsing, checking prices, 
    asking about ingredients, or casual conversation. If the user is not explicitly 
    ready to buy or checkout, use this tool."""


    try:
        response = chain.invoke(query)
        return response
    except Exception as e:
        if "429" in str(e):
            return "ERROR: Our AI engine token quota is temporarily exhausted."
        else:
            return f"ERROR: Something went wrong: {type(e).__name__}"

# INVOICE TOOL

@tool
def order(
    customer_name: str,
    order_type: str,
    payment_method: str,
    items_list: List[Dict],
    delivery_address: str = "N/A"
):
    """Call this tool when the user has confirmed their order to be placed.

    Args:
        customer_name: The name of the customer ordering.
        order_type: Must be either 'Delivery' or 'Takeaway'.
        payment_method: How they are paying (e.g., 'Cash', 'Visa', 'EasyPaisa','JazzCash','NayaPay') any other method not acceptable.
        delivery_address: The customer's full address if order_type is 'Delivery'.
        items_list: A list of dictionaries containing the items ordered.
                    Format: [{"name": "item_name", "qty": 2, "price": 950.00}]"""
    """
    ONLY call this tool when the customer has explicitly stated they want to place, 
    finalize, or complete an actual order/purchase (e.g., 'I want to order this now', 
    'Checkout my basket', 'Confirm my delivery'). 
    
    DO NOT use this tool if the user is just asking about items, prices, or menu options.
    
    items_list must be a list of dicts where each dict has 'name', 'qty', and 'price'.
    critical: if the user says "where is my invoice" use this tool to give the invoice
    """
    
    # RESTAURANT INFO HARDCODING

    restaurant_name = "CRAVING CRUST"
    restaurant_address = "Main Bostan Colony near mordern public high school"
    contact_number = "0326-446414"
    website_name = "cravingcrust.streamlit.app"

    # USER, EXTRA INFO DYNAMIC CODING

    date_of_order = datetime.now().strftime("%d/%m/%Y")
    time_of_order = datetime.now().strftime("%I:%M:%S %p")
    bill_no = f"{random.randint(0, 999999):06d}"
    unique_filename = f"receipt_{bill_no}.pdf"
    order_items = items_list if items_list else []
    subtotal = sum(item["qty"] * item["price"] for item in order_items)
    delivery_fee = 5.00 if order_type.lower() == "delivery" else 0.00
    total_amount = subtotal + delivery_fee

    # PDF LOGIC

    pdf = ThermalReceipt()
    pdf.add_page()

    # 1. Header Section (Restaurant Details)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 6, restaurant_name, ln=True, align="C")
    pdf.ln(2)

    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 4, restaurant_address, ln=True, align="C")
    pdf.cell(0, 4, f"Phone: {contact_number}", ln=True, align="C")
    pdf.cell(0, 4, website_name, ln=True, align="C")
    pdf.cell(0, 4, f"{date_of_order} at {time_of_order}", ln=True, align="C")
    pdf.cell(0, 4, f"Bill No. {bill_no}", ln=True, align="C")

    pdf.draw_divider()

    # 2. Customer & Logistics Section

    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 4, f"CUSTOMER: {customer_name.upper()}", ln=True)
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 4, f"ORDER TYPE: {order_type.upper()}", ln=True)
    pdf.cell(0, 4, f"PAYMENT: {payment_method}", ln=True)
    if (
        order_type.lower() == "delivery"
    ):  # MultiCell ensures long addresses wrap nicely within the narrow receipt width
        pdf.multi_cell(0, 4, f"DELIVERY ADDR: {delivery_address}")

    pdf.draw_divider()

    # 3. Items Table Header

    pdf.set_font("Arial", "B", 9)
    pdf.cell(10, 5, "QTY", align="L")
    pdf.cell(40, 5, "ITEM", align="L")
    pdf.cell(20, 5, "PRICE", align="R", ln=True)
    pdf.ln(1)

    # 4. Items Table Rows

    pdf.set_font("Arial", "", 9)
    for item in order_items:
        pdf.cell(10, 5, str(item["qty"]), align="L")
        pdf.cell(40, 5, item["name"], align="L")
        pdf.cell(20, 5, f"Rs. {item['price']:.2f}", align="R", ln=True)

    pdf.draw_divider()

    # 5. Financial Summary Block

    pdf.cell(45, 5, "SUBTOTAL", align="L")
    pdf.cell(25, 5, f"Rs. {subtotal:.2f}", align="R", ln=True)

    if order_type.lower() == "delivery":
        pdf.cell(45, 5, "DELIVERY FEE", align="L")
        pdf.cell(25, 5, f"Rs. {delivery_fee:.2f}", align="R", ln=True)

    pdf.draw_divider()

    # 6. Grand Total

    pdf.set_font("Arial", "B", 11)
    pdf.cell(45, 6, "=TOTAL:", align="L")
    pdf.cell(25, 6, f"Rs. {total_amount:.2f}", align="R", ln=True)
    pdf.ln(5)

    # 7. Footer Greeting

    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 4, "THANK YOU FOR EATING WITH US!", ln=True, align="C")
    pdf.cell(0, 4, "PLEASE COME AGAIN", ln=True, align="C")

    # OUTPUT FILE

    pdf.output(unique_filename)

    # RETURN SUCCESS

    return f"Invoice generated as {unique_filename}"

# AGENT CREATION

memory = InMemorySaver()
tools = [menu_assistant, order]
agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    tools=tools,
    checkpointer=memory,
    system_prompt=(
        "You are a polite AI assistant for the restaurant Craving Crust in Lahore. "
        "CRITICAL RULE: Customers will talk about food items all the time. Do NOT use the 'order' tool "
        "unless they explicitly say they are ready to place a final order or checkout. For all questions "
        "about what's on the menu, prices, flavors, or deals, always use the 'menu_assistant' tool instead."
        "Always use the latin script. No other script is allowed. urdu latin(e.g kia haal h) is allowed."
    )
)