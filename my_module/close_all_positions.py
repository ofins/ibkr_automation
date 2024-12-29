from ib_insync import MarketOrder


async def close_all_positions(ib):
    """
    Closes all active positions.
    """
    try:
        print("Cancelling all oustanding orders...")
        ib.reqGlobalCancel()

        for pos in ib.positions():  # Exit all active trades
            contract = pos.contract
            contract.exchange = "SMART"
            order = MarketOrder(
                "SELL" if pos.position > 0 else "BUY", abs(pos.position)
            )
            trade = ib.placeOrder(contract, order)
            while not trade.isDone():
                await asyncio.sleep(1)
            print(
                f"Position for {contract.localSymbol} with {abs(pos.position)} shares closed."
            )
    except Exception as e:
        print(f"Error during position closure: {e}")
