import telegram
import toml
import asyncio

with open("config.toml") as f:
    config = toml.load(f)


async def main():
    bot = telegram.Bot(token=config["token"])
    print(await bot.get_me())


asyncio.get_event_loop().run_until_complete(main())
