from collections import defaultdict
from decimal import Decimal
from typing import TypeVar, DefaultDict, Type

from t_tech.invest import PortfolioResponse, PortfolioPosition

from investbot.configs import RUB_TICKER
from investbot.core.log import write_log
from investbot.core.money_utilities import get_money, get_percentage_from_element
from investbot.core.portfolio_instruments import (
    InstrumentType,
    BondInstrumentData,
    BondType,
    InstrumentData,
)

Position_data = TypeVar("Position_data")
T = TypeVar("T", bound=InstrumentData)


class InvestPortfolio:
    """Класс представляет собой объект портфолио из всех инструментов, которые имеет пользователь
    Объект неизменяемый, объект умеет получать данные из PortfolioResponse и отображать их в информацию,
    понятную пользователю для печати.
    """

    __portfolio: PortfolioResponse
    __positions: DefaultDict[InstrumentType, list[PortfolioPosition]] = defaultdict(list)
    __etf: list[InstrumentData]
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
            self.__total_amount_bonds + self.total_amount_etf + self.total_amount_currencies + self.total_amount_shares
        )
        self.__etf = self.__get_all_etfs_data()
        self.__shares = self.__get_all_shares_data()
        self.__bonds = self.__get_all_bonds_data()
        self.__free_money = self.__get_free_money()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}"

    @property
    def total_amount_bonds(self) -> Decimal:
        return self.__total_amount_bonds

    @property
    def total_amount_etf(self) -> Decimal:
        return self.__total_amount_etf

    @property
    def total_amount_currencies(self) -> Decimal:
        return self.__total_amount_currencies

    @property
    def total_amount_shares(self) -> Decimal:
        return self.__total_amount_shares

    @property
    def etf_core(self) -> list[InstrumentData]:
        return self.__etf

    @property
    def shares(self) -> list[InstrumentData]:
        return self.__shares

    @property
    def bonds(self) -> list[BondInstrumentData]:
        return self.__bonds

    @property
    def free_money(self) -> Decimal:
        return self.__free_money

    @property
    def total_portfolio(self) -> Decimal:
        return self.__total_portfolio

    @write_log
    def __get_instrument_money(self, positions: list[PortfolioPosition], ticker: str) -> Decimal:
        for position in positions:
            if position.ticker == ticker:
                current_price = get_money(position.current_price)
                quantity = get_money(position.quantity)
                return current_price * quantity
        raise ValueError(f"Не найдено позиции с тикером {ticker}")

    @write_log
    def __get_free_money(self) -> Decimal:
        positions = self.__positions[InstrumentType.CURRENCY]
        if not positions:
            raise ValueError("Не найдены валютные позиции")
        temp_free_money = next((element for element in positions if element.ticker == RUB_TICKER), None)
        if temp_free_money is None:
            raise ValueError(f"Не найдена позиция с тикером {RUB_TICKER}")
        return get_money(temp_free_money.quantity)

    @write_log
    def __get_all_etfs_data(self) -> list[InstrumentData]:
        positions = self.__get_positions(self.__positions[InstrumentType.ETF])
        etfs_data: list[InstrumentData] = [self.__create_instrument(p, InstrumentData) for p in positions]
        return etfs_data

    @write_log
    def __get_all_shares_data(self) -> list[InstrumentData]:
        positions = self.__get_positions(self.__positions[InstrumentType.SHARE])
        shares_data: list[InstrumentData] = [self.__create_instrument(p, InstrumentData) for p in positions]
        return shares_data

    @write_log
    def __get_all_bonds_data(self) -> list[BondInstrumentData]:
        positions = self.__get_positions(self.__positions[InstrumentType.BOND])
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
        ]
        return bonds_data

    @write_log
    def __get_positions(self, positions: list[PortfolioPosition]) -> list[PortfolioPosition]:
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
