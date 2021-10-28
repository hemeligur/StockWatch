from stocks.stockdata.wrapper import StockData, is_working_time, get_next_working_time
from django_q.models import Schedule
from ..models import Watcher
from .scheduler import send_email_async


def update_price(watcher_id):
    # There's a bug where you cant's pass an object as parameter, so we have to use the id and do a lookup
    # TODO: Consider changing it so it passes the watcher's fields as parameters instead
    watcher = Watcher.objects.get(pk=watcher_id)

    result = {"opportunity": False, "kind": None, "price": None}

    if not is_working_time():
        schedule = Schedule.objects.get(pk=watcher.schedule_id)
        schedule.next_run = get_next_working_time()
        schedule.save(update_fields=["next_run"])

        return result

    stock = StockData(watcher.stock_id)
    result["price"] = stock.get_last_price(watcher.interval)[1][2]

    if result["price"] <= watcher.lower_threshold:
        result["opportunity"] = True
        result["kind"] = 1  # buy
    elif result["price"] >= watcher.upper_threshold:
        result["opportunity"] = True
        result["kind"] = -1  # sell

    return result


def price_updated(task):
    if task.result["opportunity"] is True:
        watcher = Watcher.objects.get(pk=task.args[0])
        sent = send_email_async(watcher, task.result)

        # If the email was sent, you don't want to send the email again next interval
        # The watcher did it's job
        if sent == 1:
            watcher.set_active(False)
