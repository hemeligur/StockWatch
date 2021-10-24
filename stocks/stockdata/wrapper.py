from django.utils import timezone
import arrow
import yfinance as yf
from statistics import mean

# https://www.guiainvest.com.br/lista-acoes/default.aspx?listaacaopesquisa=petrobras

API_VALID_INTERVALS = ["1m", "2m", "5m", "15m", "30m", "90m",
                       "60m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]
API_VALID_PERIODS = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]

# ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
# ["1m", "2m", "5m", "15m", "30m", "90m", "60m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]
#   0,     1,    2,    3,     4,     5,     6,     7,    8,    9,    10,    11,    12

B3_WORKING_HOURS = (9, 19)
DEFAULT_LOOKUP_TIME = mean(B3_WORKING_HOURS)


def is_working_day():
    weekday = arrow.now().weekday()
    if weekday >= 5:
        return False

    return True


def is_working_hours():
    now = arrow.now()

    start = now.replace(hour=B3_WORKING_HOURS[0], minute=0)
    end = now.replace(hour=B3_WORKING_HOURS[1], minute=0)

    if now.is_between(start, end):
        return True

    return False


def is_working_time():
    return is_working_day() and is_working_hours()


def get_next_working_time():
    now = next_work_time = arrow.now()
    changed = False
    if not is_working_day():
        next_work_time = next_work_time.shift(weekday=0)
        changed = True

    if not is_working_hours():
        # Now can be before opening or after closing
        next_work_time = next_work_time.replace(hour=DEFAULT_LOOKUP_TIME, minute=0, second=0)

        # If it's already past the default lookup time, we can assume now is after closing, next run is tomorrow
        if (next_work_time - now).days < 0:
            next_work_time = next_work_time.shift(days=1)
        changed = True

    if not changed:
        # If nothing is changed than set the next time to 1 minute in the future
        next_work_time = next_work_time.shift(minutes=1)

    return next_work_time.datetime


class StockData():
    ''' A simple interface for the yahoo finance API to decouple it from the rest of the system '''

    def __init__(self, code):
        self.code = code.upper()
        self.stock_data = yf.Ticker(self.code + ".SA")

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

    def get_last_price(self, interval="1m"):
        end_date = arrow.now()
        # minutes_to_shift = self._convert_interval(interval)
        start_date = end_date.shift(days=-3)
        hist = self.get_history(start_date=start_date.datetime, end_date=end_date.datetime, interval=interval)

        return hist['Close'][-1]

    def get_history(self, period="6mo", start_date=None, end_date=None, interval="1d", actions=False):

        # Validations
        validation = self._valid_interval(period, interval, start_date)
        if not validation[0]:
            raise ValueError(validation[1])

        if start_date is not None:
            end_date = end_date if end_date is not None else timezone.now()
            hist = self.stock_data.history(start=start_date, end=end_date, actions=actions)
        else:
            hist = self.stock_data.history(period=period, actions=actions)

        return hist

    def format_to_chart(self, hist):
        # Formating to return a list of lists in the format: label, low, open, close, high
        cols = hist.columns.tolist()
        cols = [cols[2]] + [cols[0]] + [cols[3]] + [cols[1]] + cols[4:]
        hist_mod = hist[cols]
        hist_mod = hist_mod[hist_mod.columns.tolist()[:4]]
        hist_list = [
            [i if idx != 0 else i.strftime("%Y-%m-%d") for idx, i in enumerate(row)]
            for row in hist_mod.itertuples()
        ]

        return hist_list

    def _valid_interval(self, period, interval, start_date):
        try:
            interval_idx = API_VALID_INTERVALS.index(interval)
            period_idx = API_VALID_PERIODS.index(period)

            error_message = (f"For interval {interval},"
                             f" the requested period must be within the last %d %s.")

            if start_date is None:
                if interval_idx <= 5 and period_idx > 2:
                    return (False, error_message % (60, 'days'))
                elif (interval_idx >= 6 and interval_idx <= 7) and period_idx > 6:
                    return (False, error_message % (2, 'years'))
            else:
                if interval_idx <= 5 and ((arrow.now() - start_date).days > 60):
                    return (False, error_message % (60, 'days'))
                elif (interval_idx >= 6 and interval_idx <= 7) and ((arrow.now() - start_date).days > (365 * 2)):
                    return (False, error_message % (2, 'years'))
        except ValueError as err:
            return (False, f"invalid interval and/or period: {err}")

        return (True, "")

    def _convert_interval(self, interval):
        idx = API_VALID_INTERVALS.index(interval)

        if idx <= 6:  # minutes
            minutes = int(interval[:-1])
        elif idx == 7:  # one hour
            minutes = 60
        elif idx <= 9:  # Days
            minutes = int(interval[:-1]) * 24 * 60
        elif idx == 10:  # week
            minutes = 7 * 24 * 60
        else:  # months
            minutes = int(interval[:-2]) * 30 * 24 * 60

        return minutes
