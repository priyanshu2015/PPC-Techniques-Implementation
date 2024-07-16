from mpyc.runtime import mpc

async def main():
    print("Party 1: Starting MPC runtime")
    await mpc.start()
    print("Party 1: MPC runtime started")

    print("Charlie is ready.")
    # Bob's secret
    secret_bob = 75000
    secint = mpc.SecInt()
    share_bob = secint(secret_bob)

    # Send Bob's share
    mpc.run(mpc.transfer(share_bob, senders=2))

    mpc.run(mpc.shutdown())

if __name__ == '__main__':
    mpc.run(main())