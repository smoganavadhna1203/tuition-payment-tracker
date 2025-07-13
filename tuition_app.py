import streamlit as st
import pandas as pd
from datetime import datetime
import os

# File paths
STUDENT_FILE = "students.csv"
PAYMENT_FILE = "tuition_payments.csv"

st.set_page_config(page_title="Tuition & Chess Class Tracker", layout="centered")
st.title("📚 Tuition & Chess Class Payment Tracker")

tabs = st.tabs(["➕ Add Payment", "📋 View & Manage Payments", "👩‍🎓 Manage Students"])

# ─────────────────────────────────────
# Tab 3: Manage Students
# ─────────────────────────────────────
with tabs[2]:
    st.subheader("👩‍🎓 Add or View Students")

    with st.form("student_form"):
        student_name = st.text_input("👤 Student Name")
        class_type = st.selectbox("📘 Class Type", ["English", "Chess"])
        
        # Group options based on class
        if class_type == "English":
            group = st.selectbox("🏷️ Group (Standard)", ["Year 1", "Year 2", "Year 3", "Form 1", "Form 2", "Form 3"])
        else:
            group = st.selectbox("🏷️ Group", ["Group A", "Group B"])
        
        submit_student = st.form_submit_button("➕ Add Student")

    if submit_student:
        new_student = pd.DataFrame([{
            "Student Name": student_name.strip(),
            "Class Type": class_type,
            "Group": group
        }])

        if os.path.exists(STUDENT_FILE):
            df_students = pd.read_csv(STUDENT_FILE)
            df_students = pd.concat([df_students, new_student], ignore_index=True)
        else:
            df_students = new_student

        df_students.to_csv(STUDENT_FILE, index=False)
        st.success(f"✅ {student_name} added to {class_type} - {group}")

    # View existing students
    if os.path.exists(STUDENT_FILE):
        df_students = pd.read_csv(STUDENT_FILE)
        st.markdown("### 📋 Registered Students")
        st.dataframe(df_students, use_container_width=True)
    else:
        st.info("No students registered yet.")

# ─────────────────────────────────────
# Tab 1: Add Payment
# ─────────────────────────────────────
with tabs[0]:
    st.subheader("➕ Add Payment Record")

    if os.path.exists(STUDENT_FILE):
        df_students = pd.read_csv(STUDENT_FILE)

        # Select class first
        class_type = st.selectbox("📘 Select Class Type", ["English", "Chess"])
        filtered_students = df_students[df_students["Class Type"] == class_type]
        
        student_options = filtered_students["Student Name"].tolist()
        selected_student = st.selectbox("👤 Select Student", student_options)

        # Auto-fill group
        student_group = filtered_students.loc[filtered_students["Student Name"] == selected_student, "Group"].values[0]
        st.text_input("🏷️ Group", value=student_group, disabled=True)

        amount = st.number_input("💰 Payment Amount (RM)", min_value=0.0, format="%.2f")
        date_paid = st.date_input("📅 Date Paid", value=datetime.today())
        notes = st.text_area("📝 Notes", height=100)
        submitted = st.button("💾 Save Payment")

        if submitted:
            new_payment = pd.DataFrame([{
                "Date Paid": date_paid.strftime("%Y-%m-%d"),
                "Student Name": selected_student,
                "Class Type": class_type,
                "Group": student_group,
                "Amount (RM)": amount,
                "Notes": notes.strip()
            }])

            if os.path.exists(PAYMENT_FILE):
                existing = pd.read_csv(PAYMENT_FILE)
                all_data = pd.concat([existing, new_payment], ignore_index=True)
            else:
                all_data = new_payment

            all_data.to_csv(PAYMENT_FILE, index=False)
            st.success(f"✅ Payment saved for {selected_student}")
    else:
        st.warning("⚠️ Please register students first in 'Manage Students' tab.")

# ─────────────────────────────────────
# Tab 2: View Payments (w/ Filters)
# ─────────────────────────────────────
with tabs[1]:
    st.subheader("📋 All Payment Records")

    if os.path.exists(PAYMENT_FILE):
        df = pd.read_csv(PAYMENT_FILE, parse_dates=["Date Paid"])
        df["Month Paid"] = df["Date Paid"].dt.strftime("%B %Y")

        # Filters
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            selected_student = st.selectbox("Student", ["All"] + sorted(df["Student Name"].dropna().unique()))
        with col2:
            selected_class = st.selectbox("Class", ["All", "English", "Chess"])
        with col3:
            selected_group = st.selectbox("Group", ["All"] + sorted(df["Group"].dropna().unique()))
        with col4:
            selected_month = st.selectbox("Month", ["All"] + sorted(df["Month Paid"].dropna().unique()))

        filtered = df.copy()
        if selected_student != "All":
            filtered = filtered[filtered["Student Name"] == selected_student]
        if selected_class != "All":
            filtered = filtered[filtered["Class Type"] == selected_class]
        if selected_group != "All":
            filtered = filtered[filtered["Group"] == selected_group]
        if selected_month != "All":
            filtered = filtered[filtered["Month Paid"] == selected_month]

        st.dataframe(filtered.drop(columns=["Month Paid"]).reset_index(drop=True), use_container_width=True)
    else:
        st.info("No payment records found yet.")
