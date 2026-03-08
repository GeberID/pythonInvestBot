from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import Final, TypeVar, DefaultDict

from t_tech.invest import PortfolioResponse, PortfolioPosition, MoneyValue

from invest_bot.api import tinkoff_api as api
from invest_bot.core.log import write_log
from invest_bot.core.money_utilities import get_money, get_percentage_from_element

RUB_TICKER: Final = "RUB000UTSTOM"
ETF_CORE_TICKER: Final = "EQMX"


class InstrumentType(StrEnum):
    SHARE = "share"
    BOND = "bond"
    ETF = "etf"
    CURRENCY = "currency"


@dataclass
class SharesData:
    ticker: str
    money: Decimal
    daily_yield: Decimal
    all_yield: Decimal

    def __str__(self):
        return (
            f"<code>{self.ticker:<6}</code> |"
            f"{self.money:,.2f} ₽ | "
            f"{self.daily_yield:,.2f} ₽ | "
            f"{self.all_yield:,.2f} ₽"
        )


@dataclass
class BondData:
    ticker: str
    money: Decimal
    nkd: Decimal
    daily_yield: Decimal

    def __str__(self) -> str:
        return f"<code>{self.ticker:12}</code> |" + f",{self.money:>9,.0f} ₽ |" + f"{self.nkd:>6.2f} ₽"


class InvestPortfolio:
    position_data = TypeVar('position_data')
    account_id: str
    portfolio: PortfolioResponse
    positions: dict[InstrumentType, list[PortfolioPosition]]
    positions_amt: DefaultDict[InstrumentType, Decimal] = defaultdict(Decimal)
    free_money: Decimal

    def __init__(self, portfolio: PortfolioResponse):
        self.portfolio = portfolio
        self.positions: dict[InstrumentType, list[PortfolioPosition]] = {t: [] for t in InstrumentType}
        for p in self.portfolio.positions:
            try:
                p_type = InstrumentType(p.instrument_type)
                self.positions[p_type].append(p)
            except ValueError:
                continue
        self.positions_amt[InstrumentType.SHARE] = get_money(self.portfolio.total_amount_shares)
        self.positions_amt[InstrumentType.BOND] = get_money(self.portfolio.total_amount_bonds)
        self.positions_amt[InstrumentType.ETF] = get_money(self.portfolio.total_amount_etf)
        self.positions_amt[InstrumentType.CURRENCY] = get_money(self.portfolio.total_amount_currencies)
        self.update_free_money()

    def __repr__(self):
        return f"{self.__class__.__name__}"

    @write_log
    def print_common_info_str(self) -> str:
        shares = self.positions_amt.get(InstrumentType.SHARE)
        bonds = self.positions_amt.get(InstrumentType.BOND)
        currencies = self.positions_amt.get(InstrumentType.CURRENCY)
        etf_shares = self.get_instrument_money(self.positions[InstrumentType.ETF], ETF_CORE_TICKER)
        other_etf = self.positions_amt.get(InstrumentType.ETF) - etf_shares
        return (
            f"Портфолио:\n"
            f"Акции - {shares:,.2f} ₽\n"
            f"Облигации - {bonds:,.2f} ₽\n"
            f"Фонды акций- {etf_shares:,.2f} ₽\n"
            f"Остальные Фонды - {other_etf:,.2f} ₽\n"
            f"Валюта и драгметалы - {currencies  - self.free_money:,.2f} ₽\n"
            f"Свободной валюты - {self.free_money:,.2f} ₽\n"
            f"------------------------------\n"
            f"Всего - {self._all_portfolio_money():,.2f} ₽"
        )

    @write_log
    def print_persent_structure_str(self) -> str:
        all_portfolio = self._all_portfolio_money()
        return (
            f"Процентное соотношение:\n"
            f"Акции - {get_percentage_from_element(self.positions_amt.get(InstrumentType.SHARE), all_portfolio)}\n"
            f"Облигации - {get_percentage_from_element(self.positions_amt.get(InstrumentType.BOND), all_portfolio)}\n"
            f"Фонды - {get_percentage_from_element(self.positions_amt.get(InstrumentType.ETF), all_portfolio)}\n"
            f"Валюта и драгметалы - {get_percentage_from_element(self.positions_amt.get(InstrumentType.CURRENCY), all_portfolio)}\n"
        )

    @write_log
    def print_all_shares(self) -> str:
        shares_data: list[SharesData] = [
            SharesData(
                ticker=position.ticker,
                money=get_money(position.current_price) * get_money(position.quantity),
                daily_yield=get_money(position.daily_yield),
                all_yield=get_money(position.expected_yield),
            )
            for position in self.positions.get(InstrumentType.SHARE)
        ]
        header = (
            "<b>Акции</b>\n"
            "<code>ISIN | СУММА |ИЗМЕНЕНИЯ ЗА ДЕНЬ|ЗА ВСЕ ВРЕМЯ</code>\n"
            "<code>-----|-----------|-----------------|------------</code>"
        )
        return self._get_all_positions_str(shares_data, header)

    @write_log
    def print_all_bonds(self) -> str:
        bonds_data: list[BondData] = [
            BondData(
                ticker=position.ticker,
                money=get_money(position.current_price) * get_money(position.quantity),
                nkd=get_money(position.current_nkd),
                daily_yield=get_money(position.daily_yield),
            )
            for position in self.positions.get(InstrumentType.BOND)
        ]
        header = (
            "<b>Облигации</b>\n"
            "<code>ISIN         |  СУММА   |  НКД  </code>\n"
            "<code>-------------|----------|-------</code>"
        )
        return self._get_all_positions_str(bonds_data, header)

    @write_log
    def get_instrument_money(self, positions: list[PortfolioPosition], ticker: str) -> Decimal:
        for position in positions:
            if position.ticker == ticker:
                current_price = get_money(position.current_price)
                quantity = get_money(position.quantity)
                return current_price * quantity
        return Decimal(-1)

    @write_log
    def update_free_money(self) -> None:
        temp_free_money = [
            element for element in self.positions.get(InstrumentType.CURRENCY) if element.ticker == RUB_TICKER
        ][0].quantity
        self.free_money = get_money(temp_free_money)

    @write_log
    def _get_all_positions_str(self, list_positions: list[position_data], header: str) -> str:
        body = "\n".join(str(position) for position in list_positions)
        return f"{header}\n{body}"

    @write_log
    def _all_portfolio_money(self) -> Decimal:
        return Decimal(
            (
                get_money(self.portfolio.total_amount_bonds)
                + get_money(self.portfolio.total_amount_etf)
                + get_money(self.portfolio.total_amount_currencies)
                + get_money(self.portfolio.total_amount_shares)
            )
        )
