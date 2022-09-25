from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import toml

with open("config.toml") as f:
    config = toml.load(f)

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name, update.effective_user.id}')

async def make_queue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.chat_data['queue'] = []
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Queue created")

async def get_queue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text=context.chat_data['queue'])

async def add_to_queue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.chat_data['queue'].append(update.effective_user.id)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=context.chat_data['queue'])

app = ApplicationBuilder().token(config["token"]).build()

# app.add_handler(CommandHandler("hello", hello))
app.add_handler(CommandHandler('create', make_queue))
app.add_handler(CommandHandler('get', get_queue))
app.add_handler(CommandHandler('add', add_to_queue))
app.run_polling()
