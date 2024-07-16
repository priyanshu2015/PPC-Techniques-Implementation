import requests
from mpyc.runtime import mpc
import asyncio
import pickle


async def main():
    print("Party 0: Starting MPC runtime")
    await mpc.start()
    print("Party 0: MPC runtime started")
    # Alice's secret
    secret_alice = 50000
    secint = mpc.SecInt()
    share_alice = secint(secret_alice)

    # Send Alice's share
    #mpc.transfer(share_alice, senders=1)
    await mpc.output(mpc.input(share_alice, receivers=[0]))

    mpc.shutdown()

if __name__ == '__main__':
    mpc.run(main())
