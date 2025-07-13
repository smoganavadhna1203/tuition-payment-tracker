import streamlit as st
import pandas as pd
from datetime import datetime
import os

# File to store data
DATA_FILE = "tuition_payments.csv"

# Set page config
st.set_page_config(page_title="Tuition & Chess Class Tracker", layout="centered")

# App title
st.title("📚 Tuition & Chess Class Payment Tracker")

# Tabs: Data Entry | Payment History
tabs = st.tabs(["➕ Add Payment", "📋 View Payments"])

# ─────────────────────────────
# Tab 1: Form to Add Payment
# ─────────────────────────────
with tabs[0]:
    with st.form("payment_form"):
        name = st.text_input("👤 Student Name")
        class_type = st.selectbox("📘 Class Type", ["English", "Chess"])
        amount = st.number_input("💰 Payment Amount (RM)", min_value=0.0, format="%.2f")
        date_paid = st.date_input("📅 Date Paid", value=datetime.today())
        notes = st.text_area("📝 Notes", height=100)

        submitted = st.form_submit_button("💾 Save Payment")

    if submitted:
        new_data = pd.DataFrame([{
            "Date Paid": date_paid.strftime("%Y-%m-%d"),
            "Student Name": name.strip(),
            "Class Type": class_type,
            "Amount (RM)": amount,
            "Notes": notes.strip()
        }])

        if os.path.exists(DATA_FILE):
            existing_data = pd.read_csv(DATA_FILE)
            combined = pd.concat([existing_data, new_data], ignore_index=True)
        else:
            combined = new_data

        combined.to_csv(DATA_FILE, index=False)
        st.success(f"✅ Payment saved for {name}")

# ─────────────────────────────
# Tab 2: Payment History Viewer
# ─────────────────────────────
with tabs[1]:
    st.subheader("📋 All Payment Records")

    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)

        # Filters
        col1, col2 = st.columns(2)
        with col1:
            selected_student = st.selectbox("Filter by student", ["All"] + sorted(df["Student Name"].unique().tolist()))
        with col2:
            selected_class = st.selectbox("Filter by class type", ["All", "English", "Chess"])

        # Apply filters
        filtered_df = df.copy()
        if selected_student != "All":
            filtered_df = filtered_df[filtered_df["Student Name"] == selected_student]
        if selected_class != "All":
            filtered_df = filtered_df[filtered_df["Class Type"] == selected_class]

        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.info("No payment records found yet.")
