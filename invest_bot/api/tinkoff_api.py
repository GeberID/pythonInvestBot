from t_tech.invest import PortfolioResponse, Client, GetAccountsResponse

from invest_bot.configs import TINKOFF_TOKEN
from invest_bot.core.logs import log


@log
def get_accounts() -> GetAccountsResponse:
    with Client(token=TINKOFF_TOKEN) as client:
        accounts = client.users.get_accounts()
        return accounts


@log
def get_portfolio(account_id: str) -> PortfolioResponse:
    with Client(token=TINKOFF_TOKEN) as client:
        portfolio = client.operations.get_portfolio(account_id=account_id)
        return portfolio
