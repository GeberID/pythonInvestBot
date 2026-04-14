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
