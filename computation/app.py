from flask import Flask, request, jsonify
import pandas as pd
import tenseal as ts
import io
import traceback

app = Flask(__name__)

context = ts.context(
            ts.SCHEME_TYPE.CKKS,
            poly_modulus_degree=8192,
            coeff_mod_bit_sizes=[60, 40, 40, 60]
          )
context.global_scale = 2**40


@app.route('/compute-sum', methods=['POST'])
def compute_sum():
    file = request.files['file']
    if not file:
        return "No file uploaded", 400

    # Read the CSV file into a DataFrame
    csv_data = pd.read_csv(io.StringIO(file.stream.read().decode("UTF8")))
    if 'amount' not in csv_data.columns:
        return "CSV file does not contain 'amount' column", 400

    # Deserialize encrypted 'amount' column
    encrypted_amounts = [ts.ckks_vector_from(context, bytes.fromhex(val)) for val in csv_data['amount']]

    # Perform the sum on encrypted data
    encrypted_sum = sum(encrypted_amounts)

    serialized_sum = encrypted_sum.serialize().hex()

    return jsonify({"sum": serialized_sum})


@app.route('/compute-avg', methods=['POST'])
def compute_average():
    try:
        file = request.files['file']
        data = request.form
        current_balance = data["current_balance"]
        current_balance = ts.ckks_vector_from(context, bytes.fromhex(current_balance))
        sum = current_balance
        if not file:
            return "No file uploaded", 400

        # Read the CSV file into a DataFrame
        csv_data = pd.read_csv(io.StringIO(file.stream.read().decode("UTF8")))
        if 'amount' not in csv_data.columns:
            return "CSV file does not contain 'amount' column", 400

        # Deserialize encrypted 'amount' column
        encrypted_amounts = [ts.ckks_vector_from(context, bytes.fromhex(val)) for val in csv_data['amount']]

        for i in range(len(encrypted_amounts) - 1, -1, -1):
            prev_balance = current_balance - encrypted_amounts[i]
            sum = sum + prev_balance
            current_balance = prev_balance

        return jsonify({"total_balance": sum.serialize().hex()})
    except Exception as e:
        error_trace = traceback.format_exc()
        print(error_trace)



if __name__ == '__main__':
    app.run(debug=True, port=5001)
