import sqlite3
from datetime import date


TRANSACTION_CATEGORIES = (
    "Food",
    "Travel",
    "Education",
    "Shopping",
    "Bills",
    "Salary",
    "Other",
)

def create_database():
    connection = sqlite3.connect("finance.db")
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            transaction_type TEXT NOT NULL
        )
    """)

    columns = {
        column[1]
        for column in cursor.execute("PRAGMA table_info(transactions)").fetchall()
    }

    if "category" not in columns:
        cursor.execute(
            "ALTER TABLE transactions ADD COLUMN category TEXT NOT NULL DEFAULT 'Other'"
        )

    if "date" not in columns:
        cursor.execute("ALTER TABLE transactions ADD COLUMN date TEXT")

    cursor.execute(
        "UPDATE transactions SET date = ? WHERE date IS NULL OR date = ''",
        (date.today().isoformat(),),
    )

    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_database()
    print("Database created successfully!")