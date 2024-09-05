import sqlite3

DATABASE = 'database/bank.db'

def get_db_connection():
    """
    Function to establish a connection to the database
    :return: sqlite3 connection object
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # This allows rows to be returned as dictionaries
    return conn


def fetch_all_users():
    """
    Function to fetch all users from the database
    :return: List of users as dictionaries
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user')
    users = cursor.fetchall()
    conn.close()
    return [dict(user) for user in users]


def fetch_all_transactions():
    """
    Function to fetch all transactions from the database
    :return: List of transactions as dictionaries
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM transactions')
    transactions = cursor.fetchall()
    conn.close()
    return [dict(transaction) for transaction in transactions]


def fetch_user_by_id(userid):
    """
    Function to fetch a specific user by userid
    :param userid: the userid of the user
    :return: user as a dictionary
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user WHERE userid = ?', (userid,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return dict(user)
    else:
        return None  # Return None if user is not found


def fetch_transaction_by_id(transactionid):
    """
    function to fetch a specific transaction by transactionid
    :param transactionid: the transactionid of the transaction
    :return: transaction as a dictionary
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM transactions WHERE transactionid = ?', (transactionid,))
    transaction = cursor.fetchone()
    conn.close()
    if transaction:
        return dict(transaction)
    else:
        return None  # Return None if transaction is not found


def fetch_transactions_by_userid(userid):
    """
    Function to fetch all transactions for a specific user
    :param userid: the userid of the user
    :return: List of transactions as dictionaries
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM transactions WHERE userid = ?', (userid,))
    transactions = cursor.fetchall()
    conn.close()
    return [dict(transaction) for transaction in transactions]
