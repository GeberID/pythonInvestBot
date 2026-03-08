from decimal import Decimal

from invest_bot.core.log import write_log


@write_log
def get_money(value) -> Decimal:
    return Decimal(value.units) + Decimal(value.nano) / Decimal('1e9')


@write_log
def get_percentage_from_element(element: Decimal, all_sum: Decimal) -> Decimal:
    return ((element / all_sum) * Decimal(100.00)).quantize(Decimal("1.00"))
