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

async def add_to_queue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if 'queue' not in context.chat_data:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Очередь не создана")
        return
    if update.effective_user in context.chat_data['queue']:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Вы уже в очереди")
        return
    context.chat_data['queue'].append(update.effective_user)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{update.effective_user.username} добавлен в группу, место в очереди {len(context.chat_data['queue'])}")

async def show_queue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if 'queue' not in context.chat_data:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Очередь не создана")
        return
    queue = list(map(lambda x: x.username, context.chat_data['queue']))
    data = ""
    for i in range(len(queue)):
        data += f"{i+1}. {queue[i]}\n"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=data)



app = ApplicationBuilder().token(config["token"]).build()

# app.add_handler(CommandHandler("hello", hello))
app.add_handler(CommandHandler('create', make_queue))
app.add_handler(CommandHandler('add', add_to_queue))
app.add_handler(CommandHandler('show', show_queue))
app.run_polling()
