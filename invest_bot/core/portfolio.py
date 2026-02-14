from decimal import Decimal
from enum import Enum

from t_tech.invest import PortfolioResponse, MoneyValue, PortfolioPosition

from invest_bot.core.decorators import trace
from invest_bot.core.money_utilities import get_money, get_percentage_from_element

RUB_TICKER = "RUB000UTSTOM"


class InstrumentType(Enum):
    SHARE = "share"
    BOND = "bond"
    ETF = "etf"
    CURRENCY = "currency"


class Portfolio:
    _portfolio: PortfolioResponse

    _all_currency_positions: list[PortfolioPosition]
    _all_shares_positions: list[PortfolioPosition]
    _all_bonds_positions: list[PortfolioPosition]
    _all_etfs_positions: list[PortfolioPosition]

    _free_money: Decimal

    _shares_amt: Decimal
    _bonds_amt: Decimal
    _etf_amt: Decimal
    _currencies_amt: Decimal

    def __init__(self, portfolio: PortfolioResponse):
        self._portfolio = portfolio

        self._all_currency_positions = self._get_all_currencies_positions()
        self._all_shares_positions = self._get_all_positions(InstrumentType.SHARE)
        self._all_bonds_positions = self._get_all_positions(InstrumentType.BOND)
        self._all_etfs_positions = self._get_all_positions(InstrumentType.ETF)
        self._free_money = self._update_free_money()

        self._shares_amt = get_money(portfolio.total_amount_shares)
        self._bonds_amt = get_money(portfolio.total_amount_bonds)
        self._etf_amt = get_money(portfolio.total_amount_etf)
        self._currencies_amt = get_money(portfolio.total_amount_currencies)

    def __repr__(self):
        return f"{self.__class__.__name__}"

    @trace
    def print_common_info_str(self) -> str:
        return (
            f"Портфолио:\n"
            f"Акции - {self._shares_amt:,.2f} ₽\n"
            f"Облигации - {self._bonds_amt:,.2f} ₽\n"
            f"Фонды - {self._etf_amt:,.2f} ₽\n"
            f"Валюта и драгметалы - {self._currencies_amt - self._free_money:,.2f} ₽\n"
            f"Свободной валюты - {self._free_money:,.2f} ₽\n"
            f"------------------------------\n"
            f"Всего - {self._all_portfolio_money():,.2f} ₽"
        )

    @trace
    def print_persent_structure_str(self) -> str:
        all_portfolio = self._all_portfolio_money()
        return (
            f"Процентное соотношение:\n"
            f"Акции - {get_percentage_from_element(self._shares_amt,all_portfolio)}\n"
            f"Облигации - {get_percentage_from_element(self._bonds_amt,all_portfolio)}\n"
            f"Фонды - {get_percentage_from_element(self._etf_amt,all_portfolio)}\n"
            f"Валюта и драгметалы - {get_percentage_from_element(self._currencies_amt,all_portfolio)}\n"
        )

    @trace
    def print_all_shares(self):
        shares_data = [
            (position.ticker, get_money(position.current_price) * get_money(position.quantity))
            for position in self._all_shares_positions
        ]
        shares_data.sort(key=lambda x: x[1], reverse=True)
        lines = [f"<code>{t:<6}</code> — {amt:,.2f} ₽" for t, amt in shares_data]
        return "Акции\n" + "\n".join(lines)

    @trace
    def print_all_bonds(self):
        bonds_data = [
            (position.ticker, get_money(position.current_price) * get_money(position.quantity), position.current_nkd)
            for position in self._all_bonds_positions
        ]
        bonds_data.sort(key=lambda x: x[1], reverse=True)
        lines = [f"<code>{t:<6}</code> — {amt:,.2f} ₽ - Нкд: {get_money(nkd):,.2f}" for t, amt, nkd in bonds_data]
        return "Облигации\n" + "\n".join(lines)

    @trace
    def get_instrument_money(self, positions: list[PortfolioPosition], ticker: str) -> Decimal:
        for position in positions:
            if position.ticker == ticker:
                current_price = get_money(position.current_price)
                quantity = get_money(position.quantity)
                return current_price * quantity
        return Decimal(-1)

    @trace
    def _update_free_money(self) -> Decimal:
        free_money = [element for element in self._all_currency_positions if element.ticker == RUB_TICKER][0].quantity
        return get_money(free_money)

    @trace
    def _get_all_positions(self, instrument_type: InstrumentType) -> list[PortfolioPosition]:
        return [p for p in self._portfolio.positions if p.instrument_type == instrument_type.value]

    @trace
    def _get_all_currencies_positions(self) -> list[PortfolioPosition]:
        return self._get_all_positions(InstrumentType.CURRENCY)

    @trace
    def _all_portfolio_money(self) -> Decimal:
        return Decimal(
            (
                get_money(self._portfolio.total_amount_bonds)
                + get_money(self._portfolio.total_amount_etf)
                + get_money(self._portfolio.total_amount_currencies)
                + get_money(self._portfolio.total_amount_shares)
            )
        )
