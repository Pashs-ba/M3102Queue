import telebot
from telebot import types

names = [
  "забабус",
  "забабус",
  "забашт",
  "атшта",
  "атшт",
  "атшт",
  "забабаз",
  "забабаз",
  "забаштанчик",
  "забаштанчик",
]

love = [
  "любим",
  "дорогой",
  "бесценны",
  "любезн",
]

id = "@azabashta"

token = ""
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start_message(message):
  bot.send_message(message.chat.id,"Привет ✌️ ")


@bot.message_handler(content_types='text')
def message_reply(message):
  words = message.text.split()

  if id in message.text:
    bot.send_message(message.chat.id,"йоу")
    if "pakistan" in words:
      bot.send_message(message.chat.id, "не знаю, можно в Chat Gpt спросить")
    return


  if any(name in message.text.lower() for name in names):
    bot.send_message(message.chat.id,"ЧЕ НАДО?")
    return

  if any(word in message.text.lower() for word in ["чзх", "втф", "wtf"]):
    bot.send_message(message.chat.id,"никита.....")
    return

  if any(word in message.text.lower() for word in love):
    bot.send_message(message.chat.id,"да, я, вопросы?")
    return

bot.infinity_polling()