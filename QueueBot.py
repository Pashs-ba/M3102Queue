from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import toml

with open("config.toml") as f:
    config = toml.load(f)

Timeout = 100


class Queue:
    def __init__(self):
        self.__priority = []
        self.__normal = []

    def append(self, obj):
        self.__normal.append(obj)

    def append_priority(self, obj):
        self.__priority.append(obj)

    def show(self):
        queue = ""
        if self.__priority:
            queue += "Приоритет:\n"
            for i, j in enumerate(self.__priority):
                k = f"{j['first_name']} {j['last_name'] or ''}"
                queue += f"{i + 1}. {k}\n"
        if self.__normal:
            queue += "Плебеи:\n"
            for i, j in enumerate(self.__normal):
                k = f"{j['first_name']} {j['last_name'] or ''}"
                queue += f"{i + 1}. {k}\n"
        return queue

    def iter(self):
        return self.__priority + self.__normal

    def index(self, user):
        return self.__normal.index(user)

    def remove(self, user):
        if user in self.__priority:
            self.__priority.remove(user)
        elif user in self.__normal:
            self.__normal.remove(user)

    def count(self):
        return len(self.__normal), len(self.__priority)

    def get(self, index, queue_type="n"):
        if queue_type == "n":
            return self.__normal[index]
        else:
            return self.__priority[index]


async def check_queue(update: Update, context: ContextTypes.DEFAULT_TYPE, key: str, text="Очередь не создана.") -> bool:
    if key not in context.chat_data["queue"]:
        await update.message.reply_text(text=text, read_timeout=Timeout, write_timeout=Timeout,
                                        pool_timeout=Timeout, connect_timeout=Timeout)
        return False
    return True


async def check_user(update: Update, context: ContextTypes.DEFAULT_TYPE, key: str) -> bool:
    if update.effective_user in context.chat_data["queue"][key].iter():
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
    key = update.message.text.split(' ')
    key = "queue" if len(key) < 2 else key[1]
    if not await check_admin(update):
        return
    if key in context.chat_data["queue"]:
        await update.message.reply_text(text="Такая очередь уже создана.", read_timeout=Timeout, write_timeout=Timeout,
                                        pool_timeout=Timeout, connect_timeout=Timeout)
        return
    context.chat_data['queue'][key] = Queue()
    await update.message.reply_text(f"Очередь {key} создана!", read_timeout=Timeout, write_timeout=Timeout,
                                    pool_timeout=Timeout, connect_timeout=Timeout)


async def delete_queue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    key = update.message.text.split(' ')
    if len(key) < 3:
        await update.message.reply_text(f"Нужно подтвердить, что вы хотите удалить очередь.", read_timeout=Timeout,
                                        write_timeout=Timeout,
                                        pool_timeout=Timeout, connect_timeout=Timeout)
        return
    key = key[1]
    if not (await check_queue(update, context, key) and await check_admin(update)):
        return
    del context.chat_data["queue"][key]
    await update.message.reply_text(f"Очередь {key} удалена!", read_timeout=Timeout, write_timeout=Timeout,
                                    pool_timeout=Timeout, connect_timeout=Timeout)


async def add_a_person(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    key = update.message.text.split(' ')
    key = "queue" if len(key) < 2 else key[1]
    if not await check_queue(update, context, key):
        return
    if not await check_user(update, context, key):
        return

    user = update.effective_user

    context.chat_data['queue'][key].append(user)
    await update.message.reply_text(
        f"Вы добавлены в очередь {key}.\n"
        f"Вы находитесь под номером {context.chat_data['queue'][key].index(user) + 1}.", read_timeout=Timeout,
        write_timeout=Timeout, pool_timeout=Timeout, connect_timeout=Timeout)


async def remove_a_person(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    key = update.message.text.split(' ')
    key = "queue" if len(key) < 2 else key[1]
    if not (await check_queue(update, context, key)):
        return

    user = update.effective_user
    if user not in context.chat_data["queue"][key].iter():
        await update.message.reply_text(text="Вас нет в очереди.", read_timeout=Timeout, write_timeout=Timeout,
                                        pool_timeout=Timeout, connect_timeout=Timeout)
        return

    context.chat_data["queue"][key].remove(user)
    await update.message.reply_text(f"Вас больше нет в очереди.", read_timeout=Timeout, write_timeout=Timeout,
                                    pool_timeout=Timeout, connect_timeout=Timeout)


async def show_queue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    key = update.message.text.split(' ')
    key = "queue" if len(key) < 2 else key[1]
    if not await check_queue(update, context, key):
        return

    await update.message.reply_text(context.chat_data["queue"][key].show() or "Пусто.", read_timeout=Timeout,
                                    write_timeout=Timeout,
                                    pool_timeout=Timeout, connect_timeout=Timeout)


async def show_active(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    queues = ""
    for i, j in enumerate(context.chat_data["queue"]):
        queues += f"{i + 1}. {j}\n"
    await update.message.reply_text(queues or "Пусто.", read_timeout=Timeout, write_timeout=Timeout,
                                    pool_timeout=Timeout, connect_timeout=Timeout)


async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f"/create <название> - создаст новую очередь\n"
        f"/delete <название> <любой символ> - удалит очередь\n"
        f"/add <название> - добавит вас в очередь\n"
        f"/remove <название> - удалит вас из очереди\n"
        f"/show <название> - покажет участников очереди\n"
        f"/active - покажет активные очереди\n"
        f"/all - пинганёт всех участников\n"
        f"/push <название очереди> <индекс в очереди> - добавит в приоритетную очередь\n"
        f"/force <название очереди> [p/n] <индекс в очереди> - удалит человека из (p) приоритетной или (n) обычной очереди\n"
        f"/ping [add/remove/show] <id пользователей через пробел> - добавит/удалит/покажет пользователей, которых нужно пинговать\n"
        f"/dump - перезапишет конфиг\n"
        f"/help - покажет это сообщение\n"
        f"Если не указывать <название>, то автоматически будет выбрано название queue\n", read_timeout=Timeout,
        write_timeout=Timeout, pool_timeout=Timeout, connect_timeout=Timeout)


async def ping_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_admin(update):
        return

    to_ping = "Что-то важненькое происходит! " + " ".join([i for i in config['ID_to_ping']])
    await update.message.reply_text(to_ping, read_timeout=Timeout,
                                    write_timeout=Timeout, pool_timeout=Timeout, connect_timeout=Timeout)


async def change_ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_admin(update):
        return

    key = update.message.text.split(' ')  # /add_ping add @id1 @id2 @id3
    if key[1] == "add":
        config['ID_to_ping'] += key[2:]
        await update.message.reply_text(text="Добавлено.", read_timeout=Timeout, write_timeout=Timeout,
                                        pool_timeout=Timeout, connect_timeout=Timeout)
    elif key[1] == "remove":
        for i in key[2:]:
            config['ID_to_ping'].remove(i)
        await update.message.reply_text(text="Удалено.", read_timeout=Timeout, write_timeout=Timeout,
                                        pool_timeout=Timeout, connect_timeout=Timeout)
    elif key[1] == "show":
        # print without @ so [1:]
        await update.message.reply_text(text=" ".join([i[1:] for i in config['ID_to_ping']]), read_timeout=Timeout,
                                        write_timeout=Timeout, pool_timeout=Timeout, connect_timeout=Timeout)

async def dump_config(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_admin(update):
        return

    #dump to toml
    with open("config.toml", "w") as f:
        toml.dump(config, f)

    await update.message.reply_text(text="Конфиг сохранён.", read_timeout=Timeout, write_timeout=Timeout,
                                    pool_timeout=Timeout, connect_timeout=Timeout)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if "queue" not in context.chat_data:
        context.chat_data["queue"] = dict()
    await update.message.reply_text("*звуки успешной активации*")


async def push_a_person(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    key = update.message.text.split(' ')
    if len(key) < 3:
        await update.message.reply_text(text="Неправильны формат ввода.", read_timeout=Timeout, write_timeout=Timeout,
                                        pool_timeout=Timeout, connect_timeout=Timeout)
        return
    if not await check_admin(update):
        return
    queue = key[1]
    index = key[2]
    if not index.isnumeric():
        await update.message.reply_text(text="Такого индекса нет.", read_timeout=Timeout, write_timeout=Timeout,
                                        pool_timeout=Timeout, connect_timeout=Timeout)
        return
    index = int(index)

    if not (await check_queue(update, context, queue)):
        return

    if 0 > index or index > context.chat_data["queue"][queue].count()[0]:
        await update.message.reply_text(text="Такого индекса нет.", read_timeout=Timeout, write_timeout=Timeout,
                                        pool_timeout=Timeout, connect_timeout=Timeout)
        return

    cur_queue = context.chat_data["queue"][queue]
    person = cur_queue.get(index - 1)
    cur_queue.remove(person)
    cur_queue.append_priority(person)
    await update.message.reply_text(
        text=f"{person['first_name']} {person['last_name'] or ''} перенесён в приоритетную очередь",
        read_timeout=Timeout,
        write_timeout=Timeout,
        pool_timeout=Timeout, connect_timeout=Timeout)


async def force_remove(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    key = update.message.text.split(' ')
    if len(key) < 4:
        await update.message.reply_text(text="Неправильны формат ввода.", read_timeout=Timeout, write_timeout=Timeout,
                                        pool_timeout=Timeout, connect_timeout=Timeout)
        return
    if not await check_admin(update):
        return

    queue = key[1]
    type_of_queue = key[2]
    index = key[3]
    if not index.isnumeric():
        await update.message.reply_text(text="Такого индекса нет.", read_timeout=Timeout, write_timeout=Timeout,
                                        pool_timeout=Timeout, connect_timeout=Timeout)
        return
    index = int(index)
    if type_of_queue not in ("p", "n"):
        await update.message.reply_text(text="Такого ключа нет.", read_timeout=Timeout, write_timeout=Timeout,
                                        pool_timeout=Timeout, connect_timeout=Timeout)
        return
    if 0 > index or index > context.chat_data["queue"][queue].count()[type_of_queue == "p"]:
        await update.message.reply_text(text="Такого индекса нет.", read_timeout=Timeout, write_timeout=Timeout,
                                        pool_timeout=Timeout, connect_timeout=Timeout)
        return

    cur_queue = context.chat_data["queue"][queue]
    person = cur_queue.get(index - 1, type_of_queue)
    cur_queue.remove(person)
    await update.message.reply_text(
        text=f"{person['first_name']} {person['last_name'] or ''} удалён",
        read_timeout=Timeout,
        write_timeout=Timeout,
        pool_timeout=Timeout, connect_timeout=Timeout)


if __name__ == "__main__":
    app = ApplicationBuilder().token(config["token"]).build()

    app.add_handler(CommandHandler('create', add_queue))
    app.add_handler(CommandHandler('delete', delete_queue))
    app.add_handler(CommandHandler('add', add_a_person))
    app.add_handler(CommandHandler('show', show_queue))
    app.add_handler(CommandHandler('remove', remove_a_person))
    app.add_handler(CommandHandler("active", show_active))
    app.add_handler(CommandHandler("help", show_help))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("all", ping_all))
    app.add_handler(CommandHandler("push", push_a_person))
    app.add_handler(CommandHandler("force", force_remove))
    app.add_handler(CommandHandler("ping", change_ping))
    app.add_handler(CommandHandler("dump", dump_config))

    app.run_polling()
