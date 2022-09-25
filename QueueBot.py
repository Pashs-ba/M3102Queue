from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import toml

with open("config.toml") as f:
    config = toml.load(f)

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')


app = ApplicationBuilder().token(config["token"]).build()

app.add_handler(CommandHandler("hello", hello))

app.run_polling()
