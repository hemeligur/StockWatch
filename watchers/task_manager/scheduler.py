import arrow

from django_q.tasks import schedule
from django_q.models import Schedule

from stocks.stockdata.wrapper import API_VALID_INTERVALS, get_next_working_time


def create_schedule(watcher):
    config = _generate_config(watcher.interval)
    schedule_obj = schedule(
        'watchers.task_manager.updater.update_price',
        watcher.pk,
        schedule_type=config["schedule_type"],
        minutes=config["minutes"],
        repeats=-1,
        next_run=config["next_run"],
        hook='watchers.task_manager.updater.price_updated'
    )

    return schedule_obj.pk


def send_email_async(watcher, result):
    user = watcher.user
    kind_str = "COMPRA" if result["kind"] > 0 else "VENDA"
    price = result["price"]

    subject = "Alerta! Monitor de Ativos"
    msg = (f"Olá {user.username},\n\n"
           f"Seu monitor identificou uma oportunidade de {kind_str}"
           f" para o ativo {watcher.stock.code}({watcher.stock.name}),"
           f" com o preço de {price}."
           f"\n\n\t{kind_str}:\t{watcher.stock.code}\t[{price}]")

    return user.email_user(subject, msg, from_email=None)


def _generate_config(interval):
    idx = API_VALID_INTERVALS.index(interval)

    config = {
        'next_run': get_next_working_time(),
        'minutes': 1
    }

    # Python 3.7 does not have the match/case yet :(
    if idx <= 5:  # ["1m", "2m", "5m", "15m", "30m", "90m"]
        config["schedule_type"] = Schedule.MINUTES
        config["minutes"] = int(interval[:-1])

    elif idx <= 7:  # ["60m", "1h"]
        config["schedule_type"] = Schedule.HOURLY

    elif idx == 8:  # ["1d"]
        config["schedule_type"] = Schedule.DAILY

    elif idx == 9:  # ["5d"]
        config["schedule_type"] = Schedule.MINUTES
        config["minutes"] = 5 * 24 * 60

    elif idx == 10:  # ["1wk"]
        config["schedule_type"] = Schedule.WEEKLY

    elif idx == 11:  # ["1mo"]
        config["schedule_type"] = Schedule.MONTHLY

    elif idx == 12:  # ["3mo"]
        config["schedule_type"] = Schedule.QUARTERLY

    return config
