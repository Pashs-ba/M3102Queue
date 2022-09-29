from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, Updater
import toml
from uuid import uuid4

with open("config.toml") as f:
    config = toml.load(f)


async def a(update, context):
    key = context.args[0]
    if key in context.user_data:

        user = update.effective_user
        us = f"{user['first_name']} {user['last_name']}"

        if us not in context.user_data[key]:
            context.user_data[key] += [us]

        await update.message.reply_text(f"You're the {context.user_data[key].index(us)}-th")
    else:
        await update.message.reply_text(f"Queue {key} not found")


async def r(update, context):
    key = context.args[0]
    if key in context.user_data:

        user = update.effective_user
        us = f"{user['first_name']} {user['last_name']}"

        if us in context.user_data[key]:
            context.user_data[key] -= [us]
        await update.message.reply_text(f"Removed")

    else:
        await update.message.reply_text(f"Queue {key} not found")


async def show(update, context):
    pass


async def AddQueue(update, context) -> None:
    key = context.args[0]
    context.user_data[key] = []

    await update.message.reply_html(rf"Queue {key} created!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(update.message.text)


def main() -> None:
    application = Application.builder().token(config['token']).build()

    application.add_handler(CommandHandler("create", AddQueue))
    application.add_handler(CommandHandler("a", a))
    application.add_handler(CommandHandler("r", r))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    application.run_polling()


#    updater.idle()


if __name__ == "__main__":
    main()
