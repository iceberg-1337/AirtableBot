import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from pyairtable import Base, Table

api_key = 'API_KEY'
bot = Bot(token="BOT_Token")

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO)


class Check(StatesGroup):
    check = State()


class Find(StatesGroup):
    find = State()


class CheckVerify(StatesGroup):
    check = State()


class FindVerify(StatesGroup):
    find = State()


class Menu(StatesGroup):
    menu = State()


check_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
back = '↩ Назад ↩'
ok = '✅ Все верно ✅'
again = '🔄 Ввести заново 🔄'

check_menu.add(again)
check_menu.add(back, ok)


@dp.message_handler(commands="start")
async def welcome(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = ['Проверить текст', 'Найти райтера']
    keyboard.add(*buttons)
    await message.answer("Добро пожаловать!\nЧто хотите сделать?", reply_markup=keyboard)


@dp.message_handler(commands="tables")
async def tables(message: types.Message):
    await message.answer('<b>Табличка с райтерами:</b>\n'
                         'https://airtable.com/shrYRG0aDGDZVIyqM\n\n'
                         '<b>Табличка с расшифровщиками:</b>'
                         'https://airtable.com/shrLvAUQoUuSO5o0r\n\n'
                         '<b>Черный список:</b>'
                         'https://airtable.com/shrIsxGNwih9EPqwb\n\n'
                         '<b>Табличка с корректорами (будет пополняться):</b>'
                         'https://airtable.com/shrgsYLzhAr4yifTT\n\n'
                         '<b>Табличка с райтерами на тест:</b>'
                         'https://airtable.com/shrldFcxVQpVSv7NG\n\n'
                         '<b>Памятка с брифом для райтера:</b>'
                         'https://docs.google.com/document/d/1aJbufcnXa7bjpcoqULIaNrR5KauPugmibnQT2xuzfy8/edit#heading=h.ep89xw7idfw2\n\n'
                         '<b>Гайд по тезпланам:</b>'
                         ' https://docs.google.com/document/d/18CAsEpWBieqg_qHtUcApl6mjQW4H2s0g1jYpOgqDvwk/edit?usp=sharing\n\n',
                         parse_mode='html'
                         )


@dp.message_handler(lambda message: message.text == "Проверить текст")
async def text(message: types.Message):
    await message.answer('Введите все данные в формате\n'
                         'Текст:\n'
                         'Клиент:\n'
                         'СМИ:\n'
                         'Дата сдачи менеджеру (в формате 15.04.2022):\n'
                         'Райтер:\n'
                         'Менеджер:\n'
                         'Количество символов:\n'
                         'Ссылка на текст:\n'
                         )
    await Check.check.set()


@dp.message_handler(lambda message: message.text == "Найти райтера")
async def check(message: types.Message):
    await message.answer('Введите все данные в формате\n'
                         'Название материала:\n'
                         'Клиент:\n'
                         'СМИ:\n'
                         'Менеджер:\n'
                         'К какому сроку найти:\n'
                         'Комментарий/бриф(можно многострочный)')
    await Find.find.set()


@dp.message_handler(state=Check.check)
async def text(message: types.Message, state: FSMContext):
    global records
    values = message.text.split('\n')
    if len(values) != 8:
        await message.answer('Похоже вы ввели не все данные \nПопробуйте еще раз')
        await message.answer('<em><b>Пример ввода данных:</b></em>', parse_mode='html')
        await message.answer('Метавсленная\nСколково\nПопмех\n25.03.2022\nАня\nАлла\n3214\ndocs.google.com')
        await Check.check.set()
    else:
        values.append(values[0] + ' ' + values[1] + ' ' + values[2])
        date = values[3]
        new_date = date.split('.')
        try:
            new_date = new_date[2] + '-' + new_date[1] + '-' + new_date[0]
            values[3] = new_date
            keys = ['Название', 'Клиент', 'СМИ', 'Сдача менеджеру', 'Райтер', 'Менеджер', 'Количество символов',
                    'Ссылка на текст', 'Саммари']
            records = dict(zip(keys, values))

            await message.answer(
                'Проверьте правильность ввода:\n'
                + '<b>Текст - </b>' + values[0] + '\n'
                + '<b>Клиент - </b>' + values[1] + '\n'
                + '<b>СМИ - </b>' + values[2] + '\n'
                + '<b>Дата сдачи менеджеру - </b>' + date + '\n'
                + '<b>Райтер - </b>' + values[4] + '\n'
                + '<b>Менеджер - </b>' + values[5] + '\n'
                + '<b>Количество символов - </b>' + values[6] + '\n'
                + '<b>Ссылка на текст - </b>' + values[7] + '\n',
                parse_mode='html', reply_markup=check_menu)

            await CheckVerify.check.set()

        except IndexError:
            await message.answer('Вводите дату в правильном формате')
            await message.answer('<em><b>Пример ввода данных:</b></em>', parse_mode='html')
            await message.answer('Метавсленная\nСколково\nПопмех\n25.03.2022\nАня\nАлла\n3214\ndocs.google.com')
            await Check.check.set()


@dp.message_handler(state=CheckVerify.check)
async def text(message: types.Message, state: FSMContext):
    if message.text == '✅ Все верно ✅':
        base = Base(api_key, 'appwuAIlKJxXX7doG')

        March = 'tblUCepR5Yjo0BRod'
        April = 'tbls6rXCfInJlat7x'
        May = 'tblqo6OYIbM7OdUsZ'
        June = 'tblgLiya3yRHwqlFN'
        July = 'tblVy52cLTpGtoskx'
        August = 'tblAWPFe7PvdpTJm4'
        September = 'tblhnsRX0TAZzlNKv'
        October = 'tblZATgeU917anRt9'
        November = 'tblaY3xacc7ZMsuB6'
        December = 'tblNqV3cUDI7YuSWo'

        date = records.get('Сдача менеджеру').split('-')
        mounth = date[1]

        if mounth == '03':
            base.create(March, records)
        elif mounth == '04':
            base.create(April, records)
        elif mounth == '05':
            base.create(May, records)
        elif mounth == '06':
            base.create(June, records)
        elif mounth == '07':
            base.create(July, records)
        elif mounth == '08':
            base.create(August, records)
        elif mounth == '09':
            base.create(September, records)
        elif mounth == '10':
            base.create(October, records)
        elif mounth == '11':
            base.create(November, records)
        elif mounth == '12':
            base.create(December, records)

        await message.answer('Данные отправлены в AirTable')
        await state.finish()
        await welcome(message)
        global chat_id
        chat_id = message.chat.id
        markup = types.InlineKeyboardMarkup()
        ok = types.InlineKeyboardButton('🔥 все ок 🔥', callback_data='ok')
        good = types.InlineKeyboardButton('👌 пара правок 👌', callback_data='good')
        bad = types.InlineKeyboardButton('❗ много правок ❗', callback_data='bad')
        awful = types.InlineKeyboardButton('⛔ все плохо ⛔', callback_data='awful')

        markup.add(ok, good)
        markup.add(bad, awful)

        date = records.get('Сдача менеджеру').split('-')
        new_date = date[2] + '.' + date[1] + '.' + date[0]
        await bot.send_message(-1001644325585, '<b>Текст - </b>' + records.get('Название') + '\n'
                               + '<b>Клиент - </b>' + records.get('Клиент') + '\n'
                               + '<b>СМИ - </b>' + records.get('СМИ') + '\n'
                               + '<b>Дата сдачи менеджеру - </b>' + new_date + '\n'
                               + '<b>Райтер - </b>' + records.get('Райтер') + '\n'
                               + '<b>Менеджер - </b>' + records.get('Менеджер') + '\n'
                               + '<b>Количество символов - </b>' + records.get('Количество символов') + '\n'
                               + '<b>Ссылка на текст - </b>' + records.get('Ссылка на текст') + '\n',
                               parse_mode='html', reply_markup=markup)

    elif message.text == '↩ Назад ↩':
        await state.finish()
        await welcome(message)

    elif message.text == '🔄 Ввести заново 🔄':
        await Check.check.set()
        await message.answer('Введите все данные в формате\n'
                             'Текст:\n'
                             'Клиент:\n'
                             'СМИ:\n'
                             'Дата сдачи менеджеру (в формате 15.04.2022):\n'
                             'Райтер:\n'
                             'Менеджер:\n'
                             'Количество символов:\n'
                             'Ссылка на текст:\n')


@dp.callback_query_handler(lambda c: c.data)
async def answer(call: types.CallbackQuery):
    if call.data == 'ok':
        await bot.send_message(chat_id, text='<b>Проверено</b>' + '\n\n' + call.message.text + '\n\n' +
                                             'Комментарий: забирайте, все ок', parse_mode='html')
    elif call.data == 'good':
        await bot.send_message(chat_id, text='<b>Проверено</b>' + '\n\n' + call.message.text + '\n\n' +
                                             'Комментарий: норм, пара правок', parse_mode='html')
    elif call.data == 'bad':
        await bot.send_message(chat_id, text='<b>Проверено</b>' + '\n\n' + call.message.text + '\n\n' +
                                             'Комментарий: забирайте, правок много — правьте, лучше показать ещё раз',
                               parse_mode='html')
    elif call.data == 'awful':
        await bot.send_message(chat_id, text='<b>Проверено</b>' + '\n\n' + call.message.text + '\n\n' +
                                             'Комментарий: все плохо, приходите обсуждать', parse_mode='html')

    link = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton('Проверено', url='https://airtable.com/appwuAIlKJxXX7doG')

    link.add(item1)

    await bot.edit_message_reply_markup(-1001644325585, message_id=call.message.message_id, reply_markup=link)


@dp.message_handler(state=Find.find)
async def text(message: types.Message, state: FSMContext):
    global records1
    values = message.text.split('\n', 5)
    if len(values) != 6:
        await message.answer('Похоже вы ввели не все данные \nПопробуйте еще раз')
        await message.answer('<em><b>Пример ввода данных:</b></em>', parse_mode='html')
        await message.answer('Метавсленная\nСколково\nПопмех\nАлла\nЗавтра\nмногосторочный\n'
                             'комментарий\nили\nбриф')

    else:
        values.append(values[3] + ' / ' + values[1] + ' / ' + values[0])
        keys = ['Название материала', 'Клиент', 'СМИ', 'Менеджер', 'К какому сроку найти', 'Комментарий/бриф',
                'Саммари']
        records1 = dict(zip(keys, values))

        await message.answer(
            'Проверьте правильность ввода:\n'
            + '<b>Навзание материала - </b>' + values[0] + '\n'
            + '<b>Клиент - </b>' + values[1] + '\n'
            + '<b>СМИ - </b>' + values[2] + '\n'
            + '<b>Менеджер - </b>' + values[3] + '\n'
            + '<b>К какому сроку найти - </b>' + values[4] + '\n'
            + '<b>Комментарий/бриф - </b>' + values[5],
            parse_mode='html', reply_markup=check_menu)

        await FindVerify.find.set()


@dp.message_handler(state=FindVerify.find)
async def text(message: types.Message, state: FSMContext):
    if message.text == '✅ Все верно ✅':
        table = Table(api_key, 'appwuAIlKJxXX7doG', 'tblavyZtpfHcRropZ')
        table.create(records1)

        await message.answer('Данные отправлены в AirTable')
        await bot.send_message(-679434045, '<b>Название - </b>' + records1.get('Название материала') + '\n'
                               + '<b>Клиент - </b>' + records1.get('Клиент') + '\n'
                               + '<b>СМИ - </b>' + records1.get('СМИ') + '\n'
                               + '<b>Менеджер - </b>' + records1.get('Менеджер') + '\n'
                               + '<b>К какому сроку найти - </b>' + records1.get('К какому сроку найти') + '\n'
                               + '<b>Комментарий/бриф - </b>' + records1.get('Комментарий/бриф'),
                               parse_mode='html')

    elif message.text == '↩ Назад ↩':
        await state.finish()
        await welcome(message)

    elif message.text == '🔄 Ввести заново 🔄':
        await Find.find.set()
        await message.answer('Введите все данные в формате\n'
                             'Название материала:\n'
                             'Клиент:\n'
                             'СМИ:\n'
                             'Менеджер:\n'
                             'К какому сроку найти:\n'
                             'Комментарий/бриф(можно многострочный)')


if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
