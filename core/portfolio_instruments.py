from abc import ABC
from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from configs import RUB_TICKER, ETF_CORE_TICKER, BOND_FIX, BOND_FLOATER, BOND_LINKER


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
class Data(ABC):
    ticker: str
    money: Decimal
    daily_yield: Decimal
    expected_yield: Decimal
    percentage_of_portfolio: Decimal


@dataclass(frozen=True)
class EtfData(Data):

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
class ShareData(Data):

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
class BondData(Data):
    nkd: Decimal
    type: BondType

    def __str__(self) -> str:
        d_sign = "+" if self.daily_yield > 0 else ""
        e_sign = "+" if self.expected_yield > 0 else ""
        return (
            f"<code>{self.ticker:12} | {self.percentage_of_portfolio:>5.2f}%</code>\n"
            f"<code>└ {self.money:>7.0f} | {d_sign}{self.daily_yield:>4.0f} | {e_sign}{self.expected_yield:>5.0f} | {self.nkd:>4.0f}</code>"
        )
