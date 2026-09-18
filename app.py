from flask import Flask, request, redirect
import sqlite3
from chatbot import finance_chatbot

app = Flask(__name__)


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

    balance = total_income - total_expenses

    transaction_rows = ""

    for t in transactions:
        transaction_rows += f"""
<tr>
    <td>{t["description"]}</td>
    <td>₹{t["amount"]:.2f}</td>
    <td>{t["transaction_type"]}</td>
    <td>
        <a href="/delete/{t['id']}">
            Delete
        </a>
    </td>
</tr>
"""

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Finance Assistant</title>

        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f0f4f8;
                margin: 0;
            }}

            header {{
                background: #172554;
                color: white;
                padding: 25px;
                text-align: center;
            }}

            .container {{
                width: 90%;
                max-width: 1000px;
                margin: 30px auto;
            }}

            .cards {{
                display: flex;
                gap: 20px;
                flex-wrap: wrap;
            }}

            .card {{
                background: white;
                padding: 25px;
                border-radius: 12px;
                flex: 1;
                min-width: 200px;
                box-shadow: 0 4px 10px #00000015;
            }}

            .card p {{
                font-size: 28px;
                font-weight: bold;
                color: #172554;
            }}

            .form-box, .table-box {{
                background: white;
                padding: 25px;
                border-radius: 12px;
                margin-top: 25px;
            }}

            input, select, button {{
                padding: 12px;
                margin: 5px;
                border-radius: 6px;
                border: 1px solid #ccc;
            }}

            button {{
                background: #2563eb;
                color: white;
                cursor: pointer;
            }}
            .chat-button {{
    display: inline-block;
    padding: 12px 18px;
    background: #16a34a;
    color: white;
    text-decoration: none;
    border-radius: 6px;
    margin-top: 10px;
}}

            table {{
                width: 100%;
                border-collapse: collapse;
            }}

            th, td {{
                padding: 12px;
                border-bottom: 1px solid #ddd;
                text-align: left;
            }}
        </style>
    </head>

    <body>

        <header>
    <h1>AI Finance Assistant</h1>
    <p>Manage your money smarter</p>
    <a href="/chat" class="chat-button">Open AI Chatbot</a>
</header>
        <div class="container">

            <div class="cards">

                <div class="card">
                    <h3>Total Income</h3>
                    <p>₹{total_income:.2f}</p>
                </div>

                <div class="card">
                    <h3>Total Expenses</h3>
                    <p>₹{total_expenses:.2f}</p>
                </div>

                <div class="card">
                    <h3>Current Balance</h3>
                    <p>₹{balance:.2f}</p>
                </div>

            </div>

            <div class="form-box">

                <h2>Add Transaction</h2>

                <form method="POST" action="/add">

                    <input
                        type="text"
                        name="description"
                        placeholder="Description"
                        required
                    >

                    <input
                        type="number"
                        name="amount"
                        placeholder="Amount"
                        step="0.01"
                        min="0.01"
                        required
                    >

                    <select name="transaction_type" required>
                        <option value="Income">Income</option>
                        <option value="Expense">Expense</option>
                    </select>

                    <button type="submit">
                        Add Transaction
                    </button>

                </form>

            </div>

            <div class="table-box">

                <h2>Recent Transactions</h2>

                <table>
                    <tr>
                        <th>Description</th>
                        <th>Amount</th>
                        <th>Type</th>
                        <th>Description</th>
<th>Amount</th>
<th>Type</th>
<th>Action</th>
                    </tr>

                    {transaction_rows}

                </table>

            </div>

        </div>

    </body>
    </html>
    """


@app.route("/add", methods=["POST"])
def add_transaction():

    description = request.form["description"]
    amount = float(request.form["amount"])
    transaction_type = request.form["transaction_type"]

    connection = get_db_connection()

    connection.execute(
        """
        INSERT INTO transactions
        (description, amount, transaction_type)
        VALUES (?, ?, ?)
        """,
        (description, amount, transaction_type)
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
    assistant_response = ""

    if request.method == "POST":
        user_message = request.form["message"]
        assistant_response = finance_chatbot(user_message)

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Finance Chatbot</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f0f4f8;
                padding: 30px;
            }}

            .chat-box {{
                max-width: 700px;
                margin: auto;
                background: white;
                padding: 25px;
                border-radius: 12px;
            }}

            input {{
                width: 70%;
                padding: 12px;
            }}

            button {{
                padding: 12px;
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 6px;
            }}

            .answer {{
                background: #e0f2fe;
                padding: 15px;
                margin-top: 20px;
                border-radius: 8px;
            }}
        </style>
    </head>

    <body>
        <div class="chat-box">
            <h1>AI Finance Assistant Chatbot</h1>
            <p>Ask me about saving, budget, income or expenses.</p>

            <form method="POST">
                <input
                    type="text"
                    name="message"
                    placeholder="Ask your finance question"
                    required
                >
                <button type="submit">Ask</button>
            </form>

            <div class="answer">
                <h3>Assistant:</h3>
                <p>{assistant_response}</p>
            </div>

            <br>
            <a href="/">Back to Dashboard</a>
        </div>
    </body>
    </html>
    """


if __name__ == "__main__":
    app.run(debug=True)


if __name__ == "__main__":
    app.run(debug=True)