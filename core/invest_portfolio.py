from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import TypeVar, DefaultDict

from t_tech.invest import PortfolioResponse, PortfolioPosition

from configs import RUB_TICKER, ETF_CORE_TICKER, BOND_FIX, BOND_FLOATER, BOND_LINKER
from core.log import write_log
from core.money_utilities import get_money, get_percentage_from_element

Position_data = TypeVar("Position_data")


class InstrumentType(StrEnum):
    SHARE = "share"
    BOND = "bond"
    ETF = "etf"
    CURRENCY = "currency"


class BondType(StrEnum):
    FIX = BOND_FIX
    FLOATER = BOND_FLOATER
    LINKER = BOND_LINKER


@dataclass(frozen=True)
class ShareData:
    ticker: str
    money: Decimal
    daily_yield: Decimal
    expected_yield: Decimal
    percentage_of_portfolio: Decimal

    def __str__(self) -> str:
        d_sign = "+" if self.daily_yield > 0 else ""
        e_sign = "+" if self.expected_yield > 0 else ""
        return (
            f"<code>{self.ticker:<5}</code>|"
            f"{self.money:>7.0f}|"
            f"{d_sign}{self.daily_yield:>5.0f}|"
            f"{e_sign}{self.expected_yield:>5.0f}|"
            f"{self.percentage_of_portfolio:>4.1f}%"
        )


@dataclass(frozen=True)
class BondData:
    ticker: str
    money: Decimal
    nkd: Decimal
    daily_yield: Decimal
    expected_yield: Decimal
    percentage_of_portfolio: Decimal
    type: BondType

    def __str__(self) -> str:
        d_sign = "+" if self.daily_yield > 0 else ""
        e_sign = "+" if self.expected_yield > 0 else ""
        return (
            f"<code>{self.ticker:12} | {self.percentage_of_portfolio:>5.2f}%</code>\n"
            f"<code>└ {self.money:>7.0f} | {d_sign}{self.daily_yield:>4.0f} | {e_sign}{self.expected_yield:>5.0f} | {self.nkd:>4.0f}</code>"
        )


class InvestPortfolio:
    """Класс представляет собой объект портфолио из всех инструментов, которые имеет пользователь
    Объект неизменяемый, объект умеет получать данные из PortfolioResponse и отображать их в информацию,
    понятную пользователю для печати.
    """

    __portfolio: PortfolioResponse
    __positions: DefaultDict[InstrumentType, list[PortfolioPosition]] = defaultdict(list)
    __etf_core: Decimal
    __free_money: Decimal
    __total_portfolio: Decimal
    __shares: list[ShareData]
    __bonds: list[BondData]

    def __init__(self, portfolio: PortfolioResponse):
        self.__portfolio = portfolio
        self.__positions = defaultdict(list)
        for p in portfolio.positions:
            try:
                inst_type = InstrumentType(p.instrument_type)
                self.__positions[inst_type].append(p)
            except ValueError:
                continue
        self.__etf_core = self.__get_instrument_money(self.__positions[InstrumentType.ETF], ETF_CORE_TICKER)
        self.__free_money = self.__get_free_money()
        self.__total_portfolio = (
            get_money(self.__portfolio.total_amount_bonds)
            + get_money(self.__portfolio.total_amount_etf)
            + get_money(self.__portfolio.total_amount_currencies)
            + get_money(self.__portfolio.total_amount_shares)
        )
        self.__shares = self.__get_all_shares_data()
        self.__bonds = self.__get_all_bonds_data()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}"

    @property
    def etf_core(self) -> Decimal:
        return self.__etf_core

    @property
    def free_money(self) -> Decimal:
        return self.__free_money

    @property
    def shares(self) -> list[ShareData]:
        return self.__shares

    @property
    def bonds(self) -> list[BondData]:
        return self.__bonds

    @property
    def total_portfolio(self) -> Decimal:
        return self.__total_portfolio

    @write_log
    def print_common_info_str(self) -> str:
        total = self.__total_portfolio
        if total == 0:
            return "<b>Портфолио:</b>\nПусто. Пополните счет для анализа."

        data = {
            "etf_core": self.__etf_core,
            "bonds": get_money(self.__portfolio.total_amount_bonds),
            "shares": get_money(self.__portfolio.total_amount_shares),
            "other_etf": get_money(self.__portfolio.total_amount_etf) - self.__etf_core,
            "currencies": get_money(self.__portfolio.total_amount_currencies) - self.__free_money,
            "cash": self.__free_money,
        }

        def row(label: str, value: Decimal) -> str:
            percent = value / total * 100
            return f"<code>{label:<16}</code> | {value:>9,.0f} ₽ | <b>{percent:>5.2f}%</b>"

        message = [
            "<b>📊 СОСТОЯНИЕ ПОРТФЕЛЯ</b>",
            "",
            "<b>🟢 ЯДРО (Index/Safe)</b>",
            row("Фонды акций", data["etf_core"]),
            row("Облигации", data["bonds"]),
            "",
            "<b>🟡 СПУТНИКИ (Alpha)</b>",
            row("Акции", data["shares"]),
            row("Прочие фонды", data["other_etf"]),
            row("Металлы/Валюта", data["currencies"]),
            "",
            "<b>⚪️ КЭШ</b>",
            row("Свободно", data["cash"]),
            "—" * 20,
            f"<b>ИТОГО: {total:,.2f} ₽</b>",
        ]

        return "\n".join(message)

    @write_log
    def print_all_shares(self) -> str:
        header = (
            "<b>📊 Акции (₽)</b>\n"
            "<code>ТКР  |   Σ   |  📅  |  📈  | % </code>\n"
            "<code>-----|-------|------|------|----</code>"
        )
        body = "\n".join(str(s) for s in self.__shares)
        return f"{header}\n{body}"

    @write_log
    def print_all_bonds(self) -> str:
        header = (
            "<b>🧾 Облигации (₽)</b>\n"
            "<code>ISIN         | ДОЛЯ % </code>\n"
            "<code>  Σ ПОЗИЦИИ  | ДЕНЬ | ИТОГО| НКД </code>\n"
            "<code>-------------|------|------|-----</code>"
        )
        body = "\n".join(str(bond) for bond in self.__bonds)
        return f"{header}\n{body}"

    @write_log
    def __get_instrument_money(self, positions: list[PortfolioPosition], ticker: str) -> Decimal:
        for position in positions:
            if position.ticker == ticker:
                current_price = get_money(position.current_price)
                quantity = get_money(position.quantity)
                return current_price * quantity
        return Decimal(-1)

    @write_log
    def __get_free_money(self) -> Decimal:
        temp_free_money: PortfolioPosition = [
            element for element in self.__positions[InstrumentType.CURRENCY] if element.ticker == RUB_TICKER
        ].pop()
        return get_money(temp_free_money.quantity)

    @write_log
    def __get_all_shares_data(self) -> list[ShareData]:
        positions = sorted(
            self.__positions[InstrumentType.SHARE],
            key=lambda x: get_money(x.current_price) * get_money(x.quantity),
            reverse=True,
        )
        shares_data: list[ShareData] = [
            ShareData(
                ticker=p.ticker,
                money=get_money(p.current_price) * get_money(p.quantity),
                daily_yield=get_money(p.daily_yield),
                expected_yield=get_money(p.expected_yield),
                percentage_of_portfolio=get_percentage_from_element(
                    get_money(p.current_price) * get_money(p.quantity), self.__total_portfolio
                ),
            )
            for p in positions
        ]
        return shares_data

    @write_log
    def __get_all_bonds_data(self) -> list[BondData]:
        positions = sorted(
            self.__positions[InstrumentType.BOND],
            key=lambda x: get_money(x.current_price) * get_money(x.quantity),
            reverse=True,
        )

        bonds_data: list[BondData] = [
            BondData(
                ticker=p.ticker,
                money=get_money(p.current_price) * get_money(p.quantity),
                nkd=get_money(p.current_nkd),
                daily_yield=get_money(p.daily_yield),
                expected_yield=get_money(p.expected_yield),
                percentage_of_portfolio=get_percentage_from_element(
                    get_money(p.current_price) * get_money(p.quantity), self.__total_portfolio
                ),
                type=BondType(p.ticker),
            )
            for p in positions
        ]
        return bonds_data
