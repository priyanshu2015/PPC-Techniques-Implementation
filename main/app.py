from flask import Flask, request, jsonify, render_template
import tenseal as ts
import sqlite3

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
        if isinstance(row[0], float):
            encrypted_balance = encrypt_value(row[0])
        else:
            # Deserialize the bytes to obtain the encrypted value object
            encrypted_balance = ts.ckks_vector_from(context, row[0])
        return encrypted_balance
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

    # Connect to the database
    conn = sqlite3.connect('bank.db')

    # Fetch user's current balance
    cursor = conn.cursor()
    cursor.execute('SELECT balance FROM users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    if row is None:
        conn.close()
        return jsonify({"error": "User not found"}), 404

    if isinstance(row[0], float):
        current_balance = encrypt_value(row[0])
    else:
        current_balance = ts.ckks_vector_from(context, row[0])

    # Add the deposit amount
    new_balance = current_balance + encrypt_value(amount)

    # Encrypt the new balance
    # encrypted_new_balance = encrypt_value(new_balance)

    # Update user's balance in the database
    cursor.execute('UPDATE users SET balance = ? WHERE id = ?', (new_balance.serialize(), user_id))
    conn.commit()

    # Close the database connection
    conn.close()

    return jsonify({"message": "Deposit successful"})


@app.route('/balance/<int:user_id>', methods=['GET'])
def get_balance_route(user_id):
    conn = sqlite3.connect('bank.db')
    encrypted_balance = get_balance(conn, user_id)
    conn.close()

    if encrypted_balance is None:
        return jsonify({"error": "User not found"}), 404

    # Decrypt the balance
    decrypted_balance = decrypt_value(encrypted_balance.serialize())

    # Return the decrypted balance
    return jsonify({"balance": decrypted_balance})


# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)