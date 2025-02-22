import os
from datetime import datetime, time

import plotly.graph_objects as go
import pytz

from my_module.utils.arg_parser import args


async def create_candle_chart(df, entry_price=None, stop_price=None, exit_price=None):
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

    # Plot indicators
    for indicator, color in [
        ("vwap", "blue"),
        ("vwap_upper", "gray"),
        ("vwap_lower", "gray"),
    ]:
        fig.add_trace(
            go.Scatter(
                x=df["time"],
                y=df[indicator],
                mode="lines",
                line=dict(color=color, width=1),
                name=indicator,
            )
        )

    # Fix x-axis
    trading_date = df["time"].iloc[0].date()
    trading_start = datetime.combine(trading_date, time(9, 30))
    trading_end = datetime.combine(trading_date, time(16, 0))

    fig.update_xaxes(
        range=[trading_start, trading_end],
        tickformat="%H:%M",
        showgrid=False,
    )

    # Add padding to top and bottom
    top = df["high_of_day"].max()
    bottom = df["low_of_day"].min()
    padding = (top - bottom) * 0.5
    fig.update_yaxes(
        range=[bottom - padding, top + padding],
        showgrid=False,
    )

    # Add price levels
    for price, color, label in [
        (entry_price, "green", "E"),
        (stop_price, "red", "S"),
        (exit_price, "blue", "P"),
    ]:
        if price is not None:
            fig.add_hline(
                y=price,
                line_dash="dot",
                line_color=color,
                annotation_text=f"{label} {price:.2f}",
                annotation_position="right",
                annotation=dict(
                    font_size=12,
                    font_color=color,
                    xref="x",  # Reference to full plot area
                    x=0.5,  # Center horizontally
                    xanchor="center",  # Center the text
                    yref="y",  # Reference to y-axis value
                    y=price,  # Match the line's y-position
                    yanchor="bottom",  # Place text above the line
                ),
            )

    fig.update_layout(
        yaxis2=dict(
            title="RSI",
            overlaying="y",  # Overlay on the main y-axis
            side="right",
            range=[0, 1],  # Scale RSI from 0 to 1
            showgrid=False,
            tickmode="array",
            tickvals=[0, 0.3, 0.5, 0.7, 1],  # Add ticks at key levels
        )
    )

    rsi_values = df["rsi"].copy() / 100
    valid_rsi = rsi_values.notna()

    fig.add_trace(
        go.Scatter(
            x=df.loc[valid_rsi, "time"],
            y=rsi_values[valid_rsi],
            mode="lines",
            line=dict(color="orange", width=1),
            name="RSI",
            yaxis="y2",  # Assign to secondary y-axis
            opacity=0.5,
        )
    )

    for level, label in [(0.7, "Overbought"), (0.3, "Oversold")]:
        fig.add_hline(
            y=level,
            line_dash="dash",
            line_color="yellow",
            annotation_text=label,
            annotation_position="right",
            annotation=dict(
                font_size=10,
                font_color="gray",
                xref="x",
                x=1.0,  # Align with the right side
                xanchor="right",
                yref="y2",  # Reference to RSI y-axis
                y=level,
                yanchor="bottom",
            ),
        )

    fig.update_layout(
        title=f"{args.symbol} | 3 min candles",
        xaxis_title="Time",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        # autosize=True,
        width=1000,
        height=700,
        margin=dict(l=0, r=0, t=30, b=0),
        yaxis=dict(showgrid=False, showline=True),
        xaxis=dict(showgrid=False, showline=True),
        showlegend=False,
    )

    fig.update_traces(
        selector=dict(type="candlestick"),
        increasing_line_color="gray",
        decreasing_line_color="red",
        line_width=0.5,  # Thinner wicks
    )

    ny_timezone = pytz.timezone("America/New_York")
    date_time = datetime.now(ny_timezone).strftime("%Y-%m-%d_%H-%M-%S")
    file_path = os.path.join("dist/images", f"{date_time}.png").replace("\\", "/")
    fig.write_image(file_path)

    # fig.show()
    print(f"Chart saved to {file_path}")
    return file_path
