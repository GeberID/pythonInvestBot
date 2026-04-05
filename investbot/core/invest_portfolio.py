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
    EtfInstrumentData,
    ShareInstrumentData,
    InstrumentData,
)
from investbot.core.telegram_messages import share_header, bond_header

Position_data = TypeVar("Position_data")
T = TypeVar("T", bound=InstrumentData)


class InvestPortfolio:
    """Класс представляет собой объект портфолио из всех инструментов, которые имеет пользователь
    Объект неизменяемый, объект умеет получать данные из PortfolioResponse и отображать их в информацию,
    понятную пользователю для печати.
    """

    __portfolio: PortfolioResponse
    __positions: DefaultDict[InstrumentType, list[PortfolioPosition]] = defaultdict(list)
    __etf: list[EtfInstrumentData]
    __shares: list[ShareInstrumentData]
    __bonds: list[BondInstrumentData]
    __free_money: Decimal
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
        self.__total_portfolio = (
            get_money(self.__portfolio.total_amount_bonds)
            + get_money(self.__portfolio.total_amount_etf)
            + get_money(self.__portfolio.total_amount_currencies)
            + get_money(self.__portfolio.total_amount_shares)
        )
        self.__etf = self.__get_all_etfs_data()
        self.__shares = self.__get_all_shares_data()
        self.__bonds = self.__get_all_bonds_data()
        self.__free_money = self.__get_free_money()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}"

    @property
    def etf_core(self) -> list[EtfInstrumentData]:
        return self.__etf

    @property
    def shares(self) -> list[ShareInstrumentData]:
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
    def print_common_info_str(self) -> str:
        total = self.__total_portfolio
        if total == 0:
            return "<b>Портфолио:</b>\nПусто. Пополните счет для анализа."

        data = {
            "etf": get_money(self.__portfolio.total_amount_etf),
            "bonds": get_money(self.__portfolio.total_amount_bonds),
            "shares": get_money(self.__portfolio.total_amount_shares),
            "currencies": get_money(self.__portfolio.total_amount_currencies) - self.__free_money,
            "cash": self.__free_money,
        }

        def row(label: str, value: Decimal) -> str:
            percent = value / total * 100
            return f"<code>{label:<16}</code> | {value:>9,.0f} ₽ | <b>{percent:>5.2f}%</b>"

        message = [
            "<b>📊 СОСТОЯНИЕ ПОРТФЕЛЯ</b>",
            "",
            "<b>🟢 ЯДРО (Index/Safe)</b>",
            row("Фонды акций", data["etf"]),
            row("Облигации", data["bonds"]),
            "",
            "<b>🟡 СПУТНИКИ (Alpha)</b>",
            row("Акции", data["shares"]),
            row("Металлы/Валюта", data["currencies"]),
            "",
            "<b>⚪️ КЭШ</b>",
            row("Свободно", data["cash"]),
            "—" * 20,
            f"<b>ИТОГО: {total:,.2f} ₽</b>",
        ]

        return "\n".join(message)

    @write_log
    def print_all_shares(self) -> str:
        body = "\n".join(str(s) for s in self.__shares)
        return f"{share_header}\n{body}"

    @write_log
    def print_all_bonds(self) -> str:
        body = "\n".join(str(bond) for bond in self.__bonds)
        return f"{bond_header}\n{body}"

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
    def __get_all_etfs_data(self) -> list[EtfInstrumentData]:
        positions = self.__get_positions(self.__positions[InstrumentType.ETF])
        etfs_data: list[EtfInstrumentData] = [self.__create_instrument(p, EtfInstrumentData) for p in positions]
        return etfs_data

    @write_log
    def __get_all_shares_data(self) -> list[ShareInstrumentData]:
        positions = self.__get_positions(self.__positions[InstrumentType.SHARE])
        shares_data: list[ShareInstrumentData] = [self.__create_instrument(p, ShareInstrumentData) for p in positions]
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
