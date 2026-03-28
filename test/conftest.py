import pytest
from t_tech.invest import PortfolioResponse, PortfolioPosition, MoneyValue, Quotation


@pytest.fixture
def fake_portfolio_response() -> PortfolioResponse:
    return PortfolioResponse(
        total_amount_shares=MoneyValue(currency="rub", units=10000, nano=0),
        total_amount_bonds=MoneyValue(currency="rub", units=20000, nano=0),
        total_amount_etf=MoneyValue(currency="rub", units=5000, nano=0),
        total_amount_currencies=MoneyValue(currency="rub", units=1000, nano=0),
        positions=[
            PortfolioPosition(
                ticker="EQMX",
                instrument_type="etf",
                quantity=Quotation(units=10, nano=0),
                current_price=MoneyValue(currency="rub", units=500, nano=0),
                expected_yield=Quotation(units=100, nano=0),
                daily_yield=MoneyValue(currency="rub", units=10, nano=0),
                instrument_uid="uid_etf",
            ),
            PortfolioPosition(
                ticker="GAZP",
                instrument_type="share",
                quantity=Quotation(units=10, nano=0),
                current_price=MoneyValue(currency="rub", units=1000, nano=0),
                expected_yield=Quotation(units=100, nano=0),
                daily_yield=MoneyValue(currency="rub", units=10, nano=0),
                instrument_uid="uid_gazp",
            ),
            PortfolioPosition(
                ticker="SU26244RMFS2",
                instrument_type="bond",
                quantity=Quotation(units=5, nano=0),
                current_price=MoneyValue(currency="rub", units=900, nano=0),
                current_nkd=MoneyValue(currency="rub", units=15, nano=0),
                expected_yield=Quotation(units=50, nano=0),
                daily_yield=MoneyValue(currency="rub", units=0, nano=0),
                instrument_uid="uid_bond_1",
            ),
            PortfolioPosition(
                ticker="RUB000UTSTOM",
                instrument_type="currency",
                quantity=Quotation(units=10, nano=0),
                current_price=MoneyValue(currency="rub", units=1000, nano=0),
                expected_yield=Quotation(units=100, nano=0),
                daily_yield=MoneyValue(currency="rub", units=10, nano=0),
                instrument_uid="uid_currency",
            ),
        ],
        account_id="test_account",
        total_amount_portfolio=MoneyValue(currency="rub", units=36000, nano=0),
    )
