from django.utils import timezone
import arrow
import yfinance as yf
from statistics import mean

# TODO Criar um web scrapper usando essa URL como fonte de dados para a pesquisa tbm por nome do ativo
# https://www.guiainvest.com.br/lista-acoes/default.aspx?listaacaopesquisa=petrobras

API_VALID_INTERVALS = ["1m", "2m", "5m", "15m", "30m", "90m",
                       "60m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]
API_INTERVALS_VERBOSE = ["1 minuto", "2 minutos", "5 minutos", "15 minutos",
                         "30 minutos", "90 minutos", "60 minutos", "1 hora",
                         "1 dia", "5 dias", "1 semana", "1 mês", "3 meses"]
API_VALID_PERIODS = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
PERIOD_AUTO = "auto"

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
        # Now pode ser antes da abertura ou depois do fechamento
        next_work_time = next_work_time.replace(hour=DEFAULT_LOOKUP_TIME, minute=0, second=0)

        # Se já passou do horário padrão de lookup,
        # nós podemos assumir now é depois do fechamento, próxima execução é amanhã
        if (next_work_time - now).days < 0:
            next_work_time = next_work_time.shift(days=1)
        changed = True

    if not changed:
        # Se nada mudou então define o próximo horário para 1 minuto no futuro
        next_work_time = next_work_time.shift(minutes=1)

    return next_work_time.datetime


class StockData():
    ''' Simples interface para a yahoo finance API para desacoplar do resto do sistema '''

    def __init__(self, code, as_is=False):
        self.code = code.upper()

        if not as_is:
            self.code += ".SA"

        self.stock_data = yf.Ticker(self.code)

    def symbol_search(self, query):
        pass

    def get_info(self):
        info = self.stock_data.get_info()

        # "if all(key in dict for key in query)" é mais rápido que um try/except
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

        return (
            hist.index[-1].to_pydatetime(),
            [hist['Low'][-1], hist['Open'][-1], hist['Close'][-1], hist['High'][-1]]
        )

    def get_history(self, period="6mo", start_date=None, end_date=None, interval="1d",
                    actions=False, limit_dates=True):

        if period == PERIOD_AUTO:
            period = self._calc_period(interval)

        # Validations
        validation = self._valid_interval(period, interval, start_date)
        if not validation[0]:
            raise ValueError(validation[1])

        if start_date is not None:
            end_date = end_date if end_date is not None else timezone.now()
            hist = self.stock_data.history(start=start_date, end=end_date, interval=interval, actions=actions)
        else:
            hist = self.stock_data.history(period=period, interval=interval, actions=actions)

        if limit_dates is True:
            hist = hist.iloc[-150:]
        return hist

    def format_to_chart(self, hist):
        # Retorna uma lista de listas no formato: label, low, open, close, high
        cols = hist.columns.tolist()
        cols = [cols[2]] + [cols[0]] + [cols[3]] + [cols[1]] + cols[4:]
        hist_mod = hist[cols]
        hist_mod = hist_mod[hist_mod.columns.tolist()[:4]]

        # List Comprehension Bonanza!
        # Transforma o primeiro valor de pandas.Timestamp para string e monta a lista de listas.
        # Deve haver um jeito mais legível de fazer.
        # (Um monte de fors e ifs?)
        hist_list = [
            [i if idx != 0 else
             (i.strftime("%Y-%m-%d") if (i.hour == 0 and i.minute == 0) else i.strftime("%Y-%m-%d %H:%M"))
             for idx, i in enumerate(row)]
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

        if idx <= 6:  # minutos
            minutes = int(interval[:-1])
        elif idx == 7:  # uma hora
            minutes = 60
        elif idx <= 9:  # Dias
            minutes = int(interval[:-1]) * 24 * 60
        elif idx == 10:  # semana
            minutes = 7 * 24 * 60
        else:  # meses
            minutes = int(interval[:-2]) * 30 * 24 * 60

        return minutes

    def _calc_period(self, interval):
        interval_idx = API_VALID_INTERVALS.index(interval)

        if interval_idx == 0:
            hist_period = API_VALID_PERIODS[1]
        elif interval_idx <= 8:
            hist_period = API_VALID_PERIODS[2]
        elif interval_idx == 9:
            hist_period = API_VALID_PERIODS[3]
        elif interval_idx == 10:
            hist_period = API_VALID_PERIODS[4]
        elif interval_idx == 11:
            hist_period = API_VALID_PERIODS[6]
        elif interval_idx >= 12:
            hist_period = API_VALID_PERIODS[7]

        return hist_period
