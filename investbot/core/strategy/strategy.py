from decimal import ROUND_DOWN, Decimal
from typing import TypeVar, Sequence

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
from investbot.core.log import write_log
from investbot.core.portfolio.portfolio_models.portfolio_models import (
    BondType,
    InstrumentData,
    InvestPortfolio,
    BondInstrumentData,
)
from investbot.core.base_types import Percentage, Money
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
    Объект умеет подготавливать
    Объект умеет строить план ребалансировки"""

    __discrepancy: Discrepancy

    def __init__(self, strategy_config: StrategyConfig) -> None:
        self.__config = strategy_config
        self.__discrepancy = Discrepancy(etf={}, shares={}, bonds={})

    @write_log
    def analyze(self, portfolio: InvestPortfolio) -> Discrepancy:
        portfolio_bond_linker = [i for i in portfolio.bonds if i.type == BondType.LINKER]
        portfolio_bond_floater = [i for i in portfolio.bonds if i.type == BondType.FLOATER]
        portfolio_bond_fix = [i for i in portfolio.bonds if i.type == BondType.FIX]

        self.__analyze_group(portfolio.etf_core, self.__config.etf, self.__discrepancy.etf, portfolio.total_portfolio)
        self.__analyze_group(
            portfolio.shares, self.__config.shares, self.__discrepancy.shares, portfolio.total_portfolio
        )
        self.__analyze_group(
            portfolio_bond_linker, self.__config.bonds_linker, self.__discrepancy.bonds, portfolio.total_portfolio
        )
        self.__analyze_group(
            portfolio_bond_floater, self.__config.bonds_floater, self.__discrepancy.bonds, portfolio.total_portfolio
        )
        self.__analyze_group(
            portfolio_bond_fix, self.__config.bonds_fix, self.__discrepancy.bonds, portfolio.total_portfolio
        )
        return self.__discrepancy

    def __analyze_group(
        self,
        items: Sequence[T],
        target: TargetAllocation,
        result_dict: dict[T, tuple[int, Change]],
        total_portfolio: Money,
    ) -> None:
        for item in items:
            self.__set_discrepancy(result_dict, item, target, total_portfolio)

    def __set_discrepancy(
        self, discrepancy_dict: dict[T, tuple[int, Change]], data: T, target: TargetAllocation, total_portfolio: Money
    ) -> None:
        if isinstance(data, BondInstrumentData):
            Money(data.one_instr_money + data.nkd)
        else:
            instrument_money = data.one_instr_money

        if data.percentage_of_portfolio > target.max_pct:
            percentage_inst = Percentage(data.percentage_of_portfolio - target.middle_pct)
            lots = self.__get_lots_for_working(instrument_money, data.lot, percentage_inst, total_portfolio)
            discrepancy_dict[data] = (lots, Change.DOWN)
        elif data.percentage_of_portfolio < target.min_pct:
            percentage_inst = Percentage(target.middle_pct - data.percentage_of_portfolio)
            lots = self.__get_lots_for_working(instrument_money, data.lot, percentage_inst, total_portfolio)
            discrepancy_dict[data] = (lots, Change.UP)

    def __get_lots_for_working(
        self,
        current_inst_money: Money,
        inst_lot: int,
        discrepancy_percentage: Percentage,
        total_portfolio: Money,
    ) -> int:
        target_money_delta = total_portfolio * (discrepancy_percentage / Decimal("100"))
        return int(((target_money_delta / current_inst_money) / inst_lot).to_integral_value(rounding=ROUND_DOWN))
