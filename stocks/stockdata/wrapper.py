from django.utils import timezone
import yfinance as yf

# https://www.guiainvest.com.br/lista-acoes/default.aspx?listaacaopesquisa=petrobras

API_VALID_INTERVALS = ["1m", "2m", "5m", "15m", "30m", "90m",
                       "60m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]
API_VALID_PERIODS = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]


class StockData():
    ''' A simple interface for the yahoo finance API to decouple it from the rest of the system '''

    def __init__(self, code):
        self.code = code
        self.stock_data = yf.Ticker(self.code + ".SA")

    def _valid_interval(self, period, interval):
        try:
            interval_idx = API_VALID_INTERVALS.index(interval)
            period_idx = API_VALID_PERIODS.index(period)

            error_message = (f"For interval {interval},"
                             f" the requested period must be within the last %d %s.")

            if interval_idx <= 5 and period_idx > 2:
                return (False, error_message % (60, 'days'))
            elif interval_idx >= 6 and interval_idx <= 7 and period_idx > 6:
                return (False, error_message % (2, 'years'))
        except ValueError as err:
            # TODO
            return (False, f"invalid interval and/or period: {err}")

        return (True, "")

    def symbol_search(self, query):
        pass

    def get_info(self):
        info = self.stock_data.get_info()

        # "if all(key in dict for key in query)" is faster than a try/except
        if all(k in info for k in ('symbol', 'longName', 'currentPrice')):
            return {
                'code': info['symbol'],
                'name': info['longName'],
                'current_price': info['currentPrice']
            }
        else:
            return None

    def get_last_price(self):
        hist = self.get_history(period=API_VALID_PERIODS[0], interval=API_VALID_INTERVALS[0])

        return hist['Close'][0]

    def get_history(self, period="6mo", start_date=None, end_date=None, interval="1d"):

        # Validations
        validation = self._valid_interval(period, interval)
        if not validation[0]:
            raise ValueError(validation[1])

        if start_date is not None:
            end_date = end_date if end_date is not None else timezone.now()
            history = self.stock_data.history(start=start_date, end=end_date)
        else:
            history = self.stock_data.history(period=period)

        return history
