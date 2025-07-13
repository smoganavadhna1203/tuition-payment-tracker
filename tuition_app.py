import streamlit as st
import pandas as pd
from datetime import datetime
import os

DATA_FILE = "tuition_payments.csv"
st.set_page_config(page_title="Tuition & Chess Class Tracker", layout="centered")
st.title("📚 Tuition & Chess Class Payment Tracker")

tabs = st.tabs(["➕ Add Payment", "📋 View & Manage Payments"])

# ─────────────────────────────
# Tab 1: Add New Payment
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
# Tab 2: View / Edit / Delete
# ─────────────────────────────
with tabs[1]:
    st.subheader("📋 All Payment Records")

    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE, parse_dates=["Date Paid"])
        df["Month Paid"] = df["Date Paid"].dt.strftime("%B %Y")

        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            selected_student = st.selectbox("🔍 Filter by student", ["All"] + sorted(df["Student Name"].dropna().unique()))
        with col2:
            selected_class = st.selectbox("📘 Filter by class", ["All", "English", "Chess"])
        with col3:
            selected_month = st.selectbox("📅 Filter by month", ["All"] + sorted(df["Month Paid"].dropna().unique()))

        filtered_df = df.copy()
        if selected_student != "All":
            filtered_df = filtered_df[filtered_df["Student Name"] == selected_student]
        if selected_class != "All":
            filtered_df = filtered_df[filtered_df["Class Type"] == selected_class]
        if selected_month != "All":
            filtered_df = filtered_df[filtered_df["Month Paid"] == selected_month]

        filtered_df_display = filtered_df.drop(columns=["Month Paid"])
        st.dataframe(filtered_df_display.reset_index(drop=True), use_container_width=True)

        st.markdown("---")

        st.subheader("✏️ Edit or ❌ Delete a Record")
        editable_df = df.reset_index()  # keep index to track original row

        options = [f'{row["index"]}: {row["Student Name"]} - {row["Class Type"]} - {row["Date Paid"].strftime("%Y-%m-%d")}'
                   for _, row in editable_df.iterrows()]
        selected = st.selectbox("Select a record to edit/delete", ["None"] + options)

        if selected != "None":
            selected_index = int(selected.split(":")[0])
            selected_row = df.loc[selected_index]

            with st.form("edit_form"):
                new_name = st.text_input("👤 Student Name", selected_row["Student Name"])
                new_class = st.selectbox("📘 Class Type", ["English", "Chess"], index=["English", "Chess"].index(selected_row["Class Type"]))
                new_amount = st.number_input("💰 Payment Amount (RM)", value=float(selected_row["Amount (RM)"]), format="%.2f")
                new_date = st.date_input("📅 Date Paid", value=selected_row["Date Paid"])
                new_notes = st.text_area("📝 Notes", value=selected_row["Notes"])
                col_edit, col_delete = st.columns(2)

                with col_edit:
                    update_btn = st.form_submit_button("✅ Update Record")
                with col_delete:
                    delete_btn = st.form_submit_button("❌ Delete Record")

            if update_btn:
                df.at[selected_index, "Student Name"] = new_name
                df.at[selected_index, "Class Type"] = new_class
                df.at[selected_index, "Amount (RM)"] = new_amount
                df.at[selected_index, "Date Paid"] = new_date.strftime("%Y-%m-%d")
                df.at[selected_index, "Notes"] = new_notes
                df.to_csv(DATA_FILE, index=False)
                st.success("✅ Record updated successfully.")

            if delete_btn:
                df = df.drop(index=selected_index).reset_index(drop=True)
                df.to_csv(DATA_FILE, index=False)
                st.warning("🗑️ Record deleted.")
    else:
        st.info("No payment records yet.")
