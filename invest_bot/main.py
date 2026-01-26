import api.tinkoff_api as tinkoff_api
from invest_bot.core.invest import Portfolio


def main():
    account_id = tinkoff_api.get_accounts().accounts[0].id
    portfolio = Portfolio(tinkoff_api.get_portfolio(account_id))
    print(portfolio.print_common_portfolio_info())
    print(portfolio.print_portfolio_structure())

if __name__ == "__main__":
    main()