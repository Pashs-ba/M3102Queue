from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
import toml

with open("config.toml") as f:
    config = toml.load(f)

Timeout = 100


async def check_queue(update: Update, context: ContextTypes.DEFAULT_TYPE, key: str, text="Очередь не создана.") -> bool:
    if key not in context.chat_data["queue"]:
        await update.message.reply_text(text=text, read_timeout=Timeout, write_timeout=Timeout,
                                        pool_timeout=Timeout, connect_timeout=Timeout)
        return False
    return True


async def check_user(update: Update, context: ContextTypes.DEFAULT_TYPE, key: str) -> bool:
    if update.effective_user in context.chat_data["queue"][key]:
        await update.message.reply_text(text="Вы уже в этой очереди.", read_timeout=Timeout, write_timeout=Timeout,
                                        pool_timeout=Timeout, connect_timeout=Timeout)
        return False

    return True


async def check_admin(update: Update) -> bool:
    if str(update.effective_user.id) not in config['admins']:
        await update.message.reply_text(text="Только админ может пользоваться этой функцией.", read_timeout=Timeout,
                                        write_timeout=Timeout, pool_timeout=Timeout, connect_timeout=Timeout)
        return False
    return True


async def add_queue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    key = update.message.text.partition(' ')[2] or "queue"
    if not await check_admin(update):
        return
    if key in context.chat_data["queue"]:
        await update.message.reply_text(text="Такая очередь уже создана.", read_timeout=Timeout, write_timeout=Timeout,
                                        pool_timeout=Timeout, connect_timeout=Timeout)
        return
    context.chat_data['queue'][key] = []
    await update.message.reply_text(f"Очередь {key} создана!", read_timeout=Timeout, write_timeout=Timeout,
                                    pool_timeout=Timeout, connect_timeout=Timeout)


async def delete_queue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    key = update.message.text.partition(' ')[2] or "queue"
    if not (await check_queue(update, context, key) and await check_admin(update)):
        return
    del context.chat_data["queue"][key]
    await update.message.reply_text(f"Очередь {key} удалена!", read_timeout=Timeout, write_timeout=Timeout,
                                    pool_timeout=Timeout, connect_timeout=Timeout)


async def add_a_person(update: Update, context: ContextTypes.DEFAULT_TYPE, name_of_queue="") -> None:
    if not name_of_queue:
        key = update.message.text.partition(' ')[2] or "queue"
    else:
        key = name_of_queue
    if not await check_queue(update, context, key):
        return
    if not await check_user(update, context, key):
        return

    user = update.effective_user

    if user not in context.chat_data["queue"][key]:
        context.chat_data['queue'][key].append(user)

    await update.message.reply_text(
        f"Вы добавлены в очередь {key}.\n"
        f"Вы находитесь под номером {context.chat_data['queue'][key].index(user) + 1}.", read_timeout=Timeout,
        write_timeout=Timeout, pool_timeout=Timeout, connect_timeout=Timeout)


async def remove_a_person(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    key = update.message.text.partition(' ')[2] or "queue"

    if not (await check_queue(update, context, key)):
        return
    if update.effective_user not in context.chat_data["queue"][key]:
        await update.message.reply_text(text="Вас нет в очереди.", read_timeout=Timeout, write_timeout=Timeout,
                                        pool_timeout=Timeout, connect_timeout=Timeout)
        return
    user = update.effective_user

    if user in context.chat_data["queue"][key]:
        context.chat_data["queue"][key].remove(user)
    await update.message.reply_text(f"Вас больше нет в очереди.", read_timeout=Timeout, write_timeout=Timeout,
                                    pool_timeout=Timeout, connect_timeout=Timeout)


async def show_queue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    key = update.message.text.partition(' ')[2] or "queue"
    if not await check_queue(update, context, key):
        return

    queue = ""
    for i, j in enumerate(context.chat_data["queue"][key]):
        k = f"{j['first_name']} {j['last_name'] or ''}"
        queue += f"{i + 1}. {k}\n"

    keyword = [[InlineKeyboardButton("Встать в очередь.", callback_data=' '.join(["add", key]))]] # callback_data string only

    await update.message.reply_text(queue or "Пусто.", reply_markup=InlineKeyboardMarkup(keyword), read_timeout=Timeout,
                                        write_timeout=Timeout,
                                        pool_timeout=Timeout, connect_timeout=Timeout)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    option, key = query.data.split(' ')
    if option == "add":
        # await add_a_person(update, context, key, output_needed=False)
        await query.answer(text="Кнопка не работает", show_alert=False, read_timeout=Timeout, write_timeout=Timeout, pool_timeout=Timeout, connect_timeout=Timeout)


async def show_active(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    queues = ""
    for i, j in enumerate(context.chat_data["queue"]):
        queues += f"{i + 1}. {j}\n"
    await update.message.reply_text(queues or "Пусто.", read_timeout=Timeout, write_timeout=Timeout,
                                    pool_timeout=Timeout, connect_timeout=Timeout)


async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f"/create <название> - создаст новую очередь\n"
        f"/delete <название> - удалит очередь\n"
        f"/add <название> - добавит вас в очередь\n"
        f"/remove <название> - удалит вас из очереди\n"
        f"/show <название> - покажет участников очереди\n"
        f"/active - покажет активные очереди\n"
        f"/help - покажет это сообщение\n"
        f"Если не указывать <название>, то автоматически будет выбрано название queue", read_timeout=Timeout,
        write_timeout=Timeout, pool_timeout=Timeout, connect_timeout=Timeout)


async def ping_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_admin(update):
        return

    to_ping = "Что-то важненькое происходит! " + " ".join([i for i in config['ID_to_ping']])
    await update.message.reply_text(to_ping, read_timeout=Timeout,
                                    write_timeout=Timeout, pool_timeout=Timeout, connect_timeout=Timeout)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if "queue" not in context.chat_data:
        context.chat_data["queue"] = dict()
    await update.message.reply_text("*Звуки успешной активации*", read_timeout=Timeout,
                                    write_timeout=Timeout, pool_timeout=Timeout, connect_timeout=Timeout)

if __name__ == "__main__":
    app = ApplicationBuilder().token(config["token"]).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("all", ping_all))
    app.add_handler(CommandHandler("help", show_help))
    app.add_handler(CommandHandler('show', show_queue))
    app.add_handler(CommandHandler('add', add_a_person))
    app.add_handler(CommandHandler('create', add_queue))
    app.add_handler(CommandHandler("active", show_active))
    app.add_handler(CommandHandler('delete', delete_queue))
    app.add_handler(CommandHandler('remove', remove_a_person))

    app.add_handler(CallbackQueryHandler(button))

    app.run_polling()
