from ib_insync import IB, MarketOrder, util

# ib = IB()


def connect_ib(ib):
    """
    Connects to the IBKR TWS API.

    This function attempts to establish a connection with the Interactive
    Brokers Trader Workstation API, using a specified client ID and host.

    Returns:
        int: 1 if connection is successful, 0 if there is an error.
    """
    try:
        ib.connect("127.0.0.1", 7497, clientId=1)
        print(f"Connected to IBKR tws API")
        return 1
    except Exception as e:
        print(f"Connection error: {e}")
        return 0
