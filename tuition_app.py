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

# ─────────────────────────────
# Tab 3: Manage Students
# ─────────────────────────────
with tabs[2]:
    st.subheader("👩‍🎓 Add or View Students")

    with st.form("student_form"):
        student_name = st.text_input("👤 Student Name")
        class_type = st.selectbox("📘 Class Type", ["English", "Chess"])
        group = st.text_input("🏷️ Group (e.g., Year 1, Group A, etc.)")
        submit_student = st.form_submit_button("➕ Add Student")

    if submit_student:
        if student_name and group:
            new_student = pd.DataFrame([{
                "Student Name": student_name.strip(),
                "Class Type": class_type,
                "Group": group.strip()
            }])

            if os.path.exists(STUDENT_FILE):
                df_students = pd.read_csv(STUDENT_FILE)
                df_students = pd.concat([df_students, new_student], ignore_index=True)
            else:
                df_students = new_student

            df_students.to_csv(STUDENT_FILE, index=False)
            st.success(f"✅ {student_name} added to {class_type} - {group}")
        else:
            st.warning("⚠️ Please fill in both student name and group.")

    # Display Student Table with Filters
    st.markdown("### 📋 Registered Students")

    if os.path.exists(STUDENT_FILE):
        df_students = pd.read_csv(STUDENT_FILE)

        if not df_students.empty:
            class_filter = st.selectbox("📘 Filter by Class Type", ["All"] + sorted(df_students["Class Type"].unique()))
            group_filter = st.selectbox("🏷️ Filter by Group", ["All"] + sorted(df_students["Group"].unique()))

            filtered_df = df_students.copy()
            if class_filter != "All":
                filtered_df = filtered_df[filtered_df["Class Type"] == class_filter]
            if group_filter != "All":
                filtered_df = filtered_df[filtered_df["Group"] == group_filter]

            st.dataframe(filtered_df.reset_index(drop=True), use_container_width=True)
        else:
            st.info("No students registered yet.")
    else:
        st.info("No students.csv file found. Please add a student first.")

    # Edit/Delete student
    st.markdown("### ✏️ Edit / ❌ Delete a Student")
    if os.path.exists(STUDENT_FILE):
        df_students = pd.read_csv(STUDENT_FILE)
        if len(df_students) > 0:
            student_to_edit = st.selectbox(
                "Select a student to edit/delete",
                ["None"] + df_students["Student Name"].tolist()
            )

            if student_to_edit != "None":
                student_row = df_students[df_students["Student Name"] == student_to_edit].iloc[0]
                with st.form("edit_student_form"):
                    new_name = st.text_input("👤 New Name", student_row["Student Name"])
                    new_class = st.selectbox("📘 Class Type", ["English", "Chess"], index=["English", "Chess"].index(student_row["Class Type"]))
                    new_group = st.text_input("🏷️ Group", student_row["Group"])

                    col1, col2 = st.columns(2)
                    update = col1.form_submit_button("✅ Update")
                    delete = col2.form_submit_button("🗑️ Delete")

                if update:
                    df_students.loc[df_students["Student Name"] == student_to_edit, ["Student Name", "Class Type", "Group"]] = [new_name.strip(), new_class, new_group.strip()]
                    df_students.to_csv(STUDENT_FILE, index=False)
                    st.success("✅ Student updated successfully.")
                if delete:
                    df_students = df_students[df_students["Student Name"] != student_to_edit]
                    df_students.to_csv(STUDENT_FILE, index=False)
                    st.warning("🗑️ Student deleted.")

# ─────────────────────────────
# Tab 1: Add Payment
# ─────────────────────────────
with tabs[0]:
    st.subheader("➕ Add Payment Record")

    if os.path.exists(STUDENT_FILE):
        df_students = pd.read_csv(STUDENT_FILE)
        class_type = st.selectbox("📘 Select Class Type", ["English", "Chess"])
        filtered_students = df_students[df_students["Class Type"] == class_type]
        student_options = filtered_students["Student Name"].tolist()

        if student_options:
            selected_student = st.selectbox("👤 Select Student", student_options)
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
            st.warning("⚠️ No students found in this class. Please add in 'Manage Students'.")
    else:
        st.warning("⚠️ Please register students first in 'Manage Students' tab.")

# ─────────────────────────────
# Tab 2: View & Manage Payments
# ─────────────────────────────
with tabs[1]:
    st.subheader("📋 All Payment Records")

    if os.path.exists(PAYMENT_FILE):
        df = pd.read_csv(PAYMENT_FILE, parse_dates=["Date Paid"])
        df["Month Paid"] = df["Date Paid"].dt.strftime("%B %Y")

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

        # Edit/Delete payment
        st.markdown("### ✏️ Edit / ❌ Delete a Payment")
        if len(df) > 0:
            payment_to_edit = st.selectbox(
                "Select a payment to edit/delete",
                ["None"] + df.index.astype(str).tolist()
            )

            if payment_to_edit != "None":
                idx = int(payment_to_edit)
                row = df.loc[idx]

                with st.form("edit_payment_form"):
                    new_name = st.text_input("👤 Student Name", row["Student Name"])
                    new_class = st.selectbox("📘 Class Type", ["English", "Chess"], index=["English", "Chess"].index(row["Class Type"]))
                    new_group = st.text_input("🏷️ Group", row["Group"])
                    new_amount = st.number_input("💰 Amount (RM)", value=float(row["Amount (RM)"]), format="%.2f")
                    new_date = st.date_input("📅 Date Paid", value=row["Date Paid"])
                    new_notes = st.text_area("📝 Notes", value=row["Notes"])
                    c1, c2 = st.columns(2)
                    update_btn = c1.form_submit_button("✅ Update")
                    delete_btn = c2.form_submit_button("🗑️ Delete")

                if update_btn:
                    df.at[idx, "Student Name"] = new_name.strip()
                    df.at[idx, "Class Type"] = new_class
                    df.at[idx, "Group"] = new_group.strip()
                    df.at[idx, "Amount (RM)"] = new_amount
                    df.at[idx, "Date Paid"] = new_date.strftime("%Y-%m-%d")
                    df.at[idx, "Notes"] = new_notes.strip()
                    df.to_csv(PAYMENT_FILE, index=False)
                    st.success("✅ Payment updated.")
                if delete_btn:
                    df = df.drop(index=idx).reset_index(drop=True)
                    df.to_csv(PAYMENT_FILE, index=False)
                    st.warning("🗑️ Payment deleted.")
    else:
        st.info("No payment records found yet.")
