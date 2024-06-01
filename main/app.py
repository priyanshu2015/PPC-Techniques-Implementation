from flask import Flask, request, jsonify, render_template
import tenseal as ts
import sqlite3
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import requests
import io
import pandas as pd

app = Flask(__name__)

# Setup TenSEAL context
context = ts.context(
            ts.SCHEME_TYPE.CKKS,
            poly_modulus_degree=8192,
            coeff_mod_bit_sizes=[60, 40, 40, 60]
          )
context.generate_galois_keys()
context.global_scale = 2**40
print(context)

# Database initialization
conn = sqlite3.connect('bank.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT,
        balance REAL
    )
''')
conn.commit()

DATABASE_URL = "sqlite:///bank.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# Define the Transaction model
class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    amount = Column(String, nullable=False)

# Create the transactions table in the database
Base.metadata.create_all(engine)


# Helper functions
def encrypt_value(value):
    encrypted_value = ts.ckks_vector(context, [value])
    return encrypted_value

def decrypt_value(encrypted_value):
    decrypted_value = ts.ckks_vector_from(context, encrypted_value).decrypt(context.secret_key())
    return decrypted_value[0]

def update_balance(conn, user_id, amount):
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users
        SET balance = balance + ?
        WHERE id = ?
    ''', (amount, user_id))
    conn.commit()
    cursor.close()

def get_balance(conn, user_id):
    cursor = conn.cursor()
    cursor.execute('SELECT balance FROM users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    cursor.close()
    if row:
        balance = row[0]
        # if isinstance(row[0], float):
        #     encrypted_balance = encrypt_value(row[0])
        # else:
        #     # Deserialize the bytes to obtain the encrypted value object
        #     encrypted_balance = ts.ckks_vector_from(context, row[0])
        # return encrypted_balance
        return balance
    else:
        return None


# API endpoints
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/users', methods=['GET'])
def get_users():
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM users')
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({"users": users})

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    cursor.execute('SELECT id, name, balance FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    if user:
        return jsonify({"user": user})
    else:
        return jsonify({"error": "User not found"}), 404

@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    name = data.get('name')
    if name:
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (name, balance) VALUES (?, ?)', (name, 0))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "User created successfully"})
    else:
        return jsonify({"error": "Name is required"}), 400


@app.route('/deposit', methods=['POST'])
def deposit():
    data = request.json
    user_id = data['user_id']
    amount = data['amount']
    # Create a session
    session = Session()

    # Connect to the database
    conn = sqlite3.connect('bank.db')

    # Fetch user's current balance
    cursor = conn.cursor()
    cursor.execute('SELECT balance FROM users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    if row is None:
        conn.close()
        return jsonify({"error": "User not found"}), 404

    current_balance = float(row[0])

    # if isinstance(row[0], float):
    #     current_balance = encrypt_value(row[0])
    # else:
    #     current_balance = ts.ckks_vector_from(context, row[0])

    # Add the deposit amount
    # new_balance = current_balance + encrypt_value(amount)

    new_balance = current_balance + amount

    # Encrypt the new balance
    # encrypted_new_balance = encrypt_value(new_balance)

    # Update user's balance in the database
    cursor.execute('UPDATE users SET balance = ? WHERE id = ?', (new_balance, user_id))
    conn.commit()

    # Save the transaction to the database
    new_transaction = Transaction(user_id=data['user_id'], amount=amount)
    print(new_transaction)
    session.add(new_transaction)
    session.commit()

    # Close the database connection
    conn.close()

    return jsonify({"message": "Deposit successful"})


@app.route('/withdraw', methods=['POST'])
def withdraw():
    data = request.get_json()
    # Create a session
    session = Session()
    if 'amount' not in data or 'user_id' not in data:
        return "Amount and user ID must be provided", 400

    # Connect to the database
    conn = sqlite3.connect('bank.db')

    # Fetch user's current balance
    cursor = conn.cursor()
    cursor.execute('SELECT balance FROM users WHERE id = ?', (data['user_id'],))
    row = cursor.fetchone()
    if row is None:
        conn.close()
        return jsonify({"error": "User not found"}), 404

    current_balance = float(row[0])

    if current_balance < data['amount']:
        conn.close()
        return jsonify({"error": "Not valid"}), 400


    new_balance = current_balance - data['amount']

    # Update user's balance in the database
    cursor.execute('UPDATE users SET balance = ? WHERE id = ?', (new_balance, data['user_id']))
    conn.commit()

    # Encrypt the negative amount
    amount = -data['amount']

    # Save the transaction to the database
    new_transaction = Transaction(user_id=data['user_id'], amount=amount)
    session.add(new_transaction)
    session.commit()

    return jsonify({"message": "Withdrawal successful", "amount": amount})


@app.route('/balance/<int:user_id>', methods=['GET'])
def get_balance_route(user_id):
    conn = sqlite3.connect('bank.db')
    balance = get_balance(conn, user_id)
    conn.close()

    if balance is None:
        return jsonify({"error": "User not found"}), 404

    # Decrypt the balance
    # decrypted_balance = decrypt_value(encrypted_balance.serialize())

    # Return the decrypted balance
    return jsonify({"balance": balance})


@app.route('/validate-balance/<int:user_id>', methods=['GET'])
def validate_balance(user_id):
    # Create a session
    session = Session()
    # Retrieve transactions for the given user_id
    transactions = session.query(Transaction).filter(Transaction.user_id == user_id).all()

    if not transactions:
        return jsonify({"message": "No transactions found for user_id: {}".format(user_id)}), 404

    # Encrypt amounts and create a DataFrame with the transactions
    encrypted_transactions = []
    for t in transactions:
        # Encrypt the amount before adding it to the list
        encrypted_amount = ts.ckks_vector(context, [t.amount]).serialize().hex()
        encrypted_transactions.append({"amount": encrypted_amount})

    df = pd.DataFrame(encrypted_transactions)

    # Save the DataFrame to a CSV file in memory
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    # Send the CSV file to the compute-sum endpoint
    files = {'file': ('transactions.csv', csv_buffer, 'text/csv')}
    response = requests.post('http://127.0.0.1:5001/compute-sum', files=files)

    if response.status_code != 200:
        return jsonify({"message": "Failed to compute sum"}), response.status_code

    result = response.json()

    # Decrypt the sum from the response
    decrypted_sum = ts.ckks_vector_from(context, bytes.fromhex(result['sum'])).decrypt()[0]


    conn = sqlite3.connect('bank.db')
    balance = get_balance(conn, user_id)
    conn.close()

    initial_balance = balance - round(decrypted_sum)

    # if initial balance is 0, then correct
    return jsonify({"sum": initial_balance})


@app.route('/total-credit/<int:user_id>', methods=['GET'])
def total_credit(user_id):
    # Create a session
    session = Session()
    # Retrieve transactions for the given user_id
    transactions = session.query(Transaction).filter(Transaction.user_id == user_id).all()

    if not transactions:
        return jsonify({"message": "No transactions found for user_id: {}".format(user_id)}), 404

    # Encrypt amounts and create a DataFrame with the transactions
    encrypted_transactions = []
    for t in transactions:
        if int(t.amount) > 0:
            # Encrypt the amount before adding it to the list
            encrypted_amount = ts.ckks_vector(context, [t.amount]).serialize().hex()
            encrypted_transactions.append({"amount": encrypted_amount})

    df = pd.DataFrame(encrypted_transactions)

    # Save the DataFrame to a CSV file in memory
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    # Send the CSV file to the compute-sum endpoint
    files = {'file': ('transactions.csv', csv_buffer, 'text/csv')}
    response = requests.post('http://127.0.0.1:5001/compute-sum', files=files)

    if response.status_code != 200:
        return jsonify({"message": "Failed to compute sum"}), response.status_code

    result = response.json()

    # Decrypt the sum from the response
    decrypted_sum = ts.ckks_vector_from(context, bytes.fromhex(result['sum'])).decrypt()[0]

    # if initial balance is 0, then correct
    return jsonify({"sum": decrypted_sum})


@app.route('/avg-balance/<int:user_id>', methods=['GET'])
def avg_balance(user_id):
    # Create a session
    session = Session()
    # Retrieve transactions for the given user_id
    transactions = session.query(Transaction).filter(Transaction.user_id == user_id).all()

    if not transactions:
        return jsonify({"message": "No transactions found for user_id: {}".format(user_id)}), 404

    # Encrypt amounts and create a DataFrame with the transactions
    encrypted_transactions = []
    for t in transactions:
        print(t.amount)
        # Encrypt the amount before adding it to the list
        encrypted_amount = ts.ckks_vector(context, [t.amount]).serialize().hex()
        encrypted_transactions.append({"amount": encrypted_amount})

    df = pd.DataFrame(encrypted_transactions)

    # Save the DataFrame to a CSV file in memory
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    conn = sqlite3.connect('bank.db')
    balance = get_balance(conn, user_id)
    conn.close()

    # Send the CSV file to the compute-sum endpoint
    files = {'file': ('transactions.csv', csv_buffer, 'text/csv')}
    response = requests.post('http://127.0.0.1:5001/compute-avg', files=files, data={"current_balance": ts.ckks_vector(context, [balance]).serialize().hex()})

    if response.status_code != 200:
        return jsonify({"message": "Failed to compute sum"}), response.status_code

    result = response.json()

    # Decrypt the sum from the response
    decrypted_total_balance = ts.ckks_vector_from(context, bytes.fromhex(result['total_balance'])).decrypt()[0]

    print(decrypted_total_balance)

    avg_balance = decrypted_total_balance/(len(transactions))

    # if initial balance is 0, then correct
    return jsonify({"avg_balance": avg_balance})


# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)



# 3 Usecases
# total credit
# average balance
# validate balance: To validate the balance stored in root database by performing operations on encrypted transaction