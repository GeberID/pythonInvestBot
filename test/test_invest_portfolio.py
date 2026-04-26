from decimal import Decimal

from t_tech.invest import PortfolioResponse

from investbot.core.portfolio.portfolio_adapters.tinkoff_portfolio import TinkoffBrokerAdapter
from investbot.core.portfolio.portfolio_models.portfolio_models import (
    InstrumentData,
    BondInstrumentData,
    BondType,
)
from investbot.core.base_types import Money, Percentage


def test_portfolio_total_calculation(fake_portfolio_response: PortfolioResponse) -> None:
    portfolio = TinkoffBrokerAdapter(fake_portfolio_response).fetch_portfolio()
    assert portfolio.total_portfolio == 36000


def test_portfolio_shares(fake_portfolio_response: PortfolioResponse) -> None:
    portfolio = TinkoffBrokerAdapter(fake_portfolio_response).fetch_portfolio()
    assert len(portfolio.shares) == 1
    gazp = InstrumentData(
        ticker="GAZP",
        money=Money(Decimal(10000.0)),
        daily_yield=Money(Decimal(10.0)),
        expected_yield=Money(Decimal(100.0)),
        percentage_of_portfolio=Percentage(Decimal(27.78).quantize(Decimal("0.00"))),
    )
    assert portfolio.shares[0] == gazp


def test_portfolio_bonds(fake_portfolio_response: PortfolioResponse) -> None:
    portfolio = TinkoffBrokerAdapter(fake_portfolio_response).fetch_portfolio()
    assert len(portfolio.bonds) == 1
    bond = BondInstrumentData(
        ticker="SU26244RMFS2",
        money=Money(Decimal(4500.0)),
        daily_yield=Money(Decimal(0.0)),
        expected_yield=Money(Decimal(50.0)),
        percentage_of_portfolio=Percentage(Decimal(12.50).quantize(Decimal("0.00"))),
        nkd=Money(Decimal(15.00)),
        type=BondType.FIX,
    )
    assert portfolio.bonds[0] == bond
