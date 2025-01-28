from ib_insync import IB, Event, Stock
from tabulate import tabulate

from my_module.logger import Logger

logger = Logger.get_logger()


class Level2Table:
    def __init__(self, ib, contract):
        self.ib = ib
        self.contract = contract
        self.bids = []  # List to store bid prices and sizes
        self.asks = []  # List to store ask prices and sizes

        # Subscribe to market depth
        # self.ib.reqMktDepth(self.contract)
        # print(self.ib.reqMktDepth(Stock("AAPL", "NYSE", "USD")))
        # print(self.ib.reqMktDepth(Stock("AAPL", "AMEX", "USD")))
        print(self.ib.reqMktDepth(self.contract))

        # Bind the event to the callback
        self.ib.pendingTickersEvent += self.update_table

    def update_table(self, tickers):
        self.bids = []  # Clear bids
        self.asks = []  # Clear asks
        # logger.info(tickers)
        for ticker in tickers:
            if ticker.domBids:
                self.bids = [(entry.price, entry.size) for entry in ticker.domBids]

            if ticker.domAsks:
                self.asks = [(entry.price, entry.size) for entry in ticker.domAsks]
        # logger.info(self.bids)
        # logger.info(self.asks)
        # logger.info("-----------------------------")

        self.display_table()

    def display_table(self):
        table_data = []

        # Format bids and asks for display
        for i in range(max(len(self.bids), len(self.asks))):
            bid = self.bids[i] if i < len(self.bids) else ("", "")
            ask = self.asks[i] if i < len(self.asks) else ("", "")
            table_data.append([bid[0], bid[1], ask[0], ask[1]])

        # Print the table
        print(
            tabulate(
                table_data,
                headers=["Bid Price", "Bid Size", "Ask Price", "Ask Size"],
                tablefmt="grid",
            )
        )


# Main execution
if __name__ == "__main__":
    ib = IB()
    ib.connect("127.0.0.1", 7497, clientId=3)

    # Define a contract (e.g., AAPL stock)
    contract = Stock("AAPL", "NASDAQ", "USD")

    # Start the Level 2 table
    level2_table = Level2Table(ib, contract)

    try:
        ib.run()
    except KeyboardInterrupt:
        ib.disconnect()
