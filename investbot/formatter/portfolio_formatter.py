from decimal import Decimal
from typing import Protocol

from investbot.core.log import write_log
from investbot.core.domain.portfolio_models import BondInstrumentData, InstrumentData, InvestPortfolio


class Formatter(Protocol):
    def print_common_info_str(self) -> str: ...
    def print_all_shares(self) -> str: ...
    def print_all_bonds(self) -> str: ...


class TelegramPortfolioFormatter:
    share_header = (
        "<b>📊 Акции (₽)</b>\n"
        "<code>ТКР  |   Σ   |  📅  |  📈  | % </code>\n"
        "<code>-----|-------|------|------|----</code>"
    )

    bond_header = (
        "<b>🧾 Облигации (₽)</b>\n"
        "<code>ISIN         | ДОЛЯ % </code>\n"
        "<code>  Σ ПОЗИЦИИ  | ДЕНЬ | ИТОГО| НКД </code>\n"
        "<code>-------------|------|------|-----</code>"
    )

    def __init__(self, portfolio: InvestPortfolio):
        self.__portfolio = portfolio

    @write_log
    def print_common_info_str(self) -> str:
        total = self.__portfolio.total_portfolio
        if total == 0:
            return "<b>Портфолио:</b>\nПусто. Пополните счет для анализа."

        data = {
            "etf": self.__portfolio.total_amount_etf,
            "bonds": self.__portfolio.total_amount_bonds,
            "shares": self.__portfolio.total_amount_shares,
            "currencies": self.__portfolio.total_amount_currencies - self.__portfolio.free_money,
            "cash": self.__portfolio.free_money,
        }

        def row(label: str, value: Decimal) -> str:
            percent = value / total * 100
            return f"<code>{label:<16}</code> | {value:>9,.0f} ₽ | <b>{percent:>5.2f}%</b>"

        message = [
            "<b>📊 СОСТОЯНИЕ ПОРТФЕЛЯ</b>",
            "",
            "<b>🟢 ЯДРО (Index/Safe)</b>",
            row("Фонды акций", data["etf"]),
            row("Облигации", data["bonds"]),
            "",
            "<b>🟡 СПУТНИКИ (Alpha)</b>",
            row("Акции", data["shares"]),
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
        body = "\n".join(self.__print_instrument(s) for s in self.__portfolio.shares)
        return f"{self.share_header}\n{body}"

    @write_log
    def print_all_bonds(self) -> str:
        body = "\n".join(self.__print_bond(bond) for bond in self.__portfolio.bonds)
        return f"{self.bond_header}\n{body}"

    def __print_instrument(self, share: InstrumentData) -> str:
        d_sign = "+" if share.daily_yield > 0 else ""
        e_sign = "+" if share.expected_yield > 0 else ""
        return (
            f"<code>{share.ticker:<5}</code>|"
            f"{share.money:>7.0f}|"
            f"{d_sign}{share.daily_yield:>5.0f}|"
            f"{e_sign}{share.expected_yield:>5.0f}|"
            f"{share.percentage_of_portfolio:>4.1f}%"
        )

    def __print_bond(self, bond: BondInstrumentData) -> str:
        d_sign = "+" if bond.daily_yield > 0 else ""
        e_sign = "+" if bond.expected_yield > 0 else ""
        return (
            f"<code>{bond.ticker:12} | {bond.percentage_of_portfolio:>5.2f}%</code>\n"
            f"<code>└ {bond.money:>7.0f} | {d_sign}{bond.daily_yield:>4.0f} | {e_sign}{bond.expected_yield:>5.0f} | {bond.nkd:>4.0f}</code>"
        )
