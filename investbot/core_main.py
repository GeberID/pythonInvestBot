import asyncio
from typing import NewType

import investbot.core.api.tinkoff_api as api
from investbot.adapters.portfolio_formatter import TelegramPortfolioFormatter
from investbot.core.portfolio.portfolio_adapters.tinkoff_portfolio import TinkoffBrokerAdapter
from investbot.core.strategy.strategy import StrategyAnalyzer, strategy

AccountId = NewType("AccountId", str)


async def main() -> None:
    accounts_resp = await api.get_accounts()
    account_id = AccountId(accounts_resp.accounts[0].id)
    portfolio = TinkoffBrokerAdapter(await api.get_portfolio(account_id=account_id)).fetch_portfolio()
    formater = TelegramPortfolioFormatter(portfolio)
    print(formater.print_common_info_str())
    print(formater.print_all_shares())
    print(formater.print_all_bonds())
    analyzer = StrategyAnalyzer(strategy)
    print(analyzer.analyze(portfolio))


if __name__ == "__main__":
    asyncio.run(main())
