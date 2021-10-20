from django.utils import timezone
import arrow

from django_q.tasks import schedule
from django_q.models import Schedule

from watchers.models import Watcher
from stocks.stockdata.wrapper import API_VALID_INTERVALS, is_working_hours


def create_schedule(watcher):
    if not isinstance(watcher, Watcher):
        raise ValueError(f"Wrong argument type: expected {Watcher}, got {type(watcher)}")

    config = _generate_config(watcher.interval)
    schedule_id = schedule(
        '.updater.update_price',
        watcher,
        schedule_type=config["schedule_type"],
        minutes=config["minutes"],
        repeats=-1,
        next_run=config["next_run"],
        hook='.update.price_updated'
    )

    return schedule_id


def send_email_async(watcher, result):
    if not isinstance(watcher, Watcher):
        raise ValueError(f"Wrong argument type: expected {Watcher}, got {type(watcher)}")

    user = watcher.user
    kind_str = "COMPRA" if result["kind"] > 0 else "VENDA"
    price = result["price"]

    subject = "Alerta! Monitor de Ativos"
    msg = f"Olá {user.username}\n\n,"
    f"Seu monitor identificou uma oportunidade de {kind_str}"
    f" para o ativo {watcher.stock.code}({watcher.stock.name}),"
    f" com o preço de {price}."
    f"\n\n\t{kind_str}:\t{watcher.stock.code}\t[{price}]"

    user.email_user(subject, msg, from_email=None)


def _generate_config(interval):
    idx = API_VALID_INTERVALS.index(interval)

    config = {
        'next_run': arrow.now().shift(minutes=1),
        'minutes': 1
    }

    # Python 3.7 does not have the match/case yet :(
    if idx <= 5:
        config["schedule_type"] = Schedule.MINUTES
        config["minutes"] = int(interval[:-1])

    elif idx <= 7:
        config["schedule_type"] = Schedule.HOURLY

    elif idx == 8:
        config["schedule_type"] = Schedule.DAILY

        if not is_working_hours():
            now = arrow.now()
            config["next_run"] = now.replace(hour=14, minute=0)

            if (config["next_run"] - now).days < 0:
                config["next_run"] = config["next_run"].shift(days=1)

    elif idx == 9:
        config["schedule_type"] = Schedule.MINUTES
        config["minutes"] = 5 * 24 * 60
        now = arrow.now()
        config["next_run"] = now.replace(hour=14, minute=0)

        if now.hours > 14 or (now.hours == 14 and now.minutes > 0):
            config["next_run"] = config["next_run"].shift(days=1)

    elif idx == 10:
        config["schedule_type"] = Schedule.WEEKLY
        now = arrow.now()

        if now.weekday() == 0 or now.weekday() == 6:
            config["next_run"] = now.shift(weekday=1)

    elif idx == 11:
        config["schedule_type"] = Schedule.MONTHLY

    elif idx == 12:
        config["schedule_type"] = Schedule.QUARTERLY

    return config
