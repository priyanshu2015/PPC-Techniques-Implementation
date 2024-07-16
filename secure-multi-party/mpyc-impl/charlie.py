from mpyc.runtime import mpc

async def main():
    print("Party 2: Starting MPC runtime")
    await mpc.start()
    print("Party 2: MPC runtime started")

    print("Charlie is ready.")
    # Receive shares from Alice and Bob
    share_alice = await mpc.transfer(mpc.SecInt(), senders=1)
    print(f"Received Alice's share: {share_alice}")
    share_bob = await mpc.transfer(mpc.SecInt(), senders=2)
    print(f"Received Bob's share: {share_bob}")

    # Compute the maximum value
    max_value = await mpc.output(mpc.max([share_alice[0], share_bob[0]]))
    print(f"The maximum value is: {max_value}")

    await mpc.shutdown()

if __name__ == '__main__':
    mpc.run(main())
