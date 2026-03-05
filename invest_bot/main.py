import asyncio
from typing import NewType

import dp
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

import api.tinkoff_api as api
from invest_bot.configs import TELEGRAM_TOKEN

from invest_bot.core.logs import create_logs_folder, log
from invest_bot.core.invest_portfolio import InvestPortfolio

dp = Dispatcher()
AccountId = NewType("AccountId", str)


@dp.message(CommandStart())
@log
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@dp.message(Command("portfolio"))
@log
async def command_portfolio_handler(message: Message, account_id: str) -> None:
    portfolio = InvestPortfolio(account_id)
    await message.answer(f"{portfolio.print_common_info_str()}\n\n" + f"{portfolio.print_persent_structure_str()}")
    await message.answer(f"{ portfolio.print_all_shares()}")
    await message.answer(f"{ portfolio.print_all_bonds()}")


@log
async def main():
    create_logs_folder()
    account_id = AccountId(api.get_accounts().accounts[0].id)
    bot = Bot(token=TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot, account_id=account_id)
    # print(portfolio.get_instrument_money(portfolio._all_shares_positions, "YDEX"))


if __name__ == "__main__":
    asyncio.run(main())
