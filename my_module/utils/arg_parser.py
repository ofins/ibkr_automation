import argparse

parser = argparse.ArgumentParser(description="Trade Input")
parser.add_argument("--symbol", type=str, help="Stock Symbol", default="AAPL")
parser.add_argument("--menu", type=str, help="Menu")

args = parser.parse_args()
