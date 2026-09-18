def finance_chatbot(message):
    message = message.lower()

    if "hello" in message or "hi" in message or "hey" in message:
        return "Hello! I am your AI Finance Assistant. How can I help you?"

    elif "save" in message or "saving" in message:
        return "Try to save at least 20% of your monthly income."

    elif "budget" in message:
        return "Create a monthly budget for food, travel, education and other expenses."

    elif "expense" in message or "spending" in message:
        return "Track every expense regularly to understand where your money is going."

    elif "income" in message or "salary" in message:
        return "Your income is the money you receive from salary, business or other sources."

    elif "advice" in message or "suggestion" in message:
        return "Avoid unnecessary spending and maintain an emergency savings fund."

    elif "help" in message:
        return """
I can help you with:

1. Saving money
2. Budget planning
3. Expense tracking
4. Financial advice
5. Income management
"""

    else:
        return "Sorry, I am still learning. Please ask about saving, budget, income or expenses."


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