from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

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
    etf_core: list[InstrumentData]
    etfs: list[InstrumentData]
    shares: list[InstrumentData]
    bonds: list[BondInstrumentData]
    free_money: Decimal
    total_amount_bonds: Decimal
    total_amount_etf: Decimal
    total_amount_currencies: Decimal
    total_amount_shares: Decimal
    total_portfolio: Decimal
