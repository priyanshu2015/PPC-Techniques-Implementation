import sqlite3
import requests
import random

"""
This script populates the bank database with dummy data for users and transactions.
"""

# Establish a connection to the database
conn = sqlite3.connect('bank.db')
cursor = conn.cursor()

# Create user table
cursor.execute('''
CREATE TABLE IF NOT EXISTS user (
    userid INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    balance REAL NOT NULL,
    creditscore INTEGER NOT NULL
)
''')

# Create transactions table
cursor.execute('''
CREATE TABLE IF NOT EXISTS transactions (
    transactionid INTEGER PRIMARY KEY AUTOINCREMENT,
    userid INTEGER,
    amount REAL NOT NULL,
    target TEXT NOT NULL,
    FOREIGN KEY(userid) REFERENCES user(userid)
)
''')


# Fetch random users from randomuser.me API
def fetch_random_users(n):
    url = f'https://randomuser.me/api/?results={n}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['results']
    else:
        raise Exception(f"Failed to fetch data: {response.status_code}")


# Function to generate random transactions
def create_random_transactions(userid, count=100):
    positive_targets = ['Wage', 'Money Transfer']
    negative_targets = ['ATM Withdraw', 'Online Shopping', 'Bill Payment']

    total_balance = 0  # To track the balance resulting from the transactions

    for _ in range(count):
        # Randomly choose between positive and negative transactions
        if random.choice([True, False]):
            # Positive transaction
            amount = round(random.uniform(100, 1000), 2)  # Higher range for positive transactions
            target = random.choice(positive_targets)
        else:
            # Negative transaction
            amount = round(random.uniform(10, 500), 2) * -1  # Negative amount for withdrawals/payments
            target = random.choice(negative_targets)

        # Update balance based on the transaction amount
        total_balance += amount

        # Insert transaction into the transactions table
        cursor.execute('''
        INSERT INTO transactions (userid, amount, target)
        VALUES (?, ?, ?)
        ''', (userid, amount, target))

    return total_balance  # Return the sum of all transactions


# function to populate the database with dummy data and compute correct balances
def populate_db_with_dummy_data(user_count=10):
    users = fetch_random_users(user_count)  # Fetch random users
    for user in users:
        name = f"{user['name']['first']} {user['name']['last']}"
        creditscore = random.randint(300, 850)

        # Insert the user into the user table
        cursor.execute('''
               INSERT INTO user (name, balance, creditscore)
               VALUES (?, ?, ?)
               ''', (name, 0, creditscore))

        # Get the last inserted userid
        userid = cursor.lastrowid

        # Create random transactions for this user (100 transactions)
        balance = create_random_transactions(userid, random.randint(80, 120))
        #balance = create_random_transactions(userid, 50)

        # Now update the user with the correct balance based on transactions
        cursor.execute('''
        UPDATE user
        SET balance = ?
        WHERE userid = ?
        ''', (round(balance, 2), userid))


# Insert dummy data into the database
populate_db_with_dummy_data(10)

# Commit and close the database connection
conn.commit()
conn.close()
