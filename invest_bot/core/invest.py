from t_tech.invest import PortfolioResponse, MoneyValue

def get_money(money_value:MoneyValue) -> float:
    return float(f"{money_value.units}.{money_value.nano}")

class Portfolio:
    def __init__(self, portfolio: PortfolioResponse):
        self._bonds = get_money(portfolio.total_amount_bonds)
        self._etfs = get_money(portfolio.total_amount_etf)
        self._shares = get_money(portfolio.total_amount_shares)
        self._currencies = get_money(portfolio.total_amount_currencies)
        self._all_portfolio = self._bonds + self._etfs + self._currencies + self._shares

    def print_common_portfolio_info(self) -> str:
        return (f"Портфолио:\n"
                f"Акции - {self._shares}\n"
                f"Облигации - {self._bonds}\n"
                f"Фонды - {self._etfs}\n"
                f"Валюта - {self._currencies}\n"
                f"Всего - {self._all_portfolio}")

    def print_portfolio_structure(self) -> str:
        return (f"Процентное соотношение:\n"
                f"Акции - {self._get_percentage_from_element(self._shares)}\n"
                f"Облигации - {self._get_percentage_from_element(self._bonds)}\n"
                f"Фонды - {self._get_percentage_from_element(self._etfs)}\n"
                f"Валюта - {self._get_percentage_from_element(self._currencies)}\n")

    def _get_percentage_from_element(self, money_value:MoneyValue) -> float:
        return (money_value/ self._all_portfolio) * 100.00
