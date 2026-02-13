import api.tinkoff_api as api
from invest_bot.core.portfolio import Portfolio


def main():
    account_id = api.get_accounts().accounts[0].id
    portfolio = Portfolio(api.get_portfolio(account_id))
    print(portfolio.print_common_info_str())
    print("\n")
    print(portfolio.print_persent_structure_str())
    print("\n")
    # print(portfolio.get_instrument_money(portfolio._all_shares_positions, "YDEX"))


if __name__ == "__main__":
    main()
