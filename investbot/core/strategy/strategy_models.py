from dataclasses import dataclass
from enum import Enum, auto

from investbot.core.portfolio.portfolio_models.portfolio_models import (
    BondInstrumentData,
    InstrumentData,
)
from investbot.core.base_types import Percentage


class Change(Enum):
    UP = auto()
    DOWN = auto()


@dataclass
class Discrepancy:
    etf: dict[InstrumentData, tuple[Percentage, Change]]
    shares: dict[InstrumentData, tuple[Percentage, Change]]
    bonds: dict[BondInstrumentData, tuple[Percentage, Change]]


@dataclass
class TargetAllocation:
    min_pct: Percentage
    middle_pct: Percentage
    max_pct: Percentage


@dataclass
class StrategyConfig:
    etf: TargetAllocation
    shares: TargetAllocation
    bonds_fix: TargetAllocation
    bonds_floater: TargetAllocation
    bonds_linker: TargetAllocation
