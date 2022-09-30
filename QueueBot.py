from venv import create
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import toml

with open("config.toml") as f:
    config = toml.load(f)

    
async def check_queue(update: Update, context: ContextTypes.DEFAULT_TYPE, key: str, text="Очередь не создана") -> bool:
    if not key in context.chat_data["queue"]:
        await update.message.reply_text(text=text)
        return False
    return True

async def check_user(update: Update, context: ContextTypes.DEFAULT_TYPE, key: str) -> bool:
    if update.effective_user in context.chat_data["queue"][key]:
        await update.message.reply_text(text="Вы уже в очереди")
        return False
    
    return True

async def check_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if str(update.effective_user.id) not in config['admins']:
        await update.message.reply_text(text="Только админ может пользоваться этой функцией.\n БАН БАН БАН")
        return False
    return True


async def add_queue(update, context):
    if not "queue" in context.chat_data:
        context.chat_data["queue"] = dict()
    
    key = update.message.text.partition(' ')[2] or "queue"
    if not (await check_admin(update, context)):
        return
    if key in context.chat_data["queue"]:
        await update.message.reply_text(text="Такая очередь уже создана")
        return False
    context.chat_data['queue'][key] = []
    await update.message.reply_text(f"Queue {key} created!")


async def delete_queue(update, context):
    key = update.message.text.partition(' ')[2] or "queue"
    if not( await check_queue(update, context, key)  and await check_admin(update, context)):
        return
    del context.chat_data["queue"][key]
    await update.message.reply_html(f"Queue {key} deleted!")


async def add_a_person(update, context):
    key = update.message.text.partition(' ')[2] or "queue"
    if not await check_queue(update, context, key):
        return
    if not await check_user(update, context, key):
        return

    user = update.effective_user

    if user not in context.chat_data["queue"][key]:
        context.chat_data['queue'][key].append(user)

    await update.message.reply_text(f"You're the {context.chat_data['queue'][key].index(user) + 1}-th")


async def remove_a_person(update, context):
    key = update.message.text.partition(' ')[2] or "queue"
    if not (await check_queue(update, context, key)):
        return
    if update.effective_user not in context.chat_data["queue"][key]:
        await update.message.reply_text(text="Вас нет в очереди")
        return
    user = update.effective_user

    if user in context.chat_data["queue"][key]:
        context.chat_data["queue"][key].remove(user)
    await update.message.reply_text(f"Done")


async def show_queue(update, context):
    key = update.message.text.partition(' ')[2] or "queue"
    if not await check_queue(update, context, key):
        return

    queue = ""
    for i, j in enumerate(context.chat_data["queue"][key]):
        k = f"{j['first_name']} {j['last_name']}"
        queue += f"{i+1}. {k}\n"

    await update.message.reply_text(queue or "Empty")



async def show_active(update, context):
    queues = ""
    for i, j in enumerate(context.chat_data["queue"]):
        queues += f"{i+1}. {j}\n"
    await update.message.reply_html(queues or "Empty")


if __name__ == "__main__":
    app = ApplicationBuilder().token(config["token"]).build()

    app.add_handler(CommandHandler('create', add_queue))
    app.add_handler(CommandHandler('delete', delete_queue))
    app.add_handler(CommandHandler('add', add_a_person))
    app.add_handler(CommandHandler('show', show_queue))
    app.add_handler(CommandHandler('remove', remove_a_person))
    app.add_handler(CommandHandler("active", show_active))
    app.run_polling()