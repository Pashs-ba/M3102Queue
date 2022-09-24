import telegram
import toml

with open("config.toml") as f:
    config = toml.load(f)

bot = telegram.Bot(token=config["token"])
print(bot.get_me())
