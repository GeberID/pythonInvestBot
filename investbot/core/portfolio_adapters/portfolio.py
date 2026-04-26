from typing import Protocol

from investbot.core.portfolio_models.portfolio_models import InvestPortfolio


class BrokerClient(Protocol):
    def fetch_portfolio(self) -> InvestPortfolio: ...
