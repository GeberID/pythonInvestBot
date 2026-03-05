from decimal import Decimal
from enum import Enum

from t_tech.invest import PortfolioResponse, PortfolioPosition

from invest_bot.api import tinkoff_api as api
from invest_bot.core.logs import log
from invest_bot.core.money_utilities import get_money, get_percentage_from_element

RUB_TICKER = "RUB000UTSTOM"
ETF_CORE_TICKER = "EQMX"


class InstrumentType(Enum):
    SHARE = "share"
    BOND = "bond"
    ETF = "etf"
    CURRENCY = "currency"


class InvestPortfolio:
    account_id: str
    portfolio: PortfolioResponse
    positions: dict[InstrumentType, list[PortfolioPosition]]
    positions_amt: dict[InstrumentType, Decimal]
    free_money: Decimal

    def __init__(self, account_id: str):
        self.portfolio = api.get_portfolio(account_id)
        self.positions = {
            InstrumentType.SHARE: self._get_positions(InstrumentType.SHARE),
            InstrumentType.BOND: self._get_positions(InstrumentType.BOND),
            InstrumentType.ETF: self._get_positions(InstrumentType.ETF),
            InstrumentType.CURRENCY: self._get_positions(InstrumentType.CURRENCY),
        }
        self.positions_amt = {
            InstrumentType.SHARE: get_money(self.portfolio.total_amount_shares),
            InstrumentType.BOND: get_money(self.portfolio.total_amount_bonds),
            InstrumentType.ETF: get_money(self.portfolio.total_amount_etf),
            InstrumentType.CURRENCY: get_money(self.portfolio.total_amount_currencies),
        }
        self.update_free_money()

    def __repr__(self):
        return f"{self.__class__.__name__}"

    @log
    def print_common_info_str(self) -> str:
        shares = self.positions_amt.get(InstrumentType.SHARE)
        bonds = self.positions_amt.get(InstrumentType.BOND)
        currencies = self.positions_amt.get(InstrumentType.CURRENCY) - self.free_money
        etf_shares = self.get_instrument_money(self.positions[InstrumentType.ETF], ETF_CORE_TICKER)
        other_etf = self.positions_amt.get(InstrumentType.ETF) - etf_shares
        return (
            f"Портфолио:\n"
            f"Акции - {shares:,.2f} ₽\n"
            f"Облигации - {bonds:,.2f} ₽\n"
            f"Фонды акций- {etf_shares:,.2f} ₽\n"
            f"Остальные Фонды - {other_etf:,.2f} ₽\n"
            f"Валюта и драгметалы - {currencies:,.2f} ₽\n"
            f"Свободной валюты - {self.free_money:,.2f} ₽\n"
            f"------------------------------\n"
            f"Всего - {self._all_portfolio_money():,.2f} ₽"
        )

    @log
    def print_persent_structure_str(self) -> str:
        all_portfolio = self._all_portfolio_money()
        return (
            f"Процентное соотношение:\n"
            f"Акции - {get_percentage_from_element(self.positions_amt.get(InstrumentType.SHARE), all_portfolio)}\n"
            f"Облигации - {get_percentage_from_element(self.positions_amt.get(InstrumentType.BOND), all_portfolio)}\n"
            f"Фонды - {get_percentage_from_element(self.positions_amt.get(InstrumentType.ETF), all_portfolio)}\n"
            f"Валюта и драгметалы - {get_percentage_from_element(self.positions_amt.get(InstrumentType.CURRENCY), all_portfolio)}\n"
        )

    @log
    def print_all_shares(self) -> str:
        shares_data = [
            (position.ticker, get_money(position.current_price) * get_money(position.quantity), position.daily_yield)
            for position in self.positions.get(InstrumentType.SHARE)
        ]
        shares_data.sort(key=lambda x: x[1], reverse=True)
        lines = [f"<code>{t:<12}</code> | {amt:,.2f} ₽" for t, amt, daily_yield in shares_data]
        return "<b>Акции</b>\n" + "\n".join(lines)

    @log
    def print_all_bonds(self) -> str:
        bonds_data = [
            (
                position.ticker,
                get_money(position.current_price) * get_money(position.quantity),
                position.current_nkd,
                position.daily_yield,
            )
            for position in self.positions.get(InstrumentType.BOND)
        ]
        bonds_data.sort(key=lambda x: x[1], reverse=True)
        lines = [
            f"<code>{t:12}</code> | {amt:>9,.0f} ₽ | {get_money(nkd):>6.2f} ₽"
            for t, amt, nkd, daily_yield in bonds_data
        ]
        header = (
            "<b>Облигации</b>\n"
            "<code>ISIN         |  СУММА   |  НКД  </code>\n"
            "<code>-------------|----------|-------</code>"
        )
        return header + "\n" + "\n".join(lines)

    @log
    def get_instrument_money(self, positions: list[PortfolioPosition], ticker: str) -> Decimal:
        for position in positions:
            if position.ticker == ticker:
                current_price = get_money(position.current_price)
                quantity = get_money(position.quantity)
                return current_price * quantity
        return Decimal(-1)

    @log
    def update_free_money(self) -> None:
        temp_free_money = [
            element for element in self.positions.get(InstrumentType.CURRENCY) if element.ticker == RUB_TICKER
        ][0].quantity
        self.free_money = get_money(temp_free_money)

    @log
    def _get_positions(self, instrument_type: InstrumentType) -> list[PortfolioPosition]:
        return [p for p in self.portfolio.positions if p.instrument_type == instrument_type.value]

    @log
    def _all_portfolio_money(self) -> Decimal:
        return Decimal(
            (
                get_money(self.portfolio.total_amount_bonds)
                + get_money(self.portfolio.total_amount_etf)
                + get_money(self.portfolio.total_amount_currencies)
                + get_money(self.portfolio.total_amount_shares)
            )
        )
