from ib_insync import IB, MarketOrder, util

ib = IB()


def connect_ib():
    try:
        print("3")
        ib.connect("127.0.0.1", 7497, clientId=1)
        print(f"Connected to IBKR tws API")
        return 1
    except Exception as e:
        print(f"Connection error: {e}")
        return 0
