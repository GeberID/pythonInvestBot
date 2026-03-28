from decimal import Decimal

from t_tech.invest import MoneyValue, Quotation

from core.log import write_log


@write_log
def get_money(value: MoneyValue | Quotation) -> Decimal:
    return (Decimal(value.units) + Decimal(value.nano) / Decimal("1e9")).quantize(Decimal("0.00"))


@write_log
def get_percentage_from_element(element: Decimal, all_sum: Decimal) -> Decimal:
    return ((element / all_sum) * Decimal(100.00)).quantize(Decimal("0.00"))
