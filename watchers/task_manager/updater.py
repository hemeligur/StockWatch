from stocks.stockdata.wrapper import StockData
from ..models import Watcher
from .scheduler import send_email_async


def update_price(watcher_id):
    print(f"############-watchers.task_manager.updater.update_price-############ Got {watcher_id}, looking it up...")
    # There's a bug where you cant's pass a object as parameter, so we have to use the id and do a lookup
    # TODO: Considering changing it so it passes the watcher's fields as parameters
    watcher = Watcher.objects.get(pk=watcher_id)
    print(f"############-watchers.task_manager.updater.update_price-############ Updating price for {watcher}")

    stock = StockData(watcher.stock.code)
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
        watcher = Watcher.objects.get(pk=task.args[0])
        sent = send_email_async(watcher, task.result)
        print(f"############-watchers.task_manager.updater.update_price-############ Sent {sent} email(s)")
        # If the email was sent, you don't want to send the email again next interval
        # The watcher did it's job
        if sent == 1:
            watcher.remove_schedule()
