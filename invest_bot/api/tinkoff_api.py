from t_tech.invest import Client, PortfolioResponse

from invest_bot.configs import TINKOFF_TOKEN

def get_accounts():
    with Client(token=TINKOFF_TOKEN) as client:
        accounts = client.users.get_accounts()
        return accounts

def get_portfolio(account_id:str) -> PortfolioResponse:
    with Client(token=TINKOFF_TOKEN) as client:
        portfolio = client.operations.get_portfolio(account_id=account_id)
        return portfolio