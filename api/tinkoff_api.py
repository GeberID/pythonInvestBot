from t_tech.invest import PortfolioResponse, Client, GetAccountsResponse

from configs import TINKOFF_TOKEN
from core.log import write_log


@write_log
async def get_accounts() -> GetAccountsResponse:
    with Client(token=TINKOFF_TOKEN) as client:
        accounts = client.users.get_accounts()
        return accounts


@write_log
async def get_portfolio(account_id: str) -> PortfolioResponse:
    with Client(token=TINKOFF_TOKEN) as client:
        portfolio = client.operations.get_portfolio(account_id=account_id)
        return portfolio
