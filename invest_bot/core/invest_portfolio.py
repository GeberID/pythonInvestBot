from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import TypeVar, DefaultDict

from t_tech.invest import PortfolioResponse, PortfolioPosition, MoneyValue

from invest_bot.configs import RUB_TICKER, ETF_CORE_TICKER
from invest_bot.core.log import write_log
from invest_bot.core.money_utilities import get_money, get_percentage_from_element

Position_data = TypeVar("Position_data")


class InstrumentType(StrEnum):
    SHARE = "share"
    BOND = "bond"
    ETF = "etf"
    CURRENCY = "currency"


@dataclass
class ShareData:
    ticker: str
    money: Decimal
    daily_yield: Decimal
    expected_yield: Decimal
    percentage_of_portfolio: Decimal

    def __str__(self):
        d_sign = "+" if self.daily_yield > 0 else ""
        e_sign = "+" if self.expected_yield > 0 else ""
        return (
            f"<code>{self.ticker:<5}</code>|"
            f"{self.money:>7.0f}|"
            f"{d_sign}{self.daily_yield:>5.0f}|"
            f"{e_sign}{self.expected_yield:>5.0f}|"
            f"{self.percentage_of_portfolio:>4.1f}%"
        )


@dataclass
class BondData:
    ticker: str
    money: Decimal
    nkd: Decimal
    daily_yield: Decimal
    expected_yield: Decimal
    percentage_of_portfolio: Decimal

    def __str__(self) -> str:
        d_sign = "+" if self.daily_yield > 0 else ""
        e_sign = "+" if self.expected_yield > 0 else ""
        return (
            f"<code>{self.ticker:12} | {self.percentage_of_portfolio:>5.2f}%</code>\n"
            f"<code>└ {self.money:>7.0f} | {d_sign}{self.daily_yield:>4.0f} | {e_sign}{self.expected_yield:>5.0f} | {self.nkd:>4.0f}</code>"
        )


class InvestPortfolio:
    _portfolio: PortfolioResponse
    _positions: DefaultDict[InstrumentType, list[PortfolioPosition]] = defaultdict(list)
    _etf_core: Decimal
    _free_money: Decimal
    _total_portfolio: Decimal
    _shares: list[ShareData]
    _bonds: list[BondData]

    def __init__(self, portfolio: PortfolioResponse):
        self._portfolio = portfolio
        self._positions = defaultdict(list)
        for p in portfolio.positions:
            try:
                inst_type = InstrumentType(p.instrument_type)
                self._positions[inst_type].append(p)
            except ValueError:
                continue
        self._etf_core = self.get_instrument_money(self._positions[InstrumentType.ETF], ETF_CORE_TICKER)
        self._free_money = self._get_free_money()
        self._total_portfolio = (
            get_money(self._portfolio.total_amount_bonds)
            + get_money(self._portfolio.total_amount_etf)
            + get_money(self._portfolio.total_amount_currencies)
            + get_money(self._portfolio.total_amount_shares)
        )
        self._shares = self._get_all_shares_data()
        self._bonds = self._get_all_bonds_data()

    def __repr__(self):
        return f"{self.__class__.__name__}"

    @write_log
    def print_common_info_str_old(self) -> str:
        return (
            f"Портфолио:\n"
            f"Ядро:\n"
            f"Фонды акций- {self._etf_core:,.2f} ₽ - "
            f" {get_percentage_from_element(self._etf_core, self._total_portfolio)} %\n"
            f"Облигации - {get_money(self._portfolio.total_amount_bonds):,.2f} ₽ - "
            f"{get_percentage_from_element(get_money(self._portfolio.total_amount_bonds), self._total_portfolio)} %\n\n"
            f"Спутники:\n"
            f"Акции - {get_money(self._portfolio.total_amount_shares):,.2f} ₽ - "
            f"{get_percentage_from_element(get_money(self._portfolio.total_amount_shares), self._total_portfolio)} %\n"
            f"Остальные Фонды - {get_money(self._portfolio.total_amount_etf):,.2f} ₽ - "
            f"{get_percentage_from_element(get_money(self._portfolio.total_amount_etf), self._total_portfolio)} %\n"
            f"Валюта и драгметалы - {get_money(self._portfolio.total_amount_currencies)  - self._free_money:,.2f} ₽ - "
            f"{get_percentage_from_element(get_money(self._portfolio.total_amount_currencies), self._total_portfolio)} %\n\n"
            f"Свободной валюты - {self._free_money:,.2f} ₽ - {get_percentage_from_element(self._free_money, self._total_portfolio)} %\n\n"
            f"------------------------------\n"
            f"Всего - {self._total_portfolio:,.2f} ₽"
        )

    @write_log
    def print_common_info_str(self) -> str:
        total = self._total_portfolio
        if total == 0:
            return "<b>Портфолио:</b>\nПусто. Пополните счет для анализа."

        data = {
            "etf_core": self._etf_core,
            "bonds": get_money(self._portfolio.total_amount_bonds),
            "shares": get_money(self._portfolio.total_amount_shares),
            "other_etf": get_money(self._portfolio.total_amount_etf) - self._etf_core,
            "currencies": get_money(self._portfolio.total_amount_currencies) - self._free_money,
            "cash": self._free_money,
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
        body = "\n".join(str(s) for s in self._shares)
        return f"{header}\n{body}"

    @write_log
    def print_all_bonds(self) -> str:
        header = (
            "<b>🧾 Облигации (₽)</b>\n"
            "<code>ISIN         | ДОЛЯ % </code>\n"
            "<code>  Σ ПОЗИЦИИ  | ДЕНЬ | ИТОГО| НКД </code>\n"
            "<code>-------------|------|------|-----</code>"
        )
        body = "\n".join(str(bond) for bond in self._bonds)
        return f"{header}\n{body}"

    @write_log
    def get_instrument_money(self, positions: list[PortfolioPosition], ticker: str) -> Decimal:
        for position in positions:
            if position.ticker == ticker:
                current_price = get_money(position.current_price)
                quantity = get_money(position.quantity)
                return current_price * quantity
        return Decimal(-1)

    @write_log
    def _get_free_money(self) -> Decimal:
        temp_free_money: PortfolioPosition = [
            element for element in self._positions[InstrumentType.CURRENCY] if element.ticker == RUB_TICKER
        ].pop()
        return get_money(temp_free_money.quantity)

    @write_log
    def _get_all_shares_data(self) -> list[ShareData]:
        positions = sorted(
            self._positions[InstrumentType.SHARE],
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
                    get_money(p.current_price) * get_money(p.quantity), self._total_portfolio
                ),
            )
            for p in positions
        ]
        return shares_data

    @write_log
    def _get_all_bonds_data(self) -> list[BondData]:
        positions = sorted(
            self._positions[InstrumentType.BOND],
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
                    get_money(p.current_price) * get_money(p.quantity), self._total_portfolio
                ),
            )
            for p in positions
        ]
        return bonds_data
