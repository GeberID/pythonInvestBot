from enum import Enum

from t_tech.invest import PortfolioResponse, MoneyValue

def get_money(money_value:MoneyValue) -> float:
    return float(f"{money_value.units}.{money_value.nano}")

class InstrumentType(Enum):
    SHARE = "share"
    BOND = "bond"
    ETF = "etf"
    CURRENCY = "currency"

class Portfolio:
    def __init__(self, portfolio: PortfolioResponse):
        self._free_money,self._all_currency_positions = self._get_currencies(self, portfolio)
        self._all_shares_positions = self._get_all_positions(portfolio, InstrumentType.SHARE)
        self._all_bonds_positions = self._get_all_positions(portfolio, InstrumentType.BOND)
        self._all_etfs_positions = self._get_all_positions(portfolio, InstrumentType.ETF)
        self._bonds = get_money(portfolio.total_amount_bonds)
        self._etfs = get_money(portfolio.total_amount_etf)
        self._shares = get_money(portfolio.total_amount_shares)
        self._currencies = get_money(portfolio.total_amount_currencies) - self._free_money
        self._all_portfolio = self._bonds + self._etfs + self._currencies + self._shares

    def print_common_portfolio_info(self) -> str:
        return (f"Портфолио:\n"
                f"Акции - {self._shares}\n"
                f"Облигации - {self._bonds}\n"
                f"Фонды - {self._etfs}\n"
                f"Валюта и драгметалы - {self._currencies}\n"
                f"Свободной валюты - {self._free_money}\n"
                f"Всего - {self._all_portfolio}")

    def print_portfolio_structure(self) -> str:
        return (f"Процентное соотношение:\n"
                f"Акции - {self._get_percentage_from_element(self._shares)}\n"
                f"Облигации - {self._get_percentage_from_element(self._bonds)}\n"
                f"Фонды - {self._get_percentage_from_element(self._etfs)}\n"
                f"Валюта и драгметалы - {self._get_percentage_from_element(self._currencies)}\n"
                f"Свободной валюты - {self._get_percentage_from_element(self._free_money)}\n")

    def _get_percentage_from_element(self, money_value:MoneyValue) -> float:
        return (money_value/ self._all_portfolio) * 100.00

    @staticmethod
    def _get_all_positions(portfolio: PortfolioResponse, instrument_type:InstrumentType) ->list[MoneyValue]:
        return [element for element in portfolio.positions if element.instrument_type == instrument_type.value]

    @staticmethod
    def _get_currencies(self, portfolio: PortfolioResponse, ):
        all_currencies_positions = self._get_all_positions(portfolio, InstrumentType.CURRENCY)
        free_money = [element for element in all_currencies_positions if element.ticker == "RUB000UTSTOM"][0].quantity
        return get_money(free_money),all_currencies_positions
