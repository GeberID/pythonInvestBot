from decimal import Decimal
from enum import Enum

from t_tech.invest import PortfolioResponse, PortfolioPosition

from invest_bot.core.logs import log
from invest_bot.core.money_utilities import get_money, get_percentage_from_element

RUB_TICKER = "RUB000UTSTOM"


class InstrumentType(Enum):
    SHARE = "share"
    BOND = "bond"
    ETF = "etf"
    CURRENCY = "currency"

class Portfolio:
    _portfolio: PortfolioResponse
    freeMoney: Decimal
    positions: dict[InstrumentType, list[PortfolioPosition]]
    positionsAmt: dict[InstrumentType,Decimal]

    def __init__(self, portfolio: PortfolioResponse):
        self._portfolio = portfolio
        self.positions = {
            InstrumentType.SHARE:self._get_all_positions(InstrumentType.SHARE),
            InstrumentType.BOND:self._get_all_positions(InstrumentType.BOND),
            InstrumentType.ETF:self._get_all_positions(InstrumentType.ETF),
            InstrumentType.CURRENCY:self._get_all_currencies_positions(),
        }
        self.positionsAmt = {
            InstrumentType.SHARE: get_money(portfolio.total_amount_shares),
            InstrumentType.BOND: get_money(portfolio.total_amount_bonds),
            InstrumentType.ETF: get_money(portfolio.total_amount_etf),
            InstrumentType.CURRENCY: get_money(portfolio.total_amount_currencies),
        }
        self.freeMoney = self._update_free_money()

    def __repr__(self):
        return f"{self.__class__.__name__}"

    @log
    def print_common_info_str(self) -> str:
        return (
            f"Портфолио:\n"
            f"Акции - {self.positionsAmt.get(InstrumentType.SHARE):,.2f} ₽\n"
            f"Облигации - {self.positionsAmt.get(InstrumentType.BOND):,.2f} ₽\n"
            f"Фонды - {self.positionsAmt.get(InstrumentType.ETF):,.2f} ₽\n"
            f"Валюта и драгметалы - {self.positionsAmt.get(InstrumentType.CURRENCY) - self.freeMoney:,.2f} ₽\n"
            f"Свободной валюты - {self.freeMoney:,.2f} ₽\n"
            f"------------------------------\n"
            f"Всего - {self._all_portfolio_money():,.2f} ₽"
        )

    @log
    def print_persent_structure_str(self) -> str:
        all_portfolio = self._all_portfolio_money()
        return (
            f"Процентное соотношение:\n"
            f"Акции - {get_percentage_from_element(self.positionsAmt.get(InstrumentType.SHARE), all_portfolio)}\n"
            f"Облигации - {get_percentage_from_element(self.positionsAmt.get(InstrumentType.BOND), all_portfolio)}\n"
            f"Фонды - {get_percentage_from_element(self.positionsAmt.get(InstrumentType.ETF), all_portfolio)}\n"
            f"Валюта и драгметалы - {get_percentage_from_element(self.positionsAmt.get(InstrumentType.CURRENCY), all_portfolio)}\n"
        )

    @log
    def print_all_shares(self):
        shares_data = [
            (position.ticker, get_money(position.current_price) * get_money(position.quantity))
            for position in self.positions.get(InstrumentType.SHARE)
        ]
        shares_data.sort(key=lambda x: x[1], reverse=True)
        lines = [f"<code>{t:<6}</code> — {amt:,.2f} ₽" for t, amt in shares_data]
        return "Акции\n" + "\n".join(lines)

    @log
    def print_all_bonds(self):
        bonds_data = [
            (position.ticker, get_money(position.current_price) * get_money(position.quantity), position.current_nkd)
            for position in self.positions.get(InstrumentType.BOND)
        ]
        bonds_data.sort(key=lambda x: x[1], reverse=True)
        lines = [f"<code>{t:<6}</code> — {amt:,.2f} ₽ - Нкд: {get_money(nkd):,.2f}" for t, amt, nkd in bonds_data]
        return "Облигации\n" + "\n".join(lines)

    @log
    def get_instrument_money(self, positions: list[PortfolioPosition], ticker: str) -> Decimal:
        for position in positions:
            if position.ticker == ticker:
                current_price = get_money(position.current_price)
                quantity = get_money(position.quantity)
                return current_price * quantity
        return Decimal(-1)

    @log
    def _update_free_money(self) -> Decimal:
        free_money = [element for element in self.positions.get(InstrumentType.CURRENCY)
                      if element.ticker == RUB_TICKER][0].quantity
        return get_money(free_money)

    @log
    def _get_all_positions(self, instrument_type: InstrumentType) -> list[PortfolioPosition]:
        return [p for p in self._portfolio.positions if p.instrument_type == instrument_type.value]

    @log
    def _get_all_currencies_positions(self) -> list[PortfolioPosition]:
        return self._get_all_positions(InstrumentType.CURRENCY)

    @log
    def _all_portfolio_money(self) -> Decimal:
        return Decimal(
            (
                get_money(self._portfolio.total_amount_bonds)
                + get_money(self._portfolio.total_amount_etf)
                + get_money(self._portfolio.total_amount_currencies)
                + get_money(self._portfolio.total_amount_shares)
            )
        )
