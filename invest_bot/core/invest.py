from decimal import Decimal
from enum import Enum

from t_tech.invest import PortfolioResponse, MoneyValue, PortfolioPosition

from invest_bot.core.decorators import trace


def get_money(value: MoneyValue) -> Decimal:
    return Decimal(value.units) + Decimal(value.nano) / Decimal('1e9')


class InstrumentType(Enum):
    SHARE = "share"
    BOND = "bond"
    ETF = "etf"
    CURRENCY = "currency"


class Portfolio:
    _rub_ticker = "RUB000UTSTOM"
    _portfolio: PortfolioResponse
    _all_currency_positions: list[MoneyValue]
    _all_shares_positions: list[MoneyValue]
    _all_bonds_positions: list[MoneyValue]
    _all_etfs_positions: list[MoneyValue]

    def __init__(self, portfolio: PortfolioResponse):
        self._portfolio = portfolio
        self._all_currency_positions = self._get_all_currencies_positions(self, self._portfolio)
        self._all_shares_positions = self._get_all_positions(self._portfolio, InstrumentType.SHARE)
        self._all_bonds_positions = self._get_all_positions(self._portfolio, InstrumentType.BOND)
        self._all_etfs_positions = self._get_all_positions(self._portfolio, InstrumentType.ETF)
        self._free_money = self._get_free_currencies(self)

    def __repr__(self):
        return f"{self.__class__.__name__}"

    @trace
    def print_common_portfolio_info_str(self) -> str:
        return (
            f"Портфолио:\n"
            f"Акции - {get_money(self._portfolio.total_amount_shares)}\n"
            f"Облигации - {get_money(self._portfolio.total_amount_bonds)}\n"
            f"Фонды - {get_money(self._portfolio.total_amount_etf)}\n"
            f"Валюта и драгметалы - {get_money(self._portfolio.total_amount_currencies) - self._free_money}\n"
            f"Свободной валюты - {self._free_money}\n"
            f"Всего - {self._all_portfolio()}"
        )

    @trace
    def print_portfolio_structure_str(self) -> str:
        all_portfolio = self._all_portfolio()
        return (
            f"Процентное соотношение:\n"
            f"Акции - {self._get_percentage_from_element(get_money(self._portfolio.total_amount_shares),all_portfolio)}\n"
            f"Облигации - {self._get_percentage_from_element(get_money(self._portfolio.total_amount_bonds),all_portfolio)}\n"
            f"Фонды - {self._get_percentage_from_element(get_money(self._portfolio.total_amount_etf),all_portfolio)}\n"
            f"Валюта и драгметалы - {self._get_percentage_from_element(get_money(self._portfolio.total_amount_currencies),all_portfolio)}\n"
        )

    @trace
    def get_instrument_money(
        self, portfolio_positions: list[PortfolioPosition], ticker: str
    ) -> Decimal:
        for position in portfolio_positions:
            if position.ticker == ticker:
                current_price = get_money(position.current_price)
                quantity = get_money(position.quantity)
                return round(current_price * quantity, 2)
        return Decimal(-1)

    @staticmethod
    @trace
    def _get_percentage_from_element(element: Decimal, all_sum: Decimal) -> Decimal:
        return ((element / all_sum) * Decimal(100.00)).quantize(Decimal("1.00"))

    @staticmethod
    @trace
    def _get_all_positions(
        portfolio: PortfolioResponse, instrument_type: InstrumentType
    ) -> list[MoneyValue]:
        return [
            element
            for element in portfolio.positions
            if element.instrument_type == instrument_type.value
        ]

    @staticmethod
    @trace
    def _get_free_currencies(self) -> Decimal:
        free_money = [
            element
            for element in self._all_currency_positions
            if element.ticker == Portfolio._rub_ticker
        ][0].quantity
        return get_money(free_money)

    @staticmethod
    @trace
    def _get_all_currencies_positions(self, portfolio: PortfolioResponse):
        return self._get_all_positions(portfolio, InstrumentType.CURRENCY)

    @trace
    def _all_portfolio(self) -> Decimal:
        return Decimal(
            (
                get_money(self._portfolio.total_amount_bonds)
                + get_money(self._portfolio.total_amount_etf)
                + get_money(self._portfolio.total_amount_currencies)
                + get_money(self._portfolio.total_amount_shares)
            )
        )
