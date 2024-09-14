"""
Extremely simple example of NoKnow ZK Proof implementation
"""
from getpass import getpass
from zero_knowledge_proof.schnorr_core import ZK, ZKSignature, ZKParameters, ZKData, ZKProof
from queue import Queue
from threading import Thread
import json


def client(iq: Queue, oq: Queue):
    client_zk = ZK.new(curve_name="secp256k1", hash_alg="sha3_256")

    # Create signature and send to server
    signature = client_zk.create_signature(getpass("Enter Password: "))
    signature_json = signature.to_json()
    # oq.put(json.dumps(signature_json))
    oq.put(signature_json)

    # Receive the token from the server
    token = iq.get()

    # Create a proof that signs the provided token and sends to server
    proof = client_zk.sign(getpass("Enter Password Again: "), token)
    proof_json = proof.to_json()

    # Send the token and proof to the server
    oq.put(proof_json)

    # Wait for server response!
    print("Success!" if iq.get() else "Failure!")


def server(iq: Queue, oq: Queue):
    # Set up server component
    server_password = "SecretServerPassword"
    server_zk = ZK.new(curve_name="secp384r1", hash_alg="sha3_512")
    server_signature: ZKSignature = server_zk.create_signature("SecureServerPassword")

    # Load the received signature from the Client
    sig = iq.get()
    client_signature = ZKSignature.from_json(sig)
    client_zk = ZK(client_signature.params)

    # Create a signed token and send to the client
    token = server_zk.sign("SecureServerPassword2", client_zk.token())
    oq.put(token.to_json())

    # Get the token from the client
    proof = ZKData.from_json(iq.get())
    token = ZKData.from_json(proof.data)

    # In this example, the server signs the token so it can be sure it has not been modified
    if not server_zk.verify(token, server_signature):
        oq.put(False)
    else:
        print(client_zk.verify(proof, client_signature, data=token))
        oq.put(client_zk.verify(proof, client_signature, data=token))



def main():
    q1, q2 = Queue(), Queue()
    threads = [
        Thread(target=client, args=(q1, q2)),
        Thread(target=server, args=(q2, q1)),
    ]
    for func in [Thread.start, Thread.join]:
        for thread in threads:
            func(thread)


if __name__ == "__main__":
    main()