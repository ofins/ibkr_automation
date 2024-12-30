import os
from collections import defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo

import plotly.graph_objects as go
from jinja2 import Template

from my_module.logger import Logger

logger = Logger.get_logger(__name__)


def create_waterfall_chart(symbol_data):
    """Create a waterfall chart for a single symbol's trades"""
    active_trades = sorted(symbol_data, key=lambda x: x["Time"])

    times = []
    measures = []
    values = []
    running_total = 0

    times.append(active_trades[0]["Time"])
    measures.append("relative")
    values.append(0)

    for trade in active_trades:
        if trade["Realized PNL"] != 0:
            times.append(trade["Time"])
            measures.append("relative")
            values.append(trade["Realized PNL"])
            running_total += trade["Realized PNL"]

    if values:
        times.append("Total")
        measures.append("total")
        values.append(running_total)

    fig = go.Figure(
        go.Waterfall(
            x=times,
            measure=measures,
            y=values,
            decreasing={"marker": {"color": "red"}},
            increasing={"marker": {"color": "green"}},
            totals={"marker": {"color": "gray"}},
            connector={"line": {"color": "black", "width": 1}},
        )
    )

    fig.update_layout(
        title=f"Realized PNL Over Time for {symbol_data[0]['Symbol']}",
        xaxis_title="Time",
        yaxis_title="PNL Amount",
        showlegend=False,
        xaxis={"tickangle": 45, "tickformat": "%Y-%m-%d %H:%M"},
    )

    return fig.to_json()


def generate_html(data):
    today_date = datetime.now().astimezone(ZoneInfo("America/New_York")).date()

    # Group trades by symbol
    symbol_trades = defaultdict(list)
    total_pnl = 0

    for trade in data:
        symbol_trades[trade["Symbol"]].append(trade)
        total_pnl += trade["Realized PNL"]

    # Calculate total PNL for each symbol
    symbol_totals = {
        symbol: sum(trade["Realized PNL"] for trade in trades)
        for symbol, trades in symbol_trades.items()
    }

    # Create waterfall charts
    charts_json = {
        symbol: create_waterfall_chart(trades)
        for symbol, trades in symbol_trades.items()
        if any(trade["Realized PNL"] != 0 for trade in trades)
    }

    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Trade Data Report - {{ today_date }}</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {
                padding: 20px;
                font-family: Arial, sans-serif;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                font-size: 16px;
                text-align: left;
            }
            table th, table td {
                border: 1px solid #ddd;
                padding: 12px 8px;
            }
            table th {
                background-color: #f2f2f2;
            }
            .chart-container {
                width: 100%;
                max-width: 1000px;
                height: 500px;
                margin: 20px 0;
            }
            .negative-pnl {
                background-color: #ffeded;
                color: #d32f2f;
            }
            .symbol-section {
                margin-bottom: 40px;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
            .symbol-header {
                background-color: #f8f9fa;
                padding: 10px;
                margin: -20px -20px 20px -20px;
                border-radius: 8px 8px 0 0;
                border-bottom: 1px solid #ddd;
            }
            .total-row {
                font-weight: bold;
                background-color: #f8f9fa;
            }
            .grand-total {
                margin-top: 30px;
                font-size: 1.2em;
                padding: 15px;
                background-color: #f8f9fa;
                border-radius: 4px;
                text-align: right;
            }
        </style>
    </head>
    <body>
        <h1>Trade Data Report - {{ today_date }}</h1>
        
        {% for symbol, trades in symbol_trades.items() %}
        <div class="symbol-section">
            <div class="symbol-header">
                <h2>{{ symbol }} Trades</h2>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Action</th>
                        <th>Quantity</th>
                        <th>Price</th>
                        <th>Time</th>
                        <th>Execution Price</th>
                        <th>Realized PNL</th>
                    </tr>
                </thead>
                <tbody>
                    {% for trade in trades | sort(attribute='Time') %}
                    <tr>
                        <td>{{ trade['Action'] }}</td>
                        <td>{{ trade['Quantity'] }}</td>
                        <td>{{ "%.2f"|format(trade['Price']) }}</td>
                        <td>{{ trade['Time'] }}</td>
                        <td>{{ "%.2f"|format(trade['Execution Price']) }}</td>
                        <td class="{{ 'negative-pnl' if trade['Realized PNL'] < 0 }}">
                            {{ "%.2f"|format(trade['Realized PNL']) }}
                        </td>
                    </tr>
                    {% endfor %}
                    <tr class="total-row">
                        <td colspan="5">Total {{ symbol }}</td>
                        <td class="{{ 'negative-pnl' if symbol_totals[symbol] < 0 }}">
                            {{ "%.2f"|format(symbol_totals[symbol]) }}
                        </td>
                    </tr>
                </tbody>
            </table>
            
            {% if symbol in charts %}
            <div id="chart_{{ symbol }}" class="chart-container"></div>
            <script>
                const chartData_{{ symbol }} = {{ charts[symbol] | safe }};
                Plotly.newPlot('chart_{{ symbol }}', chartData_{{ symbol }}.data, chartData_{{ symbol }}.layout);
            </script>
            {% endif %}
        </div>
        {% endfor %}
        
        <div class="grand-total">
            <strong>Total Combined Realized PNL: 
                <span class="{{ 'negative-pnl' if total_pnl < 0 }}">
                    {{ "%.2f"|format(total_pnl) }}
                </span>
            </strong>
        </div>
    </body>
    </html>
    """

    # Render HTML
    template = Template(html_template)
    rendered_html = template.render(
        symbol_trades=symbol_trades,
        charts=charts_json,
        today_date=today_date,
        symbol_totals=symbol_totals,
        total_pnl=total_pnl,
    )

    # Ensure the 'dist' folder exists
    os.makedirs("dist", exist_ok=True)

    # Define the output file path
    output_file = os.path.join("dist", f"{today_date}.html")

    # Write the HTML content to the file
    with open(output_file, "w") as file:
        file.write(rendered_html)

    logger.info(f"HTML report generated: {output_file}")
