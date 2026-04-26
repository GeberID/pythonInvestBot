import asyncio
import investbot.core.api.tinkoff_api as api
from typing import NewType

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

from investbot.configs import TELEGRAM_TOKEN, PROXY_TELEGRAM
from investbot.core.portfolio.portfolio_models.portfolio_models import InvestPortfolio
from investbot.core.portfolio.portfolio_adapters.tinkoff_portfolio import TinkoffBrokerAdapter
from investbot.core.log import write_log
from investbot.core.strategy.strategy import StrategyAnalyzer, strategy
from investbot.adapters.portfolio_formatter import TelegramPortfolioFormatter

dp = Dispatcher()
AccountId = NewType("AccountId", str)


@dp.message(Command("portfolio"))
@write_log
async def command_portfolio_handler(message: Message, account_id: str) -> None:
    telegram_formatter = TelegramPortfolioFormatter(await fetch_portfolio(account_id))
    await message.answer(f"{telegram_formatter.print_common_info_str()}\n\n")
    await message.answer(f"{telegram_formatter.print_all_shares()}")
    await message.answer(f"{telegram_formatter.print_all_bonds()}")


@dp.message(Command("analyze"))
@write_log
async def command_analyze_handler(message: Message, account_id: str) -> None:
    portfolio = await fetch_portfolio(account_id)
    analyzer = StrategyAnalyzer(strategy)
    analyze_result = analyzer.analyze(portfolio)
    print(analyze_result)


@write_log
async def start() -> None:
    session = AiohttpSession(timeout=300, proxy=PROXY_TELEGRAM)
    accounts_resp = await api.get_accounts()
    account_id = AccountId(accounts_resp.accounts[0].id)
    bot = Bot(token=TELEGRAM_TOKEN, session=session, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot, account_id=account_id)
    # print(portfolio.get_instrument_money(portfolio._all_shares_positions, "YDEX"))


async def fetch_portfolio(account_id: str) -> InvestPortfolio:
    data = await api.get_portfolio(account_id=account_id)
    return TinkoffBrokerAdapter(data).fetch_portfolio()


def main() -> None:
    try:
        asyncio.run(start())
    except KeyboardInterrupt:
        print("Бот остановлен пользователем")


if __name__ == "__main__":
    main()
