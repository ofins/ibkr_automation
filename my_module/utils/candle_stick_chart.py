import os
from datetime import datetime

import plotly.graph_objects as go
import pytz


async def create_candle_chart(df):
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=df["time"],
                open=df["open"],
                high=df["high"],
                low=df["low"],
                close=df["close"],
                increasing_line_width=1,
                decreasing_line_width=1,
            )
        ]
    )

    fig.update_layout(
        title="3 min candles",
        xaxis_title="Time",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        autosize=True,
        margin=dict(l=0, r=0, t=30, b=0),
        yaxis=dict(showgrid=False, showline=True),
        xaxis=dict(showgrid=False, showline=True),
    )

    fig.update_traces(
        increasing_line_color="gray",
        decreasing_line_color="red",
        line_width=0.5,  # Thinner wicks
    )

    #     # Add sell (red arrow)
    # fig.add_trace(
    #     go.Scatter(
    #         x=[dates[sell_index]],
    #         y=[high_data[sell_index] + 0.2],  # Slightly above the candle
    #         mode="markers+text",
    #         marker=dict(color="red", size=12, symbol="triangle-down"),
    #         text=["SELL"],
    #         textposition="top center",
    #     )
    # )

    # # Update layout
    # fig.update_layout(
    #     title="Candlestick Chart with Buy/Sell Markers",
    #     xaxis_title="Date",
    #     yaxis_title="Price",
    #     xaxis_rangeslider_visible=False,
    # )

    ny_timezone = pytz.timezone("America/New_York")
    date_time = datetime.now(ny_timezone).strftime("%Y-%m-%d_%H-%M-%S")
    file_path = os.path.join(
        "dis/images", f"{date_time}.png").replace("\\", "/")
    fig.write_image(file_path)

    # fig.show()
    print(f"Chart saved to {file_path}")
    return file_path
