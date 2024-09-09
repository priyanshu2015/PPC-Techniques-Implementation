import os

import crypten
import torch
import requests

# Initialize CrypTen
if os.name == 'nt':
    crypten.init_thread(0, 1)
else:
    crypten.init()

# bank1's data
bank_data = torch.tensor([20])

# Encrypt bank1's data
encrypted_data_bank1 = crypten.cryptensor(bank_data, src=0)

# Serialize the tensor for sending
serialized_data = torch.save(encrypted_data_bank1, 'local/encrypted_data_bank1.pth')

# Send encrypted data to Charlie
url = 'http://127.0.0.1:5000/upload/bank1'
files = {'file': ('encrypted_data_bank1.pth', open('local/encrypted_data_bank1.pth', 'rb'))}
response = requests.post(url, files=files)
if response.status_code != 200:
    print("Failed to send data to Charlie.")
    print(f"status code: {response.status_code}")
print("bank1's data sent with response:", response.text)
