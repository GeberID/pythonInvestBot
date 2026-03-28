from dataclasses import dataclass
from decimal import Decimal
from enum import Enum, auto
from typing import TypeVar

from configs import (
    ETF_FOND_MAX,
    ETF_FOND_MIN,
    ETF_FOND_MIDDLE,
    SHARES_MAX,
    SHARES_MIDDLE,
    BOND_FIX_MAX,
    BOND_FIX_MIN,
    BOND_FIX_MIDDLE,
    BOND_FLOATER_MAX,
    BOND_FLOATER_MIN,
    BOND_FLOATER_MIDDLE,
    BOND_LINKER_MAX,
    BOND_LINKER_MIN,
    BOND_LINKER_MIDDLE,
    SHARES_MIN,
)
from core.invest_portfolio import InvestPortfolio
from core.log import write_log
from core.portfolio_instruments import (
    InstrumentData,
    ShareInstrumentData,
    EtfInstrumentData,
    BondInstrumentData,
    BondType,
)

T = TypeVar("T", ShareInstrumentData, EtfInstrumentData, BondInstrumentData)


class Change(Enum):
    UP = auto()
    DOWN = auto()


@dataclass
class Discrepancy:
    etf: dict[EtfInstrumentData, tuple[Decimal, Change]]
    shares: dict[ShareInstrumentData, tuple[Decimal, Change]]
    bonds: dict[BondInstrumentData, tuple[Decimal, Change]]


class StrategyAnalyzer:
    """Класс представляет собой объект, который сравнивает текущие данные из InvestPortfolio с заранее
    забитыми инструментами и процентным соотношением из configs.py.
    Инварианты - объект получает данные только из InvestPortfolio
    Объект умеет подготавливать сообщение в виде текста пользователю
    Объект умеет строить план ребалансировки"""

    __discrepancy: Discrepancy

    def __init__(self) -> None:
        self.__discrepancy = Discrepancy(etf={}, shares={}, bonds={})

    @write_log
    def analyze(self, portfolio: InvestPortfolio) -> Discrepancy:
        self.__check_etf_core(portfolio.etf_core)
        self.__check_shares(portfolio.shares)
        self.__check_bond(portfolio.bonds)
        return self.__discrepancy

    @write_log
    def __check_etf_core(self, etfs: list[EtfInstrumentData]) -> None:
        for etf in etfs:
            self.__set_discrepancy(self.__discrepancy.etf, etf, ETF_FOND_MAX, ETF_FOND_MIDDLE, ETF_FOND_MIN)

    @write_log
    def __check_shares(self, shares: list[ShareInstrumentData]) -> None:
        for share in shares:
            self.__set_discrepancy(self.__discrepancy.shares, share, SHARES_MAX, SHARES_MIDDLE, SHARES_MIN)

    @write_log
    def __check_bond(self, bonds: list[BondInstrumentData]) -> None:
        for bond in bonds:
            match bond.type:
                case BondType.FIX:
                    self.__set_discrepancy(self.__discrepancy.bonds, bond, BOND_FIX_MAX, BOND_FIX_MIDDLE, BOND_FIX_MIN)
                case BondType.FLOATER:
                    self.__set_discrepancy(
                        self.__discrepancy.bonds, bond, BOND_FLOATER_MAX, BOND_FLOATER_MIDDLE, BOND_FLOATER_MIN
                    )
                case BondType.LINKER:
                    self.__set_discrepancy(
                        self.__discrepancy.bonds, bond, BOND_LINKER_MAX, BOND_LINKER_MIDDLE, BOND_LINKER_MIN
                    )

    @write_log
    def __set_discrepancy(
        self,
        discrepancy_dict: dict[T, tuple[Decimal, Change]],
        data: T,
        config_max: Decimal,
        config_middle: Decimal,
        config_min: Decimal,
    ) -> None:
        if data.percentage_of_portfolio > config_max:
            discrepancy_dict[data] = (data.percentage_of_portfolio - config_max, Change.DOWN)
        elif data.percentage_of_portfolio < config_min:
            discrepancy_dict[data] = (config_middle - data.percentage_of_portfolio, Change.UP)
