from datetime import date
import math
import os

from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from chatbot import finance_chatbot
from database import TRANSACTION_CATEGORIES, create_database

app = Flask(__name__)
create_database()


def get_db_connection():
    connection = sqlite3.connect("finance.db")
    connection.row_factory = sqlite3.Row
    return connection


@app.route("/")
def home():
    connection = get_db_connection()

    transactions = connection.execute(
        "SELECT * FROM transactions ORDER BY id DESC"
    ).fetchall()

    connection.close()

    total_income = sum(
        t["amount"] for t in transactions
        if t["transaction_type"] == "Income"
    )

    total_expenses = sum(
        t["amount"] for t in transactions
        if t["transaction_type"] == "Expense"
    )

    expense_by_category = {category: 0 for category in TRANSACTION_CATEGORIES}
    for transaction in transactions:
        if transaction["transaction_type"] == "Expense":
            category = transaction["category"] or "Other"
            if category not in expense_by_category:
                category = "Other"
            expense_by_category[category] += transaction["amount"]

    balance = total_income - total_expenses
    return render_template(
        "dashboard.html",
        transactions=transactions,
        total_income=total_income,
        total_expenses=total_expenses,
        balance=balance,
        categories=TRANSACTION_CATEGORIES,
        today=date.today().isoformat(),
        income_expense_chart={
            "labels": ["Income", "Expenses"],
            "values": [total_income, total_expenses],
        },
        expense_category_chart={
            "labels": list(expense_by_category),
            "values": list(expense_by_category.values()),
        },
        error_message=request.args.get("error"),
    )


@app.route("/add", methods=["POST"])
def add_transaction():

    description = request.form.get("description", "").strip()
    try:
        amount = float(request.form.get("amount", ""))
    except ValueError:
        amount = 0

    if not description:
        return redirect(url_for("home", error="Enter a transaction description."))
    if not math.isfinite(amount) or amount <= 0:
        return redirect(url_for("home", error="Enter an amount greater than zero."))

    transaction_type = request.form.get("transaction_type", "")
    if transaction_type not in {"Income", "Expense"}:
        return redirect(url_for("home", error="Choose a valid transaction type."))

    category = request.form.get("category", "Other")
    if category not in TRANSACTION_CATEGORIES:
        category = "Other"

    transaction_date = request.form.get("date", "").strip()
    try:
        transaction_date = date.fromisoformat(transaction_date).isoformat()
    except ValueError:
        return redirect(url_for("home", error="Choose a valid transaction date."))

    connection = get_db_connection()

    connection.execute(
        """
        INSERT INTO transactions
        (description, amount, transaction_type, category, date)
        VALUES (?, ?, ?, ?, ?)
        """,
        (description, amount, transaction_type, category, transaction_date)
    )

    connection.commit()
    connection.close()

    return redirect("/")
@app.route("/delete/<int:transaction_id>")
def delete_transaction(transaction_id):

    connection = get_db_connection()

    connection.execute(
        "DELETE FROM transactions WHERE id = ?",
        (transaction_id,)
    )

    connection.commit()
    connection.close()

    return redirect("/")
@app.route("/chat", methods=["GET", "POST"])
def chat():
    user_message = ""
    assistant_response = "Hello! Ask me about your income, expenses, balance, recent transactions, or saving."

    if request.method == "POST":
        user_message = request.form.get("message", "").strip()
        connection = get_db_connection()
        try:
            transactions = connection.execute(
                "SELECT * FROM transactions ORDER BY id DESC"
            ).fetchall()
        finally:
            connection.close()
        assistant_response = finance_chatbot(user_message, transactions)

    return render_template(
        "chat.html",
        user_message=user_message,
        assistant_response=assistant_response,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))