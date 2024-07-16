import requests
import torch
import syft as sy

# Create a hook for PyTorch
hook = sy.TorchHook(torch)

# Bob's data
y = torch.tensor([3, 2])

# Create shares
alice = sy.VirtualWorker(hook, id="alice")
bob = sy.VirtualWorker(hook, id="bob")
charlie = sy.VirtualWorker(hook, id="charlie")
y_shares = y.share(alice, bob, charlie)

# Send Bob's share to Charlie
data = {'worker_id': 'bob', 'share': y_shares.child(child=bob).get().tolist()}
requests.post('http://localhost:5000/receive_share', json=data)