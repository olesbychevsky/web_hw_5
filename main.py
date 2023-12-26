import platform
import aiohttp, asyncio
from enum import Enum
import sys
from datetime import datetime, timedelta
import json
from pprint import pprint


class CurrencyEnum(Enum):
    USD = 'USD'
    EUR = 'EUR'
    CHF = 'CHF'
    GBP = 'GBP'
    PLZ = 'PLZ'
    SEK = 'SEK'
    XAU = 'XAU'
    CAD = 'CAD'


CURRENCIES = ["EUR", "USD"]
FILE_PATH = "currency_rate.json"
data_to_save = []


def get_date_period(period):
    days = int(period)
    if days < 1:
        new_days = 1
    elif 1 <= days <= 9:
        new_days = days
    elif days >= 10:
        new_days = days // 10
    elif days > 100:
        print(f'Too big data, try again (from 0 to 10)')
    today: datetime = datetime.today()
    return ([(today - timedelta(i)).strftime('%d.%m.%Y') for i in range(new_days)])


def searched_currencies(data, day):
    result_fin = []
    searching_currencies = [currencie for currencie in data["exchangeRate"] if currencie["currency"] in CURRENCIES]
    for currencie in searching_currencies:
        x = {
            day: {
                currencie["currency"]: {
                    "sale": currencie["saleRateNB"],
                    "purchase": currencie["purchaseRateNB"],
                }
            }
        }
        result_fin.append(x)

    data_to_save.extend(result_fin)

    return write_to_json(data_to_save)


def write_to_json(data):
    with open(FILE_PATH, "w") as fh:
        json.dump(data, fh, indent=4)


async def request(day):
    async with aiohttp.ClientSession() as session:
        async with session.get(
                f"https://api.privatbank.ua/p24api/exchange_rates?json&date={day}"
        ) as response:
            result = await response.json()
            return searched_currencies(result, day)


async def main(futures):
    await asyncio.gather(*futures)


if __name__ == "__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    period = sys.argv[-1]
    days = get_date_period(period)
    futures = [request(day) for day in days]
    asyncio.run(main(futures))
    pprint(data_to_save)
