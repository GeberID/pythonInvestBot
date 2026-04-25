from dataclasses import dataclass, field
from decimal import Decimal
from enum import StrEnum
from typing import Sequence

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


@dataclass(frozen=True, slots=True)
class InstrumentData:
    ticker: str
    money: Decimal
    daily_yield: Decimal
    expected_yield: Decimal
    percentage_of_portfolio: Decimal


@dataclass(frozen=True, slots=True)
class BondInstrumentData(InstrumentData):
    nkd: Decimal
    type: BondType


@dataclass(frozen=True, slots=True)
class InvestPortfolio:
    etf_core: Sequence[InstrumentData] = field(default_factory=tuple)
    etfs: Sequence[InstrumentData] = field(default_factory=tuple)
    shares: Sequence[InstrumentData] = field(default_factory=tuple)
    bonds: Sequence[BondInstrumentData] = field(default_factory=tuple)
    free_money: Decimal = Decimal(0)
    total_amount_bonds: Decimal = Decimal(0)
    total_amount_etf: Decimal = Decimal(0)
    total_amount_currencies: Decimal = Decimal(0)
    total_amount_shares: Decimal = Decimal(0)
    total_portfolio: Decimal = Decimal(0)
