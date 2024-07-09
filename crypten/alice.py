import crypten
import torch
import requests

# Initialize CrypTen
crypten.init()

# Alice's data
data_alice = torch.tensor([20])

# Encrypt Alice's data
encrypted_data_alice = crypten.cryptensor(data_alice, src=0)

# Serialize the tensor for sending
serialized_data = torch.save(encrypted_data_alice, 'encrypted_data_alice.pth')

# Send encrypted data to Charlie
url = 'http://127.0.0.1:5000/upload/alice'
files = {'file': ('encrypted_data_alice.pth', open('encrypted_data_alice.pth', 'rb'))}
response = requests.post(url, files=files)
if response.status_code != 200:
    print("Failed to send data to Charlie.")
    print(f"status code: {response.status_code}")
print("Alice's data sent with response:", response.text)
