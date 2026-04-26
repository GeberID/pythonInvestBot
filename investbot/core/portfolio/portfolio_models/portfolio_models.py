from dataclasses import dataclass, field
from decimal import Decimal
from enum import StrEnum
from typing import Sequence

from investbot.configs import BOND_FIX, BOND_FLOATER, BOND_LINKER
from investbot.core.base_types import Money, Percentage


class InstrumentType(StrEnum):
    SHARE = "share"
    BOND = "bond"
    ETF = "etf"
    CURRENCY = "currency"


class BondType(StrEnum):
    FIX = BOND_FIX
    FLOATER = BOND_FLOATER
    LINKER = BOND_LINKER


@dataclass(frozen=True, slots=True)
class InstrumentData:
    ticker: str
    money: Money
    daily_yield: Money
    expected_yield: Money
    percentage_of_portfolio: Percentage


@dataclass(frozen=True, slots=True)
class BondInstrumentData(InstrumentData):
    nkd: Money
    type: BondType


@dataclass(frozen=True, slots=True)
class InvestPortfolio:
    etf_core: Sequence[InstrumentData] = field(default_factory=tuple)
    etfs: Sequence[InstrumentData] = field(default_factory=tuple)
    shares: Sequence[InstrumentData] = field(default_factory=tuple)
    bonds: Sequence[BondInstrumentData] = field(default_factory=tuple)
    free_money: Money = Money(Decimal(0))
    total_amount_bonds: Money = Money(Decimal(0))
    total_amount_etf: Money = Money(Decimal(0))
    total_amount_currencies: Money = Money(Decimal(0))
    total_amount_shares: Money = Money(Decimal(0))
    total_portfolio: Money = Money(Decimal(0))
