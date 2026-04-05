from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import Protocol, runtime_checkable

from investbot.configs import BOND_FIX, BOND_FLOATER, BOND_LINKER


class InstrumentType(StrEnum):
    SHARE = "share"
    BOND = "bond"
    ETF = "etf"
    CURRENCY = "currency"


class BondType(StrEnum):
    FIX = BOND_FIX
    FLOATER = BOND_FLOATER
    LINKER = BOND_LINKER


@runtime_checkable
class MarketInstrument(Protocol):
    """Протокол, описывающий минимально необходимые поля для любого актива."""

    ticker: str
    money: Decimal
    daily_yield: Decimal
    expected_yield: Decimal
    percentage_of_portfolio: Decimal

    def __init__(
        self,
        ticker: str,
        money: Decimal,
        daily_yield: Decimal,
        expected_yield: Decimal,
        percentage_of_portfolio: Decimal,
    ) -> None: ...


@dataclass(frozen=True, slots=True)
class InstrumentData:
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


@dataclass(frozen=True, slots=True)
class ShareInstrumentData(InstrumentData):
    pass


@dataclass(frozen=True, slots=True)
class EtfInstrumentData(InstrumentData):
    pass


@dataclass(frozen=True, slots=True)
class BondInstrumentData(InstrumentData):
    nkd: Decimal
    type: BondType

    def __str__(self) -> str:
        d_sign = "+" if self.daily_yield > 0 else ""
        e_sign = "+" if self.expected_yield > 0 else ""
        return (
            f"<code>{self.ticker:12} | {self.percentage_of_portfolio:>5.2f}%</code>\n"
            f"<code>└ {self.money:>7.0f} | {d_sign}{self.daily_yield:>4.0f} | {e_sign}{self.expected_yield:>5.0f} | {self.nkd:>4.0f}</code>"
        )
