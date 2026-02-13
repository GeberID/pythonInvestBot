from decimal import Decimal

from t_tech.invest import MoneyValue

from invest_bot.core.decorators import trace


@trace
def get_money(value: MoneyValue) -> Decimal:
    return Decimal(value.units) + Decimal(value.nano) / Decimal('1e9')


@trace
def get_percentage_from_element(element: Decimal, all_sum: Decimal) -> Decimal:
    return ((element / all_sum) * Decimal(100.00)).quantize(Decimal("1.00"))
