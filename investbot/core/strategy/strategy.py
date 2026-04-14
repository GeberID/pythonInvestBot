from decimal import Decimal
from typing import TypeVar

from investbot.configs import (
    ETF_MIN,
    ETF_TARGET,
    ETF_MAX,
    SHARE_MIN,
    SHARE_TARGET,
    SHARE_MAX,
    BOND_FIX_MIN,
    BOND_FIX_TARGET,
    BOND_FIX_MAX,
    BOND_FLOATER_MIN,
    BOND_FLOATER_TARGET,
    BOND_FLOATER_MAX,
    BOND_LINKER_MIN,
    BOND_LINKER_TARGET,
    BOND_LINKER_MAX,
)
from investbot.core.invest_portfolio import InvestPortfolio
from investbot.core.log import write_log
from investbot.core.portfolio_instruments import (
    BondType,
    InstrumentData,
)
from investbot.core.strategy.strategy_models import Discrepancy, StrategyConfig, TargetAllocation, Change

etf = TargetAllocation(min_pct=ETF_MIN, middle_pct=ETF_TARGET, max_pct=ETF_MAX)
shares = TargetAllocation(min_pct=SHARE_MIN, middle_pct=SHARE_TARGET, max_pct=SHARE_MAX)
bond_fix = TargetAllocation(min_pct=BOND_FIX_MIN, middle_pct=BOND_FIX_TARGET, max_pct=BOND_FIX_MAX)
bond_floater = TargetAllocation(min_pct=BOND_FLOATER_MIN, middle_pct=BOND_FLOATER_TARGET, max_pct=BOND_FLOATER_MAX)
bond_linker = TargetAllocation(min_pct=BOND_LINKER_MIN, middle_pct=BOND_LINKER_TARGET, max_pct=BOND_LINKER_MAX)

strategy = StrategyConfig(etf, shares, bond_fix, bond_floater, bond_linker)

T = TypeVar("T", bound=InstrumentData)


class StrategyAnalyzer:
    """Класс представляет собой объект, который сравнивает текущие данные из InvestPortfolio с заранее
    забитыми инструментами и процентным соотношением из configs.py.
    Инварианты - объект получает данные только из InvestPortfolio
    Объект умеет подготавливать сообщение в виде текста пользователю
    Объект умеет строить план ребалансировки"""

    __discrepancy: Discrepancy

    def __init__(self, strategy_config: StrategyConfig) -> None:
        self.__config = strategy_config
        self.__discrepancy = Discrepancy(etf={}, shares={}, bonds={})

    @write_log
    def analyze(self, portfolio: InvestPortfolio) -> Discrepancy:
        self.__analyze_group(portfolio.etf_core, self.__config.etf, self.__discrepancy.etf)
        self.__analyze_group(portfolio.shares, self.__config.shares, self.__discrepancy.shares)
        for bond in portfolio.bonds:
            target = self.__get_bond_target(bond.type)
            self.__analyze_group(portfolio.bonds, target, self.__discrepancy.bonds)
        return self.__discrepancy

    @write_log
    def __analyze_group(
        self,
        items: list[T],
        target: TargetAllocation,
        result_dict: dict[T, tuple[Decimal, Change]],
    ) -> None:
        for item in items:
            self.__set_discrepancy(result_dict, item, target)

    def __get_bond_target(self, bond_type: BondType) -> TargetAllocation:
        match bond_type:
            case BondType.FIX:
                return self.__config.bonds_fix
            case BondType.FLOATER:
                return self.__config.bonds_floater
            case BondType.LINKER:
                return self.__config.bonds_linker

    @staticmethod
    def __set_discrepancy(discrepancy_dict: dict[T, tuple[Decimal, Change]], data: T, target: TargetAllocation) -> None:
        if data.percentage_of_portfolio > target.max_pct:
            discrepancy_dict[data] = (data.percentage_of_portfolio - target.max_pct, Change.DOWN)
        elif data.percentage_of_portfolio < target.min_pct:
            discrepancy_dict[data] = (target.middle_pct - data.percentage_of_portfolio, Change.UP)
