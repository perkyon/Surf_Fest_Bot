import asyncio
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import locale
from datetime import datetime, timedelta

# Устанавливаем русскую локаль для получения дня недели на русском языке
locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")

# Вставьте свой токен Telegram-бота здесь
BOT_TOKEN = '6849541159:AAG3lBFxD_E7SVMfXW55gT9F1bnl7FglXPY'

# Инициализируем бота и диспетчер
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

WORKING_START_HOUR = 7
WORKING_END_HOUR = 23

# Постоянные задачи по зонам
tasks = {
    "morning": {
        "food": [
            "пополнить заготовки для фуда и напитков",
            "пополнить гостевые салфетки, трубочки, палочки, сахар",
            "сделать чиа-пудинги",
            "сделать йогурты",
            "проверить температуру холодильников",
            "протереть витрину с выпечкой и десертами",
            "написать хот-лист по продажам"
        ],
        "all": [
            "включить проектор",
            "протереть входную дверь и стекло возле мусора",
            "проверить летник, привести его в порядок",
            "включить тачку/бойлер/гриль",
            "заполнить полки с лимонадами и водой",
            "пополнить все в туалете",
            "протереть все столы"
        ],
        "bar": [
            "сделать фильтр",
            "сделать чай"
        ]
    },
    "shift_change": {
        "all": [
            "слить и наполнить заново посудомойку",
            "вынести мусор (бар/туалет/летник/зона кассы и графина)",
            "проверить чистоту туалета",
            "проверка стеллажа, открытой витрины, зона рядом с кассой на пыль, расстановка и наличие продукции, дополнить.",
            "пополнить одноразки",
            "если была поставка, разложить все по местам и промаркировать",
            "сходить за закупом"
        ],
        "bar": [
            "помыть и натереть всю посуду, расставить по местам",
            "настроить эспрессо",
            "наполнить воду для гостей"
        ],
        "cash": [
            "посчитать кассу",
            "заполнить таблицы"
        ]
    },
    "evening": {
        "bar": [
            "протереть зеркало",
            "снять полотенце и повесить сушиться",
            "помыть раковину",
            "активировать слив в посудомойке, помыть фильтр",
            "постирать и развесить тряпки",
            "помыть фрешницу",
            "проверить чистый ли фильтр",
            "помыть термоподы",
            "помыть холодильники внутри",
            "протереть весы",
            "замочить холдеры",
            "помыть чайники",
            "помыть и поставить сушиться все барные коврики",
            "убрать в холодильник заготовки матчи, основы, концентраты"
        ],
        "all": [
            "поднять стулья и столы",
            "собрать и вынести мусор",
            "протереть от грязи все столы",
            "выключить тачку/гриль/бойлер",
            "протереть поверхность бара"
        ],
        "machine": [
            "помыть кофемолки",
            "помыть ринзер",
            "помыть тачку и продуть форсунки (замочить в растворе)"
        ],
        "food": [
            "сделать заготовку на чиа",
            "занести в таблицу остатки",
            "написать в чат списания/закуп/ос",
            "помыть витрину",
            "накрыть фольгой десерты (которые надо)",
            "помыть микроволновку",
            "выключить/помыть гриль",
            "поставить на зарядку весы/телефон/планшет",
            "проверить с/г на гостевой витрине",
            "достать дефрост",
            "проверить маркировки в холодильнике",
            "протереть холодильники"
        ],
        "cash": [
            "посчитать деньги, произвести сверку итогов",
            "заполнить журналы",
            "проверить температуру холодильников",
            "пополнить предкассовую зону (салфетки, ложки, вилки, сахар) и протереть"
        ]
    }
}

def is_working_hour():
    now = datetime.now()
    hour = now.hour
    return WORKING_START_HOUR <= hour < WORKING_END_HOUR

# Функция для отправки уведомления
async def send_task_notification(chat_id, tasks, period):
    for zone, zone_tasks in tasks.items():
        message = f"Задачи на {period} ({zone}):\n"
        for task in zone_tasks:
            message += f"• {task}\n"
        await bot.send_message(chat_id, message)

async def send_report_reminder(chat_id):
    now = datetime.now()
    if (now.hour == 15 and now.minute == 30) or (now.hour == 23 and now.minute == 30):
        await bot.send_message(chat_id, "Пора написать отчет о выполнении задач на сегодня!")

async def scheduled_task_notifications(chat_id):
    while True:
        now = datetime.now()
        if now.hour == 7 and now.minute == 0:
            await send_task_notification(chat_id, tasks["morning"], "УТРО")
        elif now.hour == 15 and now.minute == 30:
            await send_task_notification(chat_id, tasks["shift_change"], "ПЕРЕСМЕНКА")
        elif now.hour == 23 and now.minute == 0:
            await send_task_notification(chat_id, tasks["evening"], "ВЕЧЕР")
        await asyncio.sleep(60)

async def scheduled_cleanliness_reminders(chat_id):
    while True:
        if is_working_hour():
            await bot.send_message(chat_id, 'Нужно проверить чистоту кофейни')
            await asyncio.sleep(1800)  # Пауза в 30 минут
        else:
            await asyncio.sleep(60)  # Пауза в минуту вне рабочего времени

async def scheduled_report_reminders(chat_id):
    while True:
        await send_report_reminder(chat_id)
        await asyncio.sleep(60)

# Обработчик команды /id
@dp.message_handler(commands=['id'])
async def send_chat_id(message: types.Message):
    chat_id = message.chat.id
    await message.reply(f"ID этого чата: {chat_id}")

if __name__ == '__main__':
    chat_id = '-1002052213905'  # Замените на актуальный chat_id
    loop = asyncio.get_event_loop()
    loop.create_task(scheduled_task_notifications(chat_id))
    loop.create_task(scheduled_cleanliness_reminders(chat_id))
    loop.create_task(scheduled_report_reminders(chat_id))
    executor.start_polling(dp, skip_updates=True)