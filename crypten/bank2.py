import os

import crypten
import torch
import requests

# Initialize CrypTen
if os.name == 'nt':
    crypten.init_thread(0, 1)
else:
    crypten.init()

# bank2's data
data_bank2 = torch.tensor([75])

# Encrypt bank2's data
encrypted_data_bank2 = crypten.cryptensor(data_bank2, src=0)

# Serialize the tensor for sending
serialized_data = torch.save(encrypted_data_bank2, 'local/encrypted_data_bank2.pth')

# Send encrypted data to Charlie
url = 'http://127.0.0.1:5000/upload/bank2'
files = {'file': ('encrypted_data_bank2.pth', open('local/encrypted_data_bank2.pth', 'rb'))}
response = requests.post(url, files=files)
print("bank2's data sent with response:", response.text)

# Send a request to Charlie to compute the sum
url = 'http://127.0.0.1:5000/compute'
response = requests.get(url)
if response.status_code != 200:
    print("Failed to get response from Charlie.")
    print(f"status code: {response.status_code}")
print("Response from Charlie:", response.json())
