import crypten
import torch
import requests

# Initialize CrypTen
crypten.init()

# Bob's data
data_bob = torch.tensor([75])

# Encrypt Bob's data
encrypted_data_bob = crypten.cryptensor(data_bob, src=0)

# Serialize the tensor for sending
serialized_data = torch.save(encrypted_data_bob, 'encrypted_data_bob.pth')

# Send encrypted data to Charlie
url = 'http://127.0.0.1:5000/upload/bob'
files = {'file': ('encrypted_data_bob.pth', open('encrypted_data_bob.pth', 'rb'))}
response = requests.post(url, files=files)
print("Bob's data sent with response:", response.text)

# Send a request to Charlie to compute the sum
url = 'http://127.0.0.1:5000/compute'
response = requests.get(url)
if response.status_code != 200:
    print("Failed to get response from Charlie.")
    print(f"status code: {response.status_code}")
print("Response from Charlie:", response.json())
