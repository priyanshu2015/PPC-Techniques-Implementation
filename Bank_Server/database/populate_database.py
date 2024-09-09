import sqlite3
import requests
import random

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
def create_random_transactions(userid, count=5):
    targets = ['ATM Withdraw', 'Money Transfer', 'Online Shopping', 'Bill Payment']
    for _ in range(count):
        amount = round(random.uniform(10, 500), 2)
        target = random.choice(targets)

        cursor.execute('''
        INSERT INTO transactions (userid, amount, target)
        VALUES (?, ?, ?)
        ''', (userid, amount, target))


# Populate database with random users and transactions
def populate_db_with_dummy_data(user_count=10):
    users = fetch_random_users(user_count)
    for user in users:
        name = f"{user['name']['first']} {user['name']['last']}"
        balance = round(random.uniform(100, 5000), 2)
        creditscore = random.randint(300, 850)

        cursor.execute('''
        INSERT INTO user (name, balance, creditscore)
        VALUES (?, ?, ?)
        ''', (name, balance, creditscore))

        # Get the last inserted userid
        userid = cursor.lastrowid

        # Create random transactions for this user
        create_random_transactions(userid, random.randint(3, 10))


# Insert dummy data into the database
populate_db_with_dummy_data(10)

# Commit and close the database connection
conn.commit()
conn.close()
