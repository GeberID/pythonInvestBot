from decimal import Decimal

from t_tech.invest import MoneyValue, Quotation

from investbot.core.log import write_log
from investbot.core.base_types import Money, Percentage


@write_log
def get_money(value: MoneyValue | Quotation) -> Money:
    return Money((Decimal(value.units) + Decimal(value.nano) / Decimal("1e9")).quantize(Decimal("0.00")))


@write_log
def get_percentage_from_element(element: Money, all_sum: Money) -> Percentage:
    return Percentage(((element / all_sum) * Decimal(100.00)).quantize(Decimal("0.00")))
