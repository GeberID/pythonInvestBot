import api.tinkoff_api as api
from invest_bot.core.invest import Portfolio


def main():
    account_id = api.get_accounts().accounts[0].id
    portfolio = Portfolio(api.get_portfolio(account_id))
    print(portfolio.print_common_portfolio_info())
    print(portfolio.print_portfolio_structure())

if __name__ == "__main__":
    main()