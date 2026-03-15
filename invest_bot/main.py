import asyncio
from typing import NewType

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

import invest_bot.api.tinkoff_api as api
from invest_bot.configs import TELEGRAM_TOKEN

from invest_bot.core.log import create_logs_folder, write_log
from invest_bot.core.invest_portfolio import InvestPortfolio

dp = Dispatcher()
AccountId = NewType("AccountId", str)


@dp.message(Command("portfolio"))
@write_log
async def command_portfolio_handler(message: Message, account_id: str) -> None:
    portfolio = InvestPortfolio(api.get_portfolio(account_id=account_id))
    await message.answer(f"{portfolio.print_common_info_str()}\n\n")
    await message.answer(f"{portfolio.print_all_shares()}")
    await message.answer(f"{portfolio.print_all_bonds()}")


@write_log
async def main() -> None:
    create_logs_folder()
    account_id = AccountId(api.get_accounts().accounts[0].id)
    bot = Bot(token=TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot, account_id=account_id)
    # print(portfolio.get_instrument_money(portfolio._all_shares_positions, "YDEX"))


if __name__ == "__main__":
    asyncio.run(main())
