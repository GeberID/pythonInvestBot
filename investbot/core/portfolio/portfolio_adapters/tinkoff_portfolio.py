from collections import defaultdict
from decimal import Decimal
from typing import TypeVar, DefaultDict, Type

from t_tech.invest import PortfolioResponse, PortfolioPosition

from investbot.configs import RUB_TICKER, ETF_CORE_TICKER
from investbot.core.log import write_log, logger
from investbot.core.money_utilities import get_money, get_percentage_from_element
from investbot.core.portfolio.portfolio_models.portfolio_models import (
    InstrumentType,
    BondInstrumentData,
    BondType,
    InstrumentData,
    InvestPortfolio,
)

Position_data = TypeVar("Position_data")
T = TypeVar("T", bound=InstrumentData)


class TinkoffBrokerAdapter:
    """Класс представляет собой объект портфолио из всех инструментов, которые имеет пользователь
    Объект неизменяемый, объект умеет получать данные из PortfolioResponse и отображать их в информацию,
    понятную пользователю для печати.
    """

    __portfolio: PortfolioResponse
    __positions: DefaultDict[InstrumentType, list[PortfolioPosition]] = defaultdict(list)
    __etf_core: list[InstrumentData]
    __etfs: list[InstrumentData]
    __shares: list[InstrumentData]
    __bonds: list[BondInstrumentData]
    __free_money: Decimal
    __total_amount_bonds: Decimal
    __total_amount_etf: Decimal
    __total_amount_currencies: Decimal
    __total_amount_shares: Decimal
    __total_portfolio: Decimal

    def __init__(self, portfolio: PortfolioResponse):
        self.__portfolio = portfolio
        self.__positions = defaultdict(list)
        for p in portfolio.positions:
            try:
                inst_type = InstrumentType(p.instrument_type)
                self.__positions[inst_type].append(p)
            except ValueError:
                continue
        self.__total_amount_bonds = get_money(self.__portfolio.total_amount_bonds)
        self.__total_amount_etf = get_money(self.__portfolio.total_amount_etf)
        self.__total_amount_currencies = get_money(self.__portfolio.total_amount_currencies)
        self.__total_amount_shares = get_money(self.__portfolio.total_amount_shares)
        self.__total_portfolio = (
            self.__total_amount_bonds
            + self.__total_amount_etf
            + self.__total_amount_currencies
            + self.__total_amount_shares
        )
        self.__etfs = self.__get_all_etfs_data()
        self.__etf_core = [f for f in self.__etfs if f.ticker == ETF_CORE_TICKER]
        self.__shares = self.__get_all_shares_data()
        self.__bonds = self.__get_all_bonds_data()
        self.__free_money = self.__get_free_money()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}"

    def fetch_portfolio(self) -> InvestPortfolio:
        return InvestPortfolio(
            etf_core=self.__etf_core,
            etfs=self.__etfs,
            shares=self.__shares,
            bonds=self.__bonds,
            free_money=self.__free_money,
            total_amount_bonds=self.__total_amount_bonds,
            total_amount_etf=self.__total_amount_etf,
            total_amount_currencies=self.__total_amount_currencies,
            total_amount_shares=self.__total_amount_shares,
            total_portfolio=self.__total_portfolio,
        )

    @write_log
    def __get_free_money(self) -> Decimal:
        positions = self.__positions[InstrumentType.CURRENCY]
        temp_free_money = next((element for element in positions if element.ticker == RUB_TICKER), None)
        if temp_free_money is None:
            return Decimal(0)
        return get_money(temp_free_money.quantity)

    @write_log
    def __get_all_etfs_data(self) -> list[InstrumentData]:
        positions = self.__get_positions(self.__positions[InstrumentType.ETF])
        if len(positions) > 0:
            etfs_data: list[InstrumentData] = [self.__create_instrument(p, InstrumentData) for p in positions]
            return etfs_data
        logger.warning(f"Empty ETFs in positions: {positions}")
        return []

    @write_log
    def __get_all_shares_data(self) -> list[InstrumentData]:
        positions = self.__get_positions(self.__positions[InstrumentType.SHARE])
        if len(positions) > 0:
            shares_data: list[InstrumentData] = [self.__create_instrument(p, InstrumentData) for p in positions]
            return shares_data
        logger.warning(f"Empty Shares in positions: {positions}")
        return []

    @write_log
    def __get_all_bonds_data(self) -> list[BondInstrumentData]:
        positions = self.__get_positions(self.__positions[InstrumentType.BOND])
        valid_tickers = {item.value for item in BondType}
        if len(positions) > 0:
            bonds_data: list[BondInstrumentData] = [
                BondInstrumentData(
                    ticker=p.ticker,
                    money=get_money(p.current_price) * get_money(p.quantity),
                    nkd=get_money(p.current_nkd),
                    daily_yield=get_money(p.daily_yield),
                    expected_yield=get_money(p.expected_yield),
                    percentage_of_portfolio=get_percentage_from_element(
                        get_money(p.current_price) * get_money(p.quantity), self.__total_portfolio
                    ),
                    type=BondType(p.ticker),
                )
                for p in positions
                if p.ticker in valid_tickers
            ]
            return bonds_data
        logger.warning(f"Empty Bonds in positions: {positions}")
        return []

    @write_log
    def __get_positions(self, positions: list[PortfolioPosition]) -> list[PortfolioPosition]:
        if not positions:
            logger.warning(f"Empty positions: {positions}")
            return []
        positions = sorted(
            positions,
            key=lambda x: get_money(x.current_price) * get_money(x.quantity),
            reverse=True,
        )
        return positions

    @write_log
    def __create_instrument(self, p: PortfolioPosition, instrument_class: Type[T]) -> T:
        return instrument_class(
            ticker=p.ticker,
            money=get_money(p.current_price) * get_money(p.quantity),
            daily_yield=get_money(p.daily_yield),
            expected_yield=get_money(p.expected_yield),
            percentage_of_portfolio=get_percentage_from_element(
                get_money(p.current_price) * get_money(p.quantity), self.__total_portfolio
            ),
        )
