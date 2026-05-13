import streamlit as st
import time

from data_manager import DataManager
from user_service import UserService
from expense_service import ExpenseService
from AI_Assistant import AIChatAssistant


st.set_page_config(
    "AI Expense Tracker",
    layout="wide",
    page_icon="💰",
    initial_sidebar_state="expanded"
)
##AI Assisted style addition for button color
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap');

html, body, [class*="css"]  {
    font-family: 'Poppins', sans-serif;
}
            
h1 {
    text-align: center;
}

h2, h3 {
    text-align: center;
}

.stApp {
    background-color: #faf7ff;
}

            
[data-testid="stSidebar"] {
    background-color: #b39ddb;
}

[data-testid="stSidebar"] * {
    color: #2c2c2c;
}

.stButton > button {
    background-color: #8e63ff;
    color: white;
    border-radius: 10px;
    border: none;
    padding: 8px 16px;
    font-weight: 600;
}

.stButton > button:hover {
    background-color: #7c4dff;
    color: white;}

div[data-testid="stVerticalBlockBorderWrapper"] {
    border: 2px solid #c5b3ff;
    border-radius: 12px;
    padding: 10px;
}

hr {
    border-top: 2px solid #333333;
}
html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
    font-size: 18px;
}
            
            .stButton > button {
    background-color: #8e63ff;
    color: white;
    border-radius: 10px;
    border: none;
    padding: 12px 22px;
    font-weight: 600;
    font-size: 18px;
}
            
            [data-testid="stMetricValue"] {
    font-size: 36px;
}


</style>
""", unsafe_allow_html=True)



data_manager = DataManager()
user_service = UserService(data_manager)
expense_service = ExpenseService(data_manager)
ai_assistant = AIChatAssistant()


if "page" not in st.session_state:
    st.session_state.page = "login"

if "user" not in st.session_state:
    st.session_state.user = None

if "edit_expense" not in st.session_state:
    st.session_state.edit_expense = None


login_guard = ["dashboard", "add_expense", "AI_Chat", "admin", "edit_expense"]

if st.session_state["page"] in login_guard and not st.session_state["user"]:
    st.warning("Please log in first")
    st.session_state["page"] = "login"
    st.rerun()


with st.sidebar:
    if st.session_state["user"]:
        st.success(f"Logged in as\n{st.session_state['user']['email']}")

        if st.button("Dashboard"):
            st.session_state["page"] = "dashboard"
            st.rerun()

        if st.button("Add Expense"):
            st.session_state["page"] = "add_expense"
            st.rerun()

        if st.button("AI Chat"):
            st.session_state["page"] = "AI_Chat"
            st.rerun()

        if st.session_state["user"]["role"].lower() == "admin":
            if st.button("Admin Features"):
                st.session_state["page"] = "admin"
                st.rerun()

        if st.button("Logout"):
            st.session_state["user"] = None
            st.session_state["page"] = "login"
            st.rerun()


if st.session_state["page"] == "login":
    st.title("Welcome to AI Expense Tracker")
    st.info("""
        Test Accounts

        Admin:
        Email: sofia@gmail.com
        Password: 12345

        User:
        Email: jdoe123@gmail.com
        Password: 98765
        """)
    st.subheader("Login")

    with st.container(border=True):
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login", type="primary"):
        with st.spinner("Logging in..."):
            time.sleep(1)

            found_user = user_service.login(email, password)

            if found_user:
                if found_user:
                    st.success(f"Welcome back, {found_user['email']}!")
                    time.sleep(2)
                    st.session_state["user"] = found_user
                    st.session_state["page"] = "dashboard"
                    st.rerun()
            else:
                st.error("Invalid credentials")

    st.subheader("Create New Account")

    with st.container(border=True):
        new_name = st.text_input("Full Name", key="register_name")
        new_email = st.text_input("Email", key="register_email")
        new_password = st.text_input("Password", type="password", key="register_password")
        new_role = st.radio("Role", options=["admin", "user"], horizontal=True)

        if st.button("Create Account", key="register_btn"):
            with st.spinner("Creating account..."):
                time.sleep(1)

                success, message = user_service.register_user(
                    new_name,
                    new_email,
                    new_password,
                    new_role
                )

                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)


elif st.session_state["page"] == "dashboard":
    st.title("💰 AI Expense Dashboard")
    st.divider()


    user_email = st.session_state.user["email"]
    user_expenses = expense_service.get_user_expenses(user_email)

    if len(user_expenses) == 0:
        st.info("No expenses yet. Add your first expense to get started.")
    else:
        total_spent, total_transactions, avg = expense_service.get_summary(user_email)

        with st.container(border=True):
            st.subheader("📋 Summary")

            col1, col2, col3 = st.columns(3)

            with col1:
                with st.container(border=True):
                    st.metric("Total Spent", f"${total_spent:.2f}")

            with col2:
                with st.container(border=True):
                    st.metric("Transactions", total_transactions)

            with col3:
                with st.container(border=True):
                    st.metric("Average Expense", f"${avg:.2f}")
        st.divider()

        category_amounts = expense_service.get_category_totals(user_email)
        highest, lowest = expense_service.get_highest_lowest(user_email)

        col1, col2 = st.columns([3,2])

        with col1:
            with st.container(border=True):
                st.subheader("Expenses by Category 📊")

                if category_amounts:
                    st.bar_chart(category_amounts)
                else:
                    st.info("No expenses yet")

        with col2:
            with st.container(border=True):
                st.subheader("📈 Highest and Lowest Expenses 📉")

                if highest and lowest:
                   col1, col2 = st.columns(2)

                with col1:
                    with st.container(border=True):
                        st.markdown(
                            f"""
                            <div style='text-align: center; padding: 10px;'>
                                <h3 style='font-size: 32px;'>Highest Expense 📈</h3>
                                <h1>${highest['amount']:.2f}</h1>
                                <p style='font-size: 24px;'>{highest["category"]}</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                with col2:
                    with st.container(border=True):
                        st.markdown(
                            f"""
                            <div style='text-align: center; padding: 10px;'>
                                <h3 style='font-size: 32px;'>Lowest Expense 📉</h3>
                                <h1>${lowest['amount']:.2f}</h1>
                                <p style='font-size: 24px;'>{lowest["category"]}</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
        st.divider()
        st.subheader("All Expenses 🧾")


##AI Assisted style addition for expense display
        for expense in user_expenses:
            with st.container(border=True):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown(
                        f"""
                        <div style='text-align: center; padding-top: 10px;'>
                            <h2>{expense['category']}</h2>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with col2:
                    st.markdown(
                        f"""
                        <div style='text-align: center;'>
                            <h4>Amount</h4>
                            <h2>${expense['amount']:.2f}</h2>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with col3:
                    st.markdown(
                        f"""
                        <div style='text-align: center;'>
                            <h4>Note</h4>
                            <p>{expense["note"] if expense["note"] else "No note added"}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

elif st.session_state["page"] == "add_expense":
    st.title("Add New Expense")
    st.subheader("New Expense Entry")
    st.divider()

    with st.container(border=True):
        amount = st.number_input("Amount", min_value=0.01)
        category = st.selectbox(
            "Category",
            options=["Food", "Transportation", "Bills", "Entertainment", "Other"]
        )
        note = st.text_area("Note (optional)")

        if st.button("Add Expense", key="add_expense_btn"):
            if amount <= 0:
                st.error("Amount must be greater than 0")
            else:
                with st.spinner("Adding expense..."):
                    time.sleep(1)

                    expense_service.add_expense(
                        st.session_state["user"]["email"],
                        amount,
                        category,
                        note
                    )

                st.success("Expense added!")
                time.sleep(2)
                st.rerun()


elif st.session_state["page"] == "AI_Chat":

    st.title("AI Spending Assistant")
    st.subheader("Ask questions about your expenses and spending habits.")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hi! I can help analyze your expenses and spending habits."
            }
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    user_input = st.chat_input("Ask about your expenses...")

    if user_input:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_input
            }
        )

        with st.chat_message("user"):
            st.write(user_input)

        user_email = st.session_state["user"]["email"]
        user_expenses = expense_service.get_user_expenses(user_email)

        response = ai_assistant.generate_response(user_input, user_expenses)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response
            }
        )

        with st.chat_message("assistant"):
            st.write(response)

elif st.session_state["page"] == "admin":
    if not st.session_state["user"] or st.session_state["user"]["role"].lower() != "admin":
        st.error("This is only accessible to admins")
        st.stop()
    st.title("Admin Dashboard 👩‍🏫")
    st.divider()

    users = user_service.users
    user_emails = [user["email"] for user in users]

    selected_user = st.selectbox("Select User", user_emails)

    if selected_user:
        user_expenses = expense_service.get_user_expenses(selected_user)

        st.subheader(f"{selected_user}'s Expenses")

        if len(user_expenses) == 0:
            st.info("This user has no expenses.")
        else:
            for expense in user_expenses:
                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns(4)

                    col1.write(f"Amount: ${expense['amount']:.2f}")
                    col2.write(f"Category: {expense['category']}")
                    col3.write(f"Note: {expense['note']}")
                    if col4.button("Delete", key=f"delete_{expense['id']}"):

                        with st.spinner("Deleting expense..."):
                            time.sleep(1)
                            expense_service.delete_expense(expense["id"])
                            st.success("Expense deleted!")
                            time.sleep(2)
                            st.rerun()
                    if col4.button("Edit", key=f"edit_{expense['id']}"):
                        st.session_state["edit_expense"] = expense
                        st.session_state["page"] = "edit_expense"
                        st.rerun()


elif st.session_state["page"] == "edit_expense":
    st.title("Edit Expense")

    if not st.session_state["user"] or st.session_state["user"]["role"].lower() != "admin":
        st.error("Admins only")
        st.stop()

    expense = st.session_state.edit_expense

    if expense is None:
        st.error("No expense selected")
        st.session_state["page"] = "admin"
        st.rerun()

    amount = st.number_input("Amount", value=float(expense["amount"]))
    category = st.selectbox(
        "Category",
        options=["Food", "Transportation", "Bills", "Entertainment", "Other"],
        index=["Food", "Transportation", "Bills", "Entertainment", "Other"].index(expense["category"])
    )
    note = st.text_area("Note (optional)", value=expense["note"])

    if st.button("Save Changes"):
        with st.spinner("Updating expense..."):
            time.sleep(1)
            expense_service.update_expense(
                expense["id"],
                amount,
                category,
                note
        )

        st.success("Expense updated")
        st.session_state["page"] = "admin"
        st.rerun()
