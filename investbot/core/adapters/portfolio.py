from typing import Protocol

from investbot.core.domain.portfolio_models import InvestPortfolio


class BrokerClient(Protocol):
    def fetch_portfolio(self) -> InvestPortfolio: ...
