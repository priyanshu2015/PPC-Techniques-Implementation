import requests
import torch
import syft as sy

# Create a hook for PyTorch
hook = sy.TorchHook(torch)

# Alice's data
x = torch.tensor([5, 7])

# Create shares
alice = sy.VirtualWorker(hook, id="alice")
bob = sy.VirtualWorker(hook, id="bob")
charlie = sy.VirtualWorker(hook, id="charlie")
x_shares = x.share(alice, bob, charlie)

# Send Alice's share to Charlie
data = {'worker_id': 'alice', 'share': x_shares.child(child=alice).get().tolist()}
requests.post('http://localhost:5000/receive_share', json=data)

# Request computation
response = requests.post('http://localhost:5000/compute')
result = response.json().get('result')
print(f"Result: {result}")