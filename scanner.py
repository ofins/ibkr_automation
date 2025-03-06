import pandas as pd
from ib_insync import *


class Scanner:

    @staticmethod
    async def get_top_gainers(ib):
        # Find top gainers with volume > 1M
        scanner = ScannerSubscription(
            instrument="STK",
            locationCode="STK.US.MAJOR",
            scanCode="TOP_PERC_GAIN",
            numberOfRows=10,
        )

        scanner.abovePrice = 1
        scanner.belowPrice = 50
        scanner.aboveVolume = 1000000

        scan_data = ib.reqScannerData(scanner)

        results = []

        # Compare today's volume with the average volume of the past 5 days
        for data in scan_data:
            # If stock already in results, skip.
            contract = data.contractDetails.contract
            symbol = contract.symbol
            pct_change = data.distance
            print(f"Processing {symbol} with {pct_change}% change")
            ticker = ib.reqMktData(contract, "", False, False)
            ib.sleep(1)
            current_volume = ticker.volume if ticker.volume != -1 else 0
            today_bars = ib.reqHistoricalData(
                contract,
                endDateTime="",
                durationStr="1 D",
                barSizeSetting="1 day",
                whatToShow="TRADES",
                useRTH=True,
                formatDate=1,
            )

            today_avg_volume = util.df(today_bars)["volume"].mean() if today_bars else 0
            print(today_avg_volume)

            past_bars = ib.reqHistoricalData(
                contract,
                endDateTime="20250306 05:00:00",
                durationStr="5 D",
                barSizeSetting="1 day",
                whatToShow="TRADES",
                useRTH=True,
                formatDate=1,
            )

            avg_volume = util.df(past_bars)["volume"].mean() if past_bars else 0
            print(avg_volume)

            volume_multiplier = today_avg_volume / avg_volume if avg_volume > 0 else 0
            if volume_multiplier > 2:
                # TODO: add indicators to check if stock is trending
                results.append(
                    {
                        "symbol": symbol,
                        "pct_change": pct_change,
                        "avg_volume": avg_volume,
                        "volume_multiplier": volume_multiplier,
                    }
                )

                # Execute bracket order for the stock

            # Repeat once every minute from 9:30 to 11:00

        df = pd.DataFrame(results)
        return df
