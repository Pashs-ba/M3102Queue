from telegram.ext import Application, CommandHandler
import toml

with open("config.toml") as f:
    config = toml.load(f)


async def check_queue(update, context, key):
    if key not in context.user_data:
        await update.message.reply_text(f"Queue {key} not found")
        return False
    return True


async def add_a_person(update, context):
    key = update.message.text.partition(' ')[2] or "queue"
    if not await check_queue(update, context, key):
        return

    user = update.effective_user

    if user not in context.user_data[key]:
        context.user_data[key] += [user]

    await update.message.reply_text(f"You're the {context.user_data[key].index(user) + 1}-th")


async def remove_a_person(update, context):
    key = update.message.text.partition(' ')[2] or "queue"
    if not await check_queue(update, context, key):
        return

    user = update.effective_user

    if user in context.user_data[key]:
        context.user_data[key].remove(user)
    await update.message.reply_text(f"Done")


async def show_queue(update, context):
    key = update.message.text.partition(' ')[2] or "queue"
    if not await check_queue(update, context, key):
        return

    queue = ""
    for i, j in enumerate(context.user_data[key]):
        k = f"{j['first_name']} {j['last_name']}"
        queue += f"{i+1}. {k}\n"

    await update.message.reply_text(queue or "Empty")


async def add_queue(update, context):
    key = update.message.text.partition(' ')[2] or "queue"
    if await check_queue(update, context, key):
        return

    context.user_data[key] = []
    await update.message.reply_html(f"Queue {key} created!")


async def delete_queue(update, context):
    key = update.message.text.partition(' ')[2] or "queue"
    if not await check_queue(update, context, key):
        return
    del context.user_data[key]
    await update.message.reply_html(f"Queue {key} deleted!")


async def show_active(update, context):
    queues = ""
    for i, j in enumerate(context.user_data):
        queues += f"{i}. {j}\n"
    await update.message.reply_html(queues or "Empty")


def main():
    application = Application.builder().token(config['token']).build()

    application.add_handler(CommandHandler("create", add_queue))
    application.add_handler(CommandHandler("add", add_a_person))
    application.add_handler(CommandHandler("remove", remove_a_person))
    application.add_handler(CommandHandler("show", show_queue))
    application.add_handler(CommandHandler("delete", delete_queue))
    application.add_handler(CommandHandler("active", show_active))

    application.run_polling()


if __name__ == "__main__":
    main()
