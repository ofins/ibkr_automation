from collections import defaultdict
from datetime import datetime

# Mock trades data
mock_trades = [
    {
        "Symbol": "AAPL",
        "Action": "BUY",
        "Quantity": 100,
        "Price": 150.25,
        "Time": datetime(2024, 12, 29, 14, 30),
        "Execution Price": 150.50,
    },
    {
        "Symbol": "GOOG",
        "Action": "BUY",
        "Quantity": 50,
        "Price": 2800.75,
        "Time": datetime(2024, 12, 29, 15, 0),
        "Execution Price": 2801.25,
    },
    {
        "Symbol": "AAPL",
        "Action": "SELL",
        "Quantity": 100,
        "Price": 151.25,
        "Time": datetime(2024, 12, 29, 14, 40),
        "Execution Price": 150.50,
    },
    {
        "Symbol": "GOOG",
        "Action": "SELL",
        "Quantity": 50,
        "Price": 2810.75,
        "Time": datetime(2024, 12, 29, 15, 10),
        "Execution Price": 2801.25,
    },
    {
        "Symbol": "TSLA",
        "Action": "BUY",
        "Quantity": 150,
        "Price": 600.50,
        "Time": datetime(2024, 12, 29, 10, 15),
        "Execution Price": 601.00,
    },
    {
        "Symbol": "AMZN",
        "Action": "SELL",
        "Quantity": 30,
        "Price": 3400.25,
        "Time": datetime(2024, 12, 29, 13, 0),
        "Execution Price": 3405.50,
    },
    {
        "Symbol": "TSLA",
        "Action": "SELL",
        "Quantity": 50,
        "Price": 602.75,
        "Time": datetime(2024, 12, 29, 11, 0),
        "Execution Price": 603.25,
    },
    {
        "Symbol": "AMZN",
        "Action": "BUY",
        "Quantity": 20,
        "Price": 3400.75,
        "Time": datetime(2024, 12, 29, 13, 30),
        "Execution Price": 3402.50,
    },
    {
        "Symbol": "AAPL",
        "Action": "BUY",
        "Quantity": 200,
        "Price": 152.50,
        "Time": datetime(2024, 12, 29, 14, 45),
        "Execution Price": 153.00,
    },
    {
        "Symbol": "GOOG",
        "Action": "BUY",
        "Quantity": 100,
        "Price": 2825.50,
        "Time": datetime(2024, 12, 29, 15, 20),
        "Execution Price": 2828.00,
    },
    {
        "Symbol": "GOOG",
        "Action": "SELL",
        "Quantity": 100,
        "Price": 2835.00,
        "Time": datetime(2024, 12, 29, 15, 40),
        "Execution Price": 2830.50,
    },
    {
        "Symbol": "TSLA",
        "Action": "BUY",
        "Quantity": 50,
        "Price": 603.00,
        "Time": datetime(2024, 12, 29, 10, 30),
        "Execution Price": 603.75,
    },
    {
        "Symbol": "AMZN",
        "Action": "SELL",
        "Quantity": 50,
        "Price": 3405.00,
        "Time": datetime(2024, 12, 29, 14, 0),
        "Execution Price": 3410.00,
    },
    {
        "Symbol": "AAPL",
        "Action": "SELL",
        "Quantity": 200,
        "Price": 153.75,
        "Time": datetime(2024, 12, 29, 14, 50),
        "Execution Price": 154.00,
    },
    {
        "Symbol": "GOOG",
        "Action": "BUY",
        "Quantity": 150,
        "Price": 2840.00,
        "Time": datetime(2024, 12, 29, 15, 30),
        "Execution Price": 2845.25,
    },
    {
        "Symbol": "AAPL",
        "Action": "BUY",
        "Quantity": 100,
        "Price": 155.25,
        "Time": datetime(2024, 12, 29, 15, 50),
        "Execution Price": 156.00,
    },
    {
        "Symbol": "AMZN",
        "Action": "BUY",
        "Quantity": 50,
        "Price": 3420.00,
        "Time": datetime(2024, 12, 29, 16, 0),
        "Execution Price": 3422.50,
    },
    {
        "Symbol": "GOOG",
        "Action": "SELL",
        "Quantity": 150,
        "Price": 2850.25,
        "Time": datetime(2024, 12, 29, 16, 10),
        "Execution Price": 2852.00,
    },
    {
        "Symbol": "TSLA",
        "Action": "SELL",
        "Quantity": 100,
        "Price": 606.25,
        "Time": datetime(2024, 12, 29, 16, 30),
        "Execution Price": 607.00,
    },
    {
        "Symbol": "AAPL",
        "Action": "SELL",
        "Quantity": 100,
        "Price": 157.00,
        "Time": datetime(2024, 12, 29, 17, 0),
        "Execution Price": 157.50,
    },
]

# Aggregate trades and calculate total gains/losses for each symbol
symbol_data = defaultdict(
    lambda: {"buy_qty": 0, "buy_price": 0, "sell_qty": 0, "sell_price": 0}
)

for trade in mock_trades:
    symbol = trade["Symbol"]
    if trade["Action"] == "BUY":
        symbol_data[symbol]["buy_qty"] += trade["Quantity"]
        symbol_data[symbol]["buy_price"] += trade["Execution Price"] * trade["Quantity"]
    elif trade["Action"] == "SELL":
        symbol_data[symbol]["sell_qty"] += trade["Quantity"]
        symbol_data[symbol]["sell_price"] += (
            trade["Execution Price"] * trade["Quantity"]
        )

# Calculate average buy price and sell price, and profit/loss for each symbol
result = []
for symbol, data in symbol_data.items():
    if data["buy_qty"] > 0 and data["sell_qty"] > 0:
        avg_buy_price = data["buy_price"] / data["buy_qty"]
        avg_sell_price = data["sell_price"] / data["sell_qty"]
        total_profit_loss = (avg_sell_price - avg_buy_price) * min(
            data["buy_qty"], data["sell_qty"]
        )
        result.append(
            {
                "Symbol": symbol,
                "Total Quantity": min(data["buy_qty"], data["sell_qty"]),
                "Average Buy Price": avg_buy_price,
                "Average Sell Price": avg_sell_price,
                "Profit/Loss": total_profit_loss,
            }
        )

# Generate HTML table
html_content = """
<html>
<head>
    <title>Total Gains/Losses by Symbol</title>
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 8px;
            text-align: left;
            border: 1px solid #ddd;
        }
        th {
            background-color: #f2f2f2;
        }
    </style>
</head>
<body>
    <h2>Total Gains/Losses by Symbol</h2>
    <table>
        <thead>
            <tr>
                <th>Symbol</th>
                <th>Total Quantity</th>
                <th>Average Buy Price</th>
                <th>Average Sell Price</th>
                <th>Profit/Loss</th>
            </tr>
        </thead>
        <tbody>
"""

for entry in result:
    html_content += f"""
            <tr>
                <td>{entry['Symbol']}</td>
                <td>{entry['Total Quantity']}</td>
                <td>{entry['Average Buy Price']:.2f}</td>
                <td>{entry['Average Sell Price']:.2f}</td>
                <td>{entry['Profit/Loss']:.2f}</td>
            </tr>
    """

html_content += """
        </tbody>
    </table>
</body>
</html>
"""

# Save the HTML content to a file
with open("trading_report.html", "w") as file:
    file.write(html_content)

print("HTML report saved as 'trading_report.html'")
