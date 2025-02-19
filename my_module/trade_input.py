import argparse

parser = argparse.ArgumentParser(description="Trade Input")
parser.add_argument("--symbol", type=str, help="Stock Symbol", default="AAPL")
args = parser.parse_args()

# Reversal Algo
WATCH_STOCK = args.symbol

# Scaling Algo
SYMBOL = "AAPL"
DIRECTION = "LONG"
ENTRY_PRICE = 230.5
POSITION_SIZE = 10
INCREMENT_RANGE = 1
NUM_INCREMENTS = 3
