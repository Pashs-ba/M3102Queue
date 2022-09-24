from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')


app = ApplicationBuilder().token("1339453682:AAH-D0KZ49an5Y4JFMHYSo9ss_TloD2XV3I").build()

app.add_handler(CommandHandler("hello", hello))

app.run_polling()
