import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Page settings
st.set_page_config(page_title="Tuition Payment Tracker", layout="centered")

st.title("📚 Tuition & Chess Class Payment Tracker")

# Form UI
with st.form("payment_form"):
    name = st.text_input("👤 Student Name")
    class_type = st.selectbox("📘 Class Type", ["English", "Chess"])
    amount = st.number_input("💰 Payment Amount (RM)", min_value=0.0, format="%.2f")
    date_paid = st.date_input("📅 Date Paid", value=datetime.today())
    notes = st.text_area("📝 Notes", height=100)

    submitted = st.form_submit_button("Save Payment")

# Save to Excel
if submitted:
    new_data = {
        "Date Paid": [date_paid.strftime("%Y-%m-%d")],
        "Student Name": [name],
        "Class Type": [class_type],
        "Amount (RM)": [amount],
        "Notes": [notes]
    }

    df_new = pd.DataFrame(new_data)

    file_path = "tuition_payments.xlsx"

    if os.path.exists(file_path):
        df_existing = pd.read_excel(file_path)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new

    df_combined.to_excel(file_path, index=False)

    st.success(f"✅ Payment saved for {name}")
