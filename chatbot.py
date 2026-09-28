import re

from database import TRANSACTION_CATEGORIES


def _format_currency(amount):
    return f"₹{amount:,.2f}"


def _transaction_value(transaction, key, default=None):
    try:
        return transaction[key]
    except (KeyError, IndexError, TypeError):
        return default


def finance_chatbot(message, transactions=None):
    normalized_message = re.sub(r"\s+", " ", (message or "").strip().lower())
    words = set(re.findall(r"[a-z]+", normalized_message))
    transactions = list(transactions or [])

    income = sum(
        float(_transaction_value(transaction, "amount", 0) or 0)
        for transaction in transactions
        if _transaction_value(transaction, "transaction_type", "") == "Income"
    )
    expenses = sum(
        float(_transaction_value(transaction, "amount", 0) or 0)
        for transaction in transactions
        if _transaction_value(transaction, "transaction_type", "") == "Expense"
    )
    balance = income - expenses

    expense_by_category = {}
    for transaction in transactions:
        if _transaction_value(transaction, "transaction_type", "") != "Expense":
            continue
        category = _transaction_value(transaction, "category") or "Other"
        expense_by_category[category] = expense_by_category.get(category, 0) + float(
            _transaction_value(transaction, "amount", 0) or 0
        )

    if not normalized_message:
        return "Type a question about your income, expenses, balance, recent transactions, or saving."

    if "help" in words:
        return (
            "You can ask me about your total income, total expenses, current balance, "
            "recent transactions, spending by category, or saving suggestions."
        )

    if words.intersection({"hello", "hi", "hey"}):
        return "Hello! Ask me about your finances or type 'help' to see what I can do."

    if any(phrase in normalized_message for phrase in ("recent transaction", "latest transaction", "transaction history")) or "recent" in words:
        if not transactions:
            return "There are no transactions recorded yet. Add one from the dashboard and ask me again."
        recent_transactions = transactions[:5]
        lines = ["Your 5 most recent transactions:"]
        for transaction in recent_transactions:
            description = _transaction_value(transaction, "description", "Transaction")
            transaction_type = _transaction_value(transaction, "transaction_type", "Transaction")
            category = _transaction_value(transaction, "category") or "Other"
            transaction_date = _transaction_value(transaction, "date") or "Date not recorded"
            amount = float(_transaction_value(transaction, "amount", 0) or 0)
            lines.append(
                f"• {transaction_date} | {description} | {category} | "
                f"{transaction_type}: {_format_currency(amount)}"
            )
        return "\n".join(lines)

    requested_category = next(
        (
            category
            for category in TRANSACTION_CATEGORIES
            if re.search(rf"\b{re.escape(category.lower())}\b", normalized_message)
        ),
        None,
    )
    if requested_category:
        amount = expense_by_category.get(requested_category, 0)
        return f"Your recorded expenses in {requested_category} total {_format_currency(amount)}."

    if "category" in words or "categories" in words or "by category" in normalized_message:
        if not expense_by_category:
            return "No expenses are recorded yet, so there is no category spending to summarize."
        lines = ["Your recorded expenses by category:"]
        for category, amount in sorted(expense_by_category.items(), key=lambda item: item[1], reverse=True):
            lines.append(f"• {category}: {_format_currency(amount)}")
        return "\n".join(lines)

    if "balance" in words or "left over" in normalized_message or "leftover" in words:
        return f"Your current recorded balance is {_format_currency(balance)} (income minus expenses)."

    if words.intersection({"income", "salary", "earned", "earnings"}):
        return f"Your total recorded income is {_format_currency(income)}."

    if words.intersection({"expense", "expenses", "spending", "spent"}):
        return f"Your total recorded expenses are {_format_currency(expenses)}."

    if words.intersection({"save", "saving", "savings", "suggestion", "suggestions", "advice"}):
        if income <= 0:
            suggestion = "Record some income to get a meaningful savings-rate suggestion."
        else:
            savings_rate = max(balance, 0) / income * 100
            if balance < 0:
                suggestion = "Your recorded expenses are higher than income. Review your largest spending category first."
            elif savings_rate < 20:
                suggestion = (
                    f"You are retaining about {savings_rate:.1f}% of recorded income. "
                    "Try setting aside a little more and review your largest spending category."
                )
            else:
                suggestion = (
                    f"You are retaining about {savings_rate:.1f}% of recorded income. "
                    "Keep setting aside part of your balance for savings."
                )
        if expense_by_category:
            largest_category, largest_amount = max(expense_by_category.items(), key=lambda item: item[1])
            suggestion += f" Your highest expense category is {largest_category} at {_format_currency(largest_amount)}."
        return suggestion

    if "budget" in words:
        return "Use your recorded category totals to set spending limits, then compare them with your actual expenses regularly."

    return "I can answer questions about income, expenses, balance, recent transactions, spending by category, and saving suggestions. Type 'help' for examples."


if __name__ == "__main__":
    print("AI Finance Assistant Chatbot")
    print("Type 'exit' to stop the chatbot.")

    while True:
        user_message = input("You: ")

        if user_message.lower() == "exit":
            print("Assistant: Thank you for using AI Finance Assistant!")
            break

        response = finance_chatbot(user_message)
        print("Assistant:", response)