from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import toml

config = toml.load("config.toml")

Timeout = 100


class Queue:
    def __init__(self):
        self._normal = []
        self._priority = []

    def __iter__(self):
        return iter(self._priority + self._normal)

    def __contains__(self, user):
        return user in self._normal or user in self._priority

    def __str__(self):
        return "Приоритет:\n" + "\n".join(
            f"{i}. {user['first_name']} {user['last_name'] or ''}" for i, user in enumerate(self._priority, 1)
        ) + "\nОбычные:\n" + "\n".join(
            f"{i}. {user['first_name']} {user['last_name'] or ''}" for i, user in enumerate(self._normal, 1)
        )

    def append(self, user, priority=False):
        if priority:
            self._priority.append(user)
            return len(self._priority)
        else:
            self._normal.append(user)
            return len(self._normal) + len(self._priority)

    def remove(self, user):
        if user in self._priority:
            self._priority.remove(user)
        elif user in self._normal:
            self._normal.remove(user)


# CONFIG
def add_to_config(user) -> None:
    if user in config['users']:
        return
    config['users'][user.username] = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'id': user.id
    }
    with open('config.toml', 'w') as f:
        toml.dump(config, f)


# CHECKS

async def check_queue_exists(update: Update, context: ContextTypes.DEFAULT_TYPE, key: str) -> bool:
    if key not in context.chat_data["queue"]:
        await update.message.reply_text(text="Очередь не создана.", read_timeout=Timeout, write_timeout=Timeout,
                                        pool_timeout=Timeout,
                                        connect_timeout=Timeout)
        return False
    return True


async def check_user_in_queue(update: Update, context: ContextTypes.DEFAULT_TYPE, key: str, username: str) -> bool:
    user = config['users'][username]
    if user in context.chat_data["queue"][key]:
        await update.message.reply_text(text="Вы уже в очереди.", read_timeout=Timeout, write_timeout=Timeout,
                                        pool_timeout=Timeout, connect_timeout=Timeout)
        return False
    return True


async def check_admin(update: Update) -> bool:
    if str(update.effective_user.id) not in config['admins']:
        await update.message.reply_text(text="Только админ может пользоваться этой функцией.", read_timeout=Timeout,
                                        write_timeout=Timeout, pool_timeout=Timeout, connect_timeout=Timeout)
        return False
    return True


def check_in_base(username: str) -> bool:
    return username in config['users']


# WORK WITH QUEUE

async def add_queue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    key = update.message.text.split(' ')
    key = "queue" if len(key) < 2 else key[1]

    if not await check_admin(update):
        return
    if key in context.chat_data["queue"]:
        await update.message.reply_text(text="Такая очередь уже создана.", read_timeout=Timeout, write_timeout=Timeout,
                                        pool_timeout=Timeout, connect_timeout=Timeout)
        return
    context.chat_data["queue"][key] = Queue()
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
    if not (await check_queue_exists(update, context, key) and await check_admin(update)):
        return
    del context.chat_data["queue"][key]
    await update.message.reply_text(f"Очередь {key} удалена!", read_timeout=Timeout, write_timeout=Timeout,
                                    pool_timeout=Timeout, connect_timeout=Timeout)


async def show_queue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    key = update.message.text.split(' ')
    key = "queue" if len(key) < 2 else key[1]

    if not await check_queue_exists(update, context, key):
        return

    await update.message.reply_text(str(context.chat_data["queue"][key]), read_timeout=Timeout,
                                    write_timeout=Timeout,
                                    pool_timeout=Timeout, connect_timeout=Timeout)


async def show_active(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    queues = ""
    for i, j in enumerate(context.chat_data["queue"]):
        queues += f"{i + 1}. {j}\n"
    await update.message.reply_text(queues or "Пусто.", read_timeout=Timeout, write_timeout=Timeout,
                                    pool_timeout=Timeout, connect_timeout=Timeout)


# WORK WITH USER

async def many_checks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> tuple:
    key = update.message.text.split(' ')
    queue_name, username, *_ = *key[1:], None, None

    if not queue_name:
        queue_name = "queue"
    if not (await check_queue_exists(update, context, queue_name)):
        return None, None, None

    if username and not await check_admin(update):
        return None, None, None

    if not username:
        username = update.effective_user.username
        if not check_in_base(username):
            add_to_config(update.effective_user)

    username = username[1:] if username[0] == '@' else username
    if not check_in_base(username):
        await update.message.reply_text(text="Пользователь не найден.", read_timeout=Timeout, write_timeout=Timeout,
                                        pool_timeout=Timeout, connect_timeout=Timeout)
        return None, None, None

    return config['users'][username], queue_name, username


async def add_a_person(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user, queue_name, username = await many_checks(update, context)
    if (user, queue_name, username) == (None, None, None):
        return
    if not await check_user_in_queue(update, context, queue_name, username):
        return

    index = context.chat_data["queue"][queue_name].append(user)
    person = "Вы" if not username else f"{user['first_name']} {user['last_name'] or ''}"
    await update.message.reply_text(
        f"{person} добавлены в очередь {queue_name} на {index} место.",
        read_timeout=Timeout, write_timeout=Timeout,
        pool_timeout=Timeout, connect_timeout=Timeout)


async def remove_a_person(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user, queue_name, username = await many_checks(update, context)
    if (user, queue_name, username) == (None, None, None):
        return
    person = f"{user['first_name']} {user['last_name'] or ''}"

    if user not in context.chat_data["queue"][queue_name]:
        await update.message.reply_text(f"{person} нет в очереди.", read_timeout=Timeout, write_timeout=Timeout,
                                        pool_timeout=Timeout, connect_timeout=Timeout)
        return

    context.chat_data["queue"][queue_name].remove(user)
    await update.message.reply_text(f"{person} больше нет в очереди.", read_timeout=Timeout, write_timeout=Timeout,
                                    pool_timeout=Timeout, connect_timeout=Timeout)


async def push_to_priority(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user, queue_name, username = await many_checks(update, context)
    if (user, queue_name, username) == (None, None, None):
        return
    person = f"{user['first_name']} {user['last_name'] or ''}"

    if user not in context.chat_data["queue"][queue_name]:
        await update.message.reply_text(f"{person} нет в очереди.", read_timeout=Timeout, write_timeout=Timeout,
                                        pool_timeout=Timeout, connect_timeout=Timeout)
        return

    context.chat_data["queue"][queue_name].remove(user)
    context.chat_data["queue"][queue_name].append(user, True)
    await update.message.reply_text(f"{person} в приоритете.", read_timeout=Timeout, write_timeout=Timeout,
                                    pool_timeout=Timeout, connect_timeout=Timeout)


# OTHER STUFF

async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f"/create <название> - создаст новую очередь\n"
        f"/delete <название> <любой символ> - удалит очередь\n"
        f"/add <название> <@us_name> - добавит вас в очередь\n"
        f"/remove <название> <@us_name> - удалит вас из очереди\n"
        f"/push <название> <@us_name> - добавит вас в приоритет\n"
        f"/show <название> - покажет участников очереди\n"
        f"/active - покажет активные очереди\n"
        f"/all - пинганёт всех участников\n"
        f"/help - покажет это сообщение\n"
        f"Если не указывать <название>, то автоматически будет выбрано название queue\n"
        f"Если не указывать <@us_name>, то будет выбрано username вводившего", read_timeout=Timeout,
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

    await update.message.reply_text("*звуки успешной активации*")


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
    app.add_handler(CommandHandler("push", push_to_priority))

    app.run_polling()
