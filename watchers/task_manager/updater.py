from stocks.stockdata.wrapper import StockData
from ..models import Watcher
from .scheduler import send_email_async


def update_price(watcher):

    if not isinstance(watcher, Watcher):
        raise ValueError("Wrong argument type")

    stock = StockData(watcher.code)
    price = stock.get_last_price(watcher.interval)

    result = {"opportunity": False, "kind": None, "price": price}

    if price <= watcher.lower_threshold:
        result["opportunity"] = True
        result["kind"] = 1  # buy
    elif price >= watcher.upper_threshold:
        result["opportunity"] = True
        result["kind"] = -1  # sell

    return result


def price_updated(task):
    if task.result["opportunity"] is True:
        send_email_async(task.args[0], task.result)
