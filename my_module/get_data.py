from ib_insync import Contract


class GetData:

    @staticmethod
    async def get_live_data(ib, symbol):
        contract = Contract(
            symbol=symbol, secType="STK", exchange="SMART", currency="USD"
        )
        ib.qualifyContracts(contract)

        ticker = ib.reqMktData(contract, "", False, False)
        ib.sleep(2)

        price = ticker.last if ticker.last else ticker.close
        volume = ticker.volume

        return symbol, price, volume
