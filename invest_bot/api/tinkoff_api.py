from t_tech.invest import PortfolioResponse, AsyncClient

from invest_bot.configs import TINKOFF_TOKEN


async def get_accounts():
    async with AsyncClient(token=TINKOFF_TOKEN) as client:
        accounts = client.users.get_accounts()
        return await accounts


async def get_portfolio(account_id: str) -> PortfolioResponse:
    async with AsyncClient(token=TINKOFF_TOKEN) as client:
        portfolio = client.operations.get_portfolio(account_id=account_id)
        return await portfolio
