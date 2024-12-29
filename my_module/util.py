from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

import pandas as pd

from my_module.logger import Logger

logger = Logger.get_logger(__name__)


def get_exit_time():
    est_time = ZoneInfo("America/New_York")
    now = datetime.now(est_time)
    # Holiday dates for 12:00 PM exit time
    holiday_dates = [(7, 3), (11, 26), (12, 24)]
    return time(12, 0) if (now.month, now.day) in holiday_dates else time(15, 0)


def export_to_excel(data, file_name):
    df = pd.DataFrame(data)

    try:
        df.to_excel(file_name, index=False)
        logger.info(f"Today's trades saved to {file_name}")
    except Exception as e:
        logger.error(f"Error saving trades to Excel: {e}")


def generate_html_table(trades):
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Trade Report</title>
        <style>
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                padding: 8px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }
            th {
                background-color: #f2f2f2;
            }
            tr:hover {
                background-color: #f1f1f1;
            }
        </style>
    </head>
    <body>
        <h2>Today's Trade Report</h2>
        <table>
            <thead>
                <tr>
                    <th>Symbol</th>
                    <th>Action</th>
                    <th>Quantity</th>
                    <th>Price</th>
                    <th>Time</th>
                    <th>Execution Price</th>
                </tr>
            </thead>
            <tbody>
    """

    for trade in trades:
        html_content += f"""
            <tr>
                <td>{trade['Symbol']}</td>
                <td>{trade['Action']}</td>
                <td>{trade['Quantity']}</td>
                <td>{trade['Price']}</td>
                <td>{trade['Time'].strftime('%Y-%m-%d %H:%M')}</td>
                <td>{trade['Execution Price']}</td>
            </tr>
        """

    html_content += """
            </tbody>
        </table>
    </body>
    </html>
    """

    # Write to HTML file
    with open("trade_report.html", "w") as file:
        file.write(html_content)

    print("HTML report has been generated successfully.")
