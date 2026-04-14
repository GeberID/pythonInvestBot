from decimal import Decimal

from t_tech.invest import PortfolioResponse

from investbot.core.invest_portfolio import InvestPortfolio
from investbot.core.portfolio_instruments import InstrumentData, BondInstrumentData, BondType


def test_portfolio_total_calculation(fake_portfolio_response: PortfolioResponse) -> None:
    portfolio = InvestPortfolio(fake_portfolio_response)
    assert portfolio.total_portfolio == 36000


def test_portfolio_shares(fake_portfolio_response: PortfolioResponse) -> None:
    portfolio = InvestPortfolio(fake_portfolio_response)
    assert len(portfolio.shares) == 1
    gazp = InstrumentData(
        ticker="GAZP",
        money=Decimal(10000.0),
        daily_yield=Decimal(10.0),
        expected_yield=Decimal(100.0),
        percentage_of_portfolio=Decimal(27.78).quantize(Decimal("0.00")),
    )
    assert portfolio.shares[0] == gazp


def test_portfolio_bonds(fake_portfolio_response: PortfolioResponse) -> None:
    portfolio = InvestPortfolio(fake_portfolio_response)
    assert len(portfolio.bonds) == 1
    bond = BondInstrumentData(
        ticker="SU26244RMFS2",
        money=Decimal(4500.0),
        daily_yield=Decimal(0.0),
        expected_yield=Decimal(50.0),
        percentage_of_portfolio=Decimal(12.50).quantize(Decimal("0.00")),
        nkd=Decimal(15.00),
        type=BondType.FIX,
    )
    assert portfolio.bonds[0] == bond
