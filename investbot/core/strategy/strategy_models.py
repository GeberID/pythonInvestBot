from dataclasses import dataclass
from decimal import Decimal
from enum import Enum, auto

from investbot.core.portfolio_instruments import BondInstrumentData, InstrumentData


class Change(Enum):
    UP = auto()
    DOWN = auto()


@dataclass
class Discrepancy:
    etf: dict[InstrumentData, tuple[Decimal, Change]]
    shares: dict[InstrumentData, tuple[Decimal, Change]]
    bonds: dict[BondInstrumentData, tuple[Decimal, Change]]


@dataclass
class TargetAllocation:
    min_pct: Decimal
    middle_pct: Decimal
    max_pct: Decimal


@dataclass
class StrategyConfig:
    etf: TargetAllocation
    shares: TargetAllocation
    bonds_fix: TargetAllocation
    bonds_floater: TargetAllocation
    bonds_linker: TargetAllocation
