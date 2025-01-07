import asyncio
import json
import math
import os
import re
from enum import Enum

import aiogram
import google.generativeai as genai
import requests
from aiogram import Bot, Dispatcher, types
from aiogram import F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from bs4 import BeautifulSoup

import funcs_for_resp
import generate

token = os.getenv('NEURO_TOKEN')
bot = Bot(token=token)
dp = Dispatcher()

creator = int(os.getenv('CREATOR'))  # TODO: in constant class
prompts_channel = int(os.getenv('PROMPTS_CHANNEL'))
log_chat = int(os.getenv('LOG_CHAT'))
support_chat = int(os.getenv('SUPPORT_CHAT'))


class MessageToAdmin(StatesGroup):
    text_message = State('text_message')


class Permissions(str, Enum):  # TODO: work
    CREATE_PROMPTS = 'create_prompts'
    BAN_USERS = 'ban_users'
    ADMIN_USERS = 'admin_users'
    VIEW_OTHER = 'view_other'
    # TODO: управление ботом


def find_draw_strings(text):
    draw_strings = re.findall(r'{{{(.*?)}}}', text, re.DOTALL)
    new_draw_strings = []
    for string in draw_strings:
        escaped_string = re.escape(string)
        text = re.sub(escaped_string, '', text, flags=re.DOTALL)
        text = re.sub(r'{{{', '', text, flags=re.DOTALL)
        text = re.sub(r'}}}', '', text, flags=re.DOTALL)
        string = re.sub(r'\n', '', string)
        string = re.sub(r'%', '', string)
        new_draw_strings.append(string)
    return new_draw_strings, text


def find_strings():  # TODO: handle other strings but a `find_draw_strings()`
    pass


def find_prompt(text):
    data = text.replace('/addprompt ', '')
    data = data.replace('/addprompt@neuro_gemini_bot ', '')
    data = data.split('|')
    command = data[0]
    name = data[1]
    description = data[2]
    prompt = "|".join(data[3:])
    return command, name, description, prompt


def is_banned(id):
    with open('bans.json') as f:
        bans = json.load(f)
    if str(id) in bans:
        return True


def replace_links(match):
    url = match.group(0)
    return get_article(url)


def get_article(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    main_content = soup.find('article', class_='tl_article_content')
    main_text = ''
    for element in main_content.find_all(['p']):
        main_text += element.get_text() + '\n'
    return main_text


def read_telegraph(text):
    pattern = r'(?:https:\/\/)?telegra\.ph\/[a-zA-Z0-9_-]+'
    return re.sub(pattern, replace_links, text)


def default_sets(id):  # TODO: work
    pass


def in_users(id):  # TODO: work
    pass


def sets_msg(id):
    with open('settings.json') as f:
        settings = json.load(f)
    reset = types.InlineKeyboardButton(text='Кнопки сброса диалога:', callback_data='reset')
    reset_on = types.InlineKeyboardButton(text='✅', callback_data='reset_on')
    reset_off = types.InlineKeyboardButton(text='❎', callback_data='reset_off')
    pictures_in_chat = types.InlineKeyboardButton(text='Генерация картинок в диалоге:',
                                                  callback_data='pictures_in_dialog')
    pictures_on = types.InlineKeyboardButton(text='✅', callback_data='pictures_on')
    pictures_off = types.InlineKeyboardButton(text='❎', callback_data='pictures_off')
    pictures_count = types.InlineKeyboardButton(text='Количество картинок в /sd:', callback_data='pictures_count')
    pictures_count_1 = types.InlineKeyboardButton(text='1️⃣', callback_data='pictures_count_1')
    pictures_count_2 = types.InlineKeyboardButton(text='2️⃣', callback_data='pictures_count_2')
    pictures_count_3 = types.InlineKeyboardButton(text='3️⃣', callback_data='pictures_count_3')
    pictures_count_4 = types.InlineKeyboardButton(text='4️⃣', callback_data='pictures_count_4')
    pictures_count_5 = types.InlineKeyboardButton(text='5️⃣', callback_data='pictures_count_5')
    imageai = types.InlineKeyboardButton(text='Нейросеть для генерации картинок в диалоге:', callback_data='imageai')
    imageai_sd = types.InlineKeyboardButton(text='SD', callback_data='imageai_sd')
    imageai_flux = types.InlineKeyboardButton(text='Flux', callback_data='imageai_flux')
    markup = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [reset],
            [reset_on, reset_off],
            [pictures_in_chat],
            [pictures_on, pictures_off],
            [pictures_count],
            [pictures_count_1, pictures_count_2, pictures_count_3, pictures_count_4, pictures_count_5],
            [imageai],
            [imageai_sd, imageai_flux]
        ]
    )
    if settings[str(id)]["reset"]:
        reset_status = "включено"
    else:
        reset_status = "выключено"
    if settings[str(id)]["pictures_in_dialog"]:
        pictures_status = "включено"
    else:
        pictures_status = "выключено"
    msg = (f'Настройки:\n\n'
           f'Кнопки сброса диалога: {reset_status}\n'
           f'Картинки в диалоге: {pictures_status}\n'
           f'Количество картинок: {settings[str(id)]["pictures_count"]}\n'
           f'Нейросеть для генерации картинок в диалоге: {settings[str(id)]["imageai"]}')
    return msg, markup


@dp.message(Command(commands=['start']))
async def start(message: Message):
    await bot.send_document(-1002318702468, open('prompts.json'))
    if is_banned(message.from_user.id):
        await message.reply('Вы забанены.')
    else:
        with open('users.json') as f:
            users = json.load(f)
        if str(message.from_user.id) not in users:
            users[str(message.from_user.id)] = message.from_user.first_name
        with open('users.json', 'w') as f:
            json.dump(users, f)
        with open('settings.json') as f:
            settings = json.load(f)
        if str(message.from_user.id) not in settings:
            settings[str(message.from_user.id)] = {'reset': True, 'pictures_in_dialog': True, 'pictures_count': 5,
                                                   'imageai': 'sd'}
        with open('settings.json', 'w') as f:
            json.dump(settings, f)
        await message.reply('Привет!\nПомощь - /help')


@dp.message(Command(commands=['online']))
async def online(message: Message):
    if is_banned(message.from_user.id):
        await message.reply('Вы забанены.')
    else:
        try:
            prompt = message.text.replace('/online ', '')
            prompt = prompt.replace('/online@neuro_gemini_bot ', '')
            response = generate.onlinegen(prompt)
            await message.reply(response)
        except Exception as e:
            await message.reply(f'Ошибка: {e}')


@dp.message(Command(commands=['sd']))
async def sd(message: Message):
    if is_banned(message.from_user.id):
        await message.reply('Вы забанены.')
    else:
        prompt = message.text.replace('/sd ', '')
        prompt = prompt.replace('/sd@neuro_gemini_bot ', '')
        wait_msg = await message.reply('Рисую...')
        try:
            with open('settings.json') as f:
                settings = json.load(f)
            photos = []
            for i in range(settings[str(message.from_user.id)]['pictures_count']):
                request = requests.post('https://api.r00t.us.kg/v1/image/sd', json={"prompt": prompt})
                photos.append(types.InputMediaPhoto(media=request.text))
            if len(photos) == 1:
                await message.reply_photo(photos[0].media)
            else:
                await message.reply_media_group(photos)
            await wait_msg.delete()
        except Exception as e:
            await message.reply(f'Ошибка при генерации изображения: {e}')
            await wait_msg.delete()


@dp.message(Command(commands=['flux']))
async def flux(message: Message):
    if is_banned(message.from_user.id):
        await message.reply('Вы забанены.')
    else:
        prompt = message.text.replace('/flux ', '')
        prompt = prompt.replace('/flux@neuro_gemini_bot ', '')
        wait_msg = await message.reply('Рисую...')
        try:
            with open('settings.json') as f:
                settings = json.load(f)
            photos = []
            for i in range(settings[str(message.from_user.id)]['pictures_count']):
                request = requests.post('https://api.r00t.us.kg/v1/image/flux', json={"prompt": prompt})
                photos.append(types.InputMediaPhoto(media=request.text))
            if len(photos) == 1:
                await message.reply_photo(photos[0].media)
            else:
                await message.reply_media_group(photos)
            await wait_msg.delete()
        except Exception as e:
            await message.reply(f'Ошибка при генерации изображения: {e}')
            await wait_msg.delete()


@dp.message(Command(commands=['help']))
async def help(message: Message):
    if is_banned(message.from_user.id):
        await message.reply('Вы забанены.')
    else:
        help_message = ('Команды:\n/start - начать\n/online - онлайн\n/sd <запрос> - cгенерировать картинку в SD\n'
                        '/prompts - список промптов\n/reset - очистить контекст\n/help - помощь\n/settings - настройки'
                        '\n/unicode - посмотреть символы unicode\n/send - отправить сообщение админу\n/stats - '
                        'статистика\n/profile - профиль')
        with open('admins.json') as f:
            admins = json.load(f)
        if str(message.from_user.id) in admins or message.from_user.id == creator:
            help_message += ('\n/addprompt <команда>|<название>|<описание>|<промпт> - добавить/изменить промпт\n'
                             '/delprompt <команда> - удалить промпт\n/getprompt <команда> - просмотреть промпт\n'
                             '/myprompts - просмотреть свои промпты\n/addadmin <команда> - добавить админа к промпту\n'
                             '/deladmin <команда> - удалить админа промпта')
        if message.from_user.id == creator:
            help_message += ('\n/admin - назначить админа\n/unadmin - снять админа\n/ban - забанить пользователя\n'
                             '/unban - разбанить пользователя\n/bans - список забаненых\n/admins - список админов\n'
                             '/yourprompts - просмотреть чьи-то промпты\n/restart - перезапуск бота\n/stop - остановка '
                             'бота\n/your_profile - просмотреть чей-то профиль')
        await message.reply(help_message)


@dp.message(Command(commands=['settings']))  # TODO: fix, check and work
async def settings(message: Message):
    if is_banned(message.from_user.id):
        await message.reply('Вы забанены.')
    else:
        msg = sets_msg(message.from_user.id)
        await message.reply(msg[0], reply_markup=msg[1])


@dp.message(Command(commands=['stats']))  # TODO: work
async def stats(message: Message):
    if is_banned(message.from_user.id):
        await message.reply('Вы забанены.')
    else:
        with open('prompts.json') as f:
            prompts = json.load(f)
        prompts_count = 0
        for _ in prompts:
            prompts_count += 1

        with open('bans.json') as f:
            bans = json.load(f)
        bans_count = 0
        for _ in bans:
            bans_count += 1

        with open('admins.json') as f:
            admins = json.load(f)
        admins_count = 0
        for _ in admins:
            admins_count += 1

        with open('users.json') as f:
            users = json.load(f)
        users_count = 0
        for _ in users:
            users_count += 1
        await message.reply(
            f'Статистика:\n\nПромпты: {prompts_count}\nБаны: {bans_count}\nАдмины: {admins_count}\nПользователи: {users_count}')


@dp.message(Command(commands=['profile']))  # TODO: work
async def profile(message: Message):
    if is_banned(message.from_user.id):
        await message.reply('Вы забанены.')
    else:
        with open('admins.json') as f:
            admins = json.load(f)
        if str(message.from_user.id) in admins:
            user_admin_status = 'да'
        else:
            user_admin_status = 'нет'
        await message.reply(f'{message.from_user.mention_html("Вы")} админ: {user_admin_status}',
                            parse_mode=ParseMode.HTML)


@dp.message(Command(commands=['your_profile']))  # TODO: work with `profile()`
async def your_profile(message: Message):
    if message.from_user.id == creator:
        with open('admins.json') as f:
            admins = json.load(f)
        if str(message.reply_to_message.from_user.id) in admins:
            user_admin_status = 'да'
        else:
            user_admin_status = 'нет'
        await message.reply(f'{message.reply_to_message.from_user.mention_html()} админ: {user_admin_status}',
                            parse_mode=ParseMode.HTML)


@dp.message(Command(commands=['reset']))  # TODO: work with `name` of prompt
async def reset(message: Message):
    if is_banned(message.from_user.id):
        await message.reply('Вы забанены.')
    else:
        with open('contexts.json') as f:
            contexts = json.load(f)
        for context in contexts:
            if context.startswith(str(message.from_user.id)):
                del contexts[context]
        with open('contexts.json', 'w') as f:
            json.dump(contexts, f, ensure_ascii=False, indent=4)
        await message.reply('Весь контекст удалён')


@dp.message(Command(commands=['unicode']))
async def unicode(message: Message):
    if is_banned(message.from_user.id):
        await message.reply('Вы забанены.')
    else:
        await message.reply('Эта функция предоставляет символы Unicode (их могут использовать админы для создания ASCII'
                            '-картинок или кастомизированных меню в своих промптах), отобранные из '
                            'https://unicode-table.com/ru/ и приложения "Таблица символов" (ОС Windows) создетелем бота'
                            ', а также предложенные пользователями по команде /send:\n'
                            '֎ ֍ \n█ ▓ ▒ ░ ▄ ▀ ▌ ▐ \n■ □ ▬ ▲ ► ▼ ◄ \n◊ ○ ◌ ● ◘ ◙ ◦ ☻ \n☼ ♀ ♂ ♪ ♫ ♯ \n'
                            '┌─┬┐  ╒═╤╕\n│ ││  │ ││\n├─┼┤  ╞═╪╡\n└─┴┘  ╘═╧╛\n╓─╥╖  ╔═╦╗\n║ ║║  ║ ║║\n╟─╫╢  ╠═╬╣\n'
                            '╙─╨╜  ╚═╩╝\nΩ ₪ ← ↑ → ↓ ∆ ∏ ∑ \n√ ∞ ∟ ∩ ≈ ≠ ≡ ≤ ≥ ⌂ ⌐ \n➀➁➂➃➄➅➆➇➈➉\n⓿❶❷❸❹❺❻❼❽❾❿\n'
                            '➊➋➌➍➎➏➐➑➒➓\n⓫⓬⓭⓮⓯⓰⓱⓲⓳⓴\n⓵⓶⓷⓸⓹⓺⓻⓼⓽⓾\n⑴⑵⑶⑷⑸⑹⑺⑻⑼⑽\n⑾⑿⒀⒁⒂⒃⒄⒅⒆⒇\n'
                            '⒈⒉⒊⒋⒌⒍⒎⒏⒐⒑\n⒒⒓⒔⒕⒖⒗⒘⒙⒚⒛\n①②③④⑤⑥⑦⑧⑨⑩\n⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳\n♳♴♵♶♷♸♹♺\n♼♽✓\n♩♪♫♬\n'
                            '▁▂▃▄▅▆▇█ \n▊\n▋\n▌\n▍\n▎\n▏\n\n▔\n')


@dp.message(Command(commands=['addkey']))
async def addkey(message: Message):
    with open('keys.json') as f:
        keys = json.load(f)
    data = message.text.replace('/addkey ', '')
    data = data.replace('/addkey@neuro_gemini_bot ', '')
    try:
        genai.configure(api_key=data)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        chat = model.start_chat(history=[])
        chat.send_message('hi')
        keys.append(data)
        with open('keys.json', 'w') as f:
            json.dump(keys, f, ensure_ascii=False, indent=4)
        await message.reply('Ключ добавлен.')
    except Exception as e:
        await message.reply(f'Ключ неактивен. Попробуйте снова чуть позже. \nОшибка: {e}')


@dp.message(Command(commands=['test']))
async def test(message: Message):
    if is_banned(message.from_user.id):
        await message.reply('Вы забанены.')
        return
    with open('keys.json') as f:
        keys = json.load(f)
    for key in keys:
        genai.configure(api_key=key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            }
        ]
        response = model.generate_content('Привет!', safety_settings=safety_settings)
        await message.reply(response.text)
        break


@dp.message(Command(commands=['support']))
async def send(message: Message, state: FSMContext):
    if is_banned(message.from_user.id):
        await message.reply('Вы забанены.')
    else:
        await state.set_state(MessageToAdmin.text_message)
        await message.reply('Связь с админом.\nНапишите сообщение, для отмены напишите: "отмена":')


@dp.message(MessageToAdmin.text_message)
async def message_to_admin(message: Message, state: FSMContext):
    if is_banned(message.from_user.id):
        await message.reply('Вы забанены.')
    else:
        await state.update_data(text_message=message.text)
        if message.text.lower() == 'отмена':
            await state.clear()
            await message.reply('Отмена.')
        else:
            await state.clear()
            await message.reply('Сообщение отправлено.\nОбсуждение бота в группе @neuro_opensource')
            await bot.send_message(support_chat,
                                   f'Сообщение от пользователя @{message.from_user.username}, {message.from_user.id}, {message.from_user.mention_html()}:',
                                   parse_mode=ParseMode.HTML)
            await message.forward(support_chat)


@dp.message(Command(commands=['addprompt']))
async def addprompt(message: Message):
    with open('admins.json') as f:
        admins = json.load(f)
    if str(message.from_user.id) in admins or message.from_user.id == creator:
        data = find_prompt(message.text)
        with open('prompts.json') as f:
            prompts = json.load(f)
        if data[0] in prompts:
            prompt_in_db = True
            if prompts[data[0]][
                'creator'] == message.from_user.id or message.from_user.id == creator or message.from_user.id in \
                    prompts[data[0]]['admins']:
                user_prompt_admin = True
            else:
                user_prompt_admin = False
        else:
            prompt_in_db = False
            user_prompt_admin = False
        if prompt_in_db and user_prompt_admin:
            creator_of_prompt = prompts[data[0]]['creator']
            admins_of_prompt = prompts[data[0]]['admins']
            prompts[data[0]] = {
                'name': data[1],
                'description': data[2],
                'prompt': data[3],
                'creator': creator_of_prompt,
                'admins': admins_of_prompt
            }
            with open('prompts.json', 'w') as f:
                json.dump(prompts, f, ensure_ascii=False, indent=4)
            await message.reply(f'Промпт /{data[0]} изменён')
            await bot.send_message(prompts_channel, f'/addprompt {data[0]}|{data[1]}|{data[2]}|{data[3]}\n\n'
                                                    f'Создатель: {admins[str(creator_of_prompt)]} (`{creator_of_prompt}`)\n'
                                                    f'Админы: {admins_of_prompt}', parse_mode=ParseMode.MARKDOWN)
        elif not prompt_in_db:
            prompts[data[0]] = {
                'name': data[1],
                'description': data[2],
                'prompt': data[3],
                'creator': message.from_user.id,
                'admins': []
            }
            with open('prompts.json', 'w') as f:
                json.dump(prompts, f, ensure_ascii=False, indent=4)
            await message.reply(f'Промпт /{data[0]} добавлен')
            await bot.send_message(prompts_channel, f'/addprompt {data[0]}|{data[1]}|{data[2]}|{data[3]}\n\n'
                                                    f'Создатель: {admins[str(message.from_user.id)]} (`{message.from_user.id}`)\n'
                                                    'Админы: []', parse_mode=ParseMode.MARKDOWN)
        else:
            await message.reply('Это не твой промпт')
    else:
        data = find_prompt(message.text)
        with open('prompts.json') as f:
            prompts = json.load(f)
        if prompts[data[0]]['creator'] == message.from_user.id:
            admins_of_prompt = prompts[data[0]]['admins']
            prompts[data[0]] = {
                'name': data[1],
                'description': data[2],
                'prompt': data[3],
                'creator': message.from_user.id,
                'admins': admins_of_prompt
            }
            with open('prompts.json', 'w') as f:
                json.dump(prompts, f, ensure_ascii=False, indent=4)
            await message.reply(f'Промпт /{data[0]} изменён')
            await bot.send_message(prompts_channel, f'/addprompt {data[0]}|{data[1]}|{data[2]}|{data[3]}\n\n'
                                                    f'Создатель: {admins[str(message.from_user.id)]} (`{message.from_user.id}`)\n'
                                                    f'Админы: {str(admins_of_prompt)}', parse_mode=ParseMode.MARKDOWN)
        else:
            await message.reply('Куда полез? Тебе сюда нельзя')


@dp.message(Command(commands=['delprompt']))
async def delprompt(message: Message):
    prompt = message.text.replace('/delprompt ', '')
    prompt = prompt.replace('/delprompt@neuro_gemini_bot ', '')
    with open('prompts.json') as f:
        prompts = json.load(f)
    try:
        prompt_creator = prompts[prompt]['creator']
    except KeyError:
        await message.reply('Такого промпта нет')
        return
    if prompt_creator == message.from_user.id or message.from_user.id == creator:
        btn1 = types.InlineKeyboardButton(text='Нет', callback_data=f'false_delprompt_{message.from_user.id}')
        btn2 = types.InlineKeyboardButton(text='Да', callback_data=f'true__delprompt__{prompt}__{message.from_user.id}')
        markup = types.InlineKeyboardMarkup(inline_keyboard=[[btn1, btn2]])
        await message.reply(f'Ты уверен?', reply_markup=markup)
    else:
        await message.reply('Куда полез? Тебе сюда нельзя')


@dp.message(Command(commands=['getprompt']))
async def getprompt(message: Message):
    key = message.text.replace('/getprompt ', '')
    key = key.replace('/getprompt@neuro_gemini_bot ', '')
    with open('prompts.json') as f:
        prompts = json.load(f)
    try:
        prompt_creator = prompts[key]['creator']
        prompt_admins = prompts[key]['admins']
    except KeyError:
        await message.reply('Такого промпта нет')
        return
    if prompt_creator == message.from_user.id or message.from_user.id == creator or message.from_user.id in prompt_admins:
        with open('admins.json') as f:
            admins = json.load(f)
        command = key
        name = prompts[key]['name']
        description = prompts[key]['description']
        prompt = prompts[key]['prompt']
        creator_of_prompt = prompts[key]['creator']
        admins_of_prompt = prompts[key]['admins']
        btn1 = types.InlineKeyboardButton(text='❌ Скрыть', callback_data=f'del_{message.from_user.id}')
        markup = types.InlineKeyboardMarkup(inline_keyboard=[[btn1]])
        await message.reply(f'/addprompt {command}|{name}|{description}|{prompt}\n\n'
                            f'Создатель: {admins[str(creator_of_prompt)]} (`{creator_of_prompt}`)'
                            f'Админы: {str(admins_of_prompt)}', reply_markup=markup, parse_mode=ParseMode.MARKDOWN)
    else:
        await message.reply('Куда полез? Тебе сюда нельзя')


@dp.message(Command(commands=['gdelprompt']))
async def gdelprompt(message: Message):
    prompt_command = message.text.replace('/gdelprompt ', '')
    prompt_command = prompt_command.replace('/gdelprompt@neuro_gemini_bot ', '')
    with open('prompts.json') as f:
        prompts = json.load(f)
    try:
        prompt_creator = prompts[prompt_command]['creator']
    except KeyError:
        await message.reply('Такого промпта нет')
        return
    if prompt_creator == message.from_user.id or message.from_user.id == creator:
        with open('admins.json') as f:
            admins = json.load(f)
        command = prompt_command
        name = prompts[prompt_command]['name']
        description = prompts[prompt_command]['description']
        prompt = prompts[prompt_command]['prompt']
        creator_of_prompt = prompts[prompt_command]['creator']
        admins_of_prompt = prompts[prompt_command]['admins']
        await message.reply(f'/addprompt {command}|{name}|{description}|{prompt}\n\n'
                            f'Создатель: {admins[str(creator_of_prompt)]} (`{creator_of_prompt}`)'
                            f'Админы: {str(admins_of_prompt)}', parse_mode=ParseMode.MARKDOWN)
        btn1 = types.InlineKeyboardButton(text='Нет', callback_data=f'false_delprompt_{message.from_user.id}')
        btn2 = types.InlineKeyboardButton(text='Да',
                                          callback_data=f'true__delprompt__{prompt_command}__{message.from_user.id}')
        markup = types.InlineKeyboardMarkup(inline_keyboard=[[btn1, btn2]])
        await message.reply(f'Ты уверен?', reply_markup=markup)
    else:
        await message.reply('Куда полез? Тебе сюда нельзя')


@dp.message(Command(commands=['addadmin']))  # TODO: check
async def addadmin(message: Message):
    data = message.text.replace('/addadmin ', '')
    data = data.replace('/addadmin@neuro_gemini_bot ', '')
    with open('prompts.json') as f:
        prompts = json.load(f)
    with open('admins.json') as f:
        admins = json.load(f)
    if str(message.reply_to_message.from_user.id) in admins:
        prompts[data]['admins'].append(message.reply_to_message.from_user.id)
    else:
        await message.reply('Ты не админ')
        return
    with open('prompts.json', 'w') as f:
        json.dump(prompts, f)
    await message.reply(f'Админ к /{data} добавлен')


@dp.message(Command(commands=['deladmin']))  # TODO: check
async def deladmin(message: Message):
    data = message.text.replace('/deladmin ', '')
    data = data.replace('/deladmin@neuro_gemini_bot ', '')
    with open('prompts.json') as f:
        prompts = json.load(f)
    prompts[data]['admins'].remove(message.reply_to_message.from_user.id)
    with open('prompts.json', 'w') as f:
        json.dump(prompts, f)
    await message.reply(f'Админ к /{data} удалён')


@dp.message(Command(commands=['myprompts']))
async def myprompts(message: Message):
    with open('prompts.json') as f:
        prompts = json.load(f)
    message_prompts = ''
    for prompt in prompts:
        if prompts[prompt]['creator'] == message.from_user.id:
            message_prompts += '/' + prompt + '\n'
    try:
        await message.reply(message_prompts)
    except aiogram.exceptions.TelegramBadRequest:
        await message.reply('У вас нет ни одного созданного промпта')


@dp.message(Command(commands=['yourprompts']))
async def yourprompts(message: Message):
    if message.from_user.id == creator:
        with open('prompts.json') as f:
            prompts = json.load(f)
        message_prompts = ''
        for prompt in prompts:
            if prompts[prompt]['creator'] == message.reply_to_message.from_user.id:
                message_prompts += '/' + prompt + '\n'
        try:
            await message.reply(message_prompts)
        except aiogram.exceptions.TelegramBadRequest:
            await message.reply(f'У {message.reply_to_message.from_user.first_name} нет ни одного созданного промпта')


@dp.message(Command(commands=['prompts']))  # TODO: check
async def prompts(message: Message):
    if is_banned(message.from_user.id):
        await message.reply('Вы забанены.')
    else:
        with open('prompts.json') as f:
            prompts = json.load(f)
        list_prompts = []
        for prompt in prompts:
            message_prompt = '/' + prompt + ' "' + prompts[prompt]['name'] + '" ' + prompts[prompt][
                'description'] + '\n'
            list_prompts.append(message_prompt)
        btn1 = types.InlineKeyboardButton(text='❌ Скрыть', callback_data='del')
        markup = types.InlineKeyboardMarkup(inline_keyboard=[[btn1]])
        i = len(list_prompts)
        y = [0, 10]
        while True:
            message_prompts = ''
            for msg in list_prompts[y[0]:y[1]]:
                message_prompts += msg
            await message.reply(message_prompts, reply_markup=markup)
            if y[1] >= i:
                break
            y[0] += 10
            y[1] += 10


@dp.message(Command(commands=['ban']))
async def ban(message: Message):
    if message.from_user.id == creator:
        with open('bans.json') as f:
            bans = json.load(f)
        if message.reply_to_message.from_user.id not in bans:
            bans[str(message.reply_to_message.from_user.id)] = message.reply_to_message.from_user.first_name
        with open('bans.json', 'w') as f:
            json.dump(bans, f)
        await message.reply(f'{message.reply_to_message.from_user.first_name} забанен')
    else:
        await message.reply('Вы не админ')


@dp.message(Command(commands=['unban']))
async def unban(message: Message):
    if message.from_user.id == creator:
        with open('bans.json') as f:
            bans = json.load(f)
        del bans[str(message.reply_to_message.from_user.id)]
        with open('bans.json', 'w') as f:
            json.dump(bans, f)
        await message.reply(f'{message.reply_to_message.from_user.first_name} разбанен')
    else:
        await message.reply('Вы не админ')


@dp.message(Command(commands=['admin']))
async def admin(message: Message):
    if message.from_user.id == creator:
        with open('admins.json') as f:
            admins = json.load(f)
        if message.reply_to_message.from_user.id not in admins:
            admins[str(message.reply_to_message.from_user.id)] = message.reply_to_message.from_user.first_name
        with open('admins.json', 'w') as f:
            json.dump(admins, f)
        await message.reply(f'{message.reply_to_message.from_user.first_name} теперь админ')
    else:
        await message.reply('Вы не админ')


@dp.message(Command(commands=['unadmin']))
async def unadmin(message: Message):
    if message.from_user.id == creator:
        with open('admins.json') as f:
            admins = json.load(f)
        del admins[str(message.reply_to_message.from_user.id)]
        with open('admins.json', 'w') as f:
            json.dump(admins, f)
        await message.reply(f'{message.reply_to_message.from_user.first_name} больше не админ')
    else:
        await message.reply('Вы не админ')


@dp.message(Command(commands=['admins']))
async def admins(message: Message):
    if message.from_user.id == creator:
        with open('admins.json') as f:
            admins = json.load(f)
        admins_message = 'Админы:\n'
        for admin in admins:
            admins_message += f'{admins[admin]} (`{admin}`)\n'
        btn1 = types.InlineKeyboardButton(text='❌ Скрыть', callback_data=f'del_{message.from_user.id}')
        markup = types.InlineKeyboardMarkup(inline_keyboard=[[btn1]])
        if admins_message == 'Админы:\n':
            await message.reply('Админов нет')
            return
        await message.reply(admins_message, reply_markup=markup, parse_mode=ParseMode.MARKDOWN)
    else:
        await message.reply('Вы не админ')


@dp.message(Command(commands=['bans']))
async def bans(message: Message):
    if message.from_user.id == creator:
        with open('bans.json') as f:
            bans = json.load(f)
        bans_message = 'Забаненные пользователи:\n'
        for ban in bans:
            bans_message += f'{bans[ban]} (`{ban}`)\n'
        btn1 = types.InlineKeyboardButton(text='❌ Скрыть', callback_data=f'del_{message.from_user.id}')
        markup = types.InlineKeyboardMarkup(inline_keyboard=[[btn1]])
        if bans_message == 'Забаненные пользователи:\n':
            await message.reply('Забаненных пользователей нет')
            return
        await message.reply(bans_message, reply_markup=markup, parse_mode=ParseMode.MARKDOWN)
    else:
        await message.reply('Вы не админ')


@dp.message(Command(commands=['stop']))
async def stop(message: Message):
    if message.from_user.id == creator:
        await message.reply('Бот остановлен')
        await dp.stop_polling()


@dp.message(Command(commands=['restart']))
async def restart(message: Message):
    if message.from_user.id == creator:
        await message.reply('Временно недоступно.')


@dp.message(F.text.startswith('/'))  # TODO: in func
async def command_response(message: Message):
    if is_banned(message.from_user.id):
        await message.reply('Вы забанены.')
    elif message.text[0] == '/':
        with open('prompts.json') as f:
            prompts = json.load(f)
        command = message.text.split()[0].replace('/', '')
        command = command.split()[0].replace('@neuro_gemini_bot', '')
        prompt = message.text.replace(message.text.split()[0], '')
        prompt = prompt.replace('@neuro_gemini_bot ', '')
        prompt = read_telegraph(prompt)
        if prompt == '':
            prompt = ' '

        with open('contexts.json') as f:
            contexts = json.load(f)
        try:
            system_prompt = read_telegraph(prompts[command]['prompt'])
        except KeyError:
            return
        with open('keys.json') as f:
            keys = json.load(f)
        wait_msg = await message.reply('Думаю...')
        if f'{message.from_user.id}-{command}' not in contexts:
            contexts[f'{message.from_user.id}-{command}'] = []
        context = contexts[f'{message.from_user.id}-{command}']
        try:
            for key in keys:
                try:
                    genai.configure(api_key=key)
                    model = genai.GenerativeModel('gemini-2.0-flash-exp',
                                                  system_instruction=system_prompt,
                                                  tools=[funcs_for_resp, math])
                    chat = model.start_chat(history=context)
                    request = chat.send_message(prompt, safety_settings=0)
                    break
                except Exception as e:
                    e = e
            else:
                try:
                    await message.reply(f'Ошибка при генерации: {e}\n Вы можете сообщить о ней по команде /send')
                    await wait_msg.delete()
                    return
                except UnboundLocalError:
                    await message.reply('Кончились ключи. Можете добавить по команде /addkey')
                    await wait_msg.delete()
                    return
            response = find_draw_strings(request.text)
            btn1 = types.InlineKeyboardButton(text='Сбросить весь диалог', callback_data='delall_context')
            btn2 = types.InlineKeyboardButton(text='Сбросить диалог', callback_data=f'delcontext__{command}')
            with open('settings.json') as f:
                settings = json.load(f)
            if settings[str(message.from_user.id)]['reset']:
                markup = types.InlineKeyboardMarkup(inline_keyboard=[[btn1, btn2]])
            else:
                markup = types.InlineKeyboardMarkup(inline_keyboard=[])
            i = len(response[1])
            x = [0, 4096]
            ids1 = []
            while True:
                msg = await message.reply(response[1][x[0]:x[1]], reply_markup=markup)
                ids1.append(msg.message_id)
                if x[1] >= i:
                    break
                x[0] += 4096
                x[1] += 4096
            await wait_msg.delete()
        except Exception as e:
            await message.reply(f'Ошибка при отправке: {e}\nВы можете сообщить о ней по команде /send')
            await wait_msg.delete()
            return
        context.append({'role': 'user', 'parts': prompt})
        context.append({'role': 'model', 'parts': response[1]})
        with open('prompts_message_ids.json') as f:
            ids = json.load(f)
        if f'{command}' not in ids:
            ids[f'{command}'] = []
        for id in ids1:
            ids[f'{command}'].append(id)
        contexts[f'{str(message.from_user.id)}-{command}'] = context
        with open('prompts_message_ids.json', 'w') as f:
            json.dump(ids, f, indent=4)
        with open('contexts.json', 'w') as f:
            json.dump(contexts, f, ensure_ascii=False, indent=4)
        with open('settings.json') as f:
            settings = json.load(f)
        photos = []
        if settings[str(message.from_user.id)]['pictures_in_dialog']:
            for prompt in response[0]:
                request = requests.post(
                    f'https://https://api.r00t.us.kg/v1/image/{settings[str(message.from_user.id)]["imageai"]}',
                    json={"prompt": prompt})
                photos.append(types.InputMediaPhoto(media=request.text, caption=prompt))
            if len(photos) == 1:
                await message.reply_photo(photos[0].media)
            else:
                await message.reply_media_group(photos)
        await wait_msg.delete()


@dp.message(F.reply_to_message.from_user.id == 7487465375)  # TODO: in func
async def reply_response(message: Message):
    if is_banned(message.from_user.id):
        await message.reply('Вы забанены.')
    else:
        with open('prompts_message_ids.json') as f:
            ids = json.load(f)
        for prompt_ids in ids:
            if message.reply_to_message.message_id in ids[prompt_ids]:
                command = prompt_ids
                break
        else:
            return
        with open('prompts.json') as f:
            prompts = json.load(f)
        prompt = message.text
        prompt = read_telegraph(prompt)

        with open('contexts.json') as f:
            contexts = json.load(f)
        if f'{message.from_user.id}-{command}' not in contexts:
            contexts[f'{message.from_user.id}-{command}'] = []
        context = contexts[f'{message.from_user.id}-{command}']
        system_prompt = read_telegraph(prompts[command]['prompt'])
        with open('keys.json') as f:
            keys = json.load(f)
        wait_msg = await message.reply('Думаю...')
        try:
            for key in keys:
                try:
                    genai.configure(api_key=key)
                    model = genai.GenerativeModel('gemini-2.0-flash-exp',
                                                  system_instruction=system_prompt,
                                                  tools=[funcs_for_resp, math])
                    chat = model.start_chat(history=context)
                    request = chat.send_message(prompt, safety_settings=0)
                    break
                except Exception as e:
                    pass
            else:
                try:
                    await message.reply(f'Ошибка при генерации: {e}\n Вы можете сообщить о ней по команде /send')
                    await wait_msg.delete()
                    return
                except UnboundLocalError:
                    await message.reply('Кончились ключи. Можете добавить по команде /addkey')
                    await wait_msg.delete()
                    return
            response = find_draw_strings(request.text)
            with open('settings.json') as f:
                settings = json.load(f)
            btn1 = types.InlineKeyboardButton(text='Сбросить весь диалог', callback_data='delall_context')
            btn2 = types.InlineKeyboardButton(text='Сбросить диалог', callback_data=f'delcontext__{command}')
            if settings[str(message.from_user.id)]['reset']:
                markup = types.InlineKeyboardMarkup(inline_keyboard=[[btn1, btn2]])
            else:
                markup = types.InlineKeyboardMarkup(inline_keyboard=[])
            i = len(response[1])
            x = [0, 4096]
            ids1 = []
            while True:
                msg = await message.reply(response[1][x[0]:x[1]], reply_markup=markup)
                ids1.append(msg.message_id)
                if x[1] >= i:
                    break
                x[0] += 4096
                x[1] += 4096
            await wait_msg.delete()
        except Exception as e:
            await message.reply(f'Ошибка при отправке: {e}\nВы можете сообщить о ней по команде /send')
            await wait_msg.delete()
            return
        context.append({'role': 'user', 'parts': prompt})
        context.append({'role': 'model', 'parts': response[1]})
        for id in ids1:
            ids[f'{command}'].append(id)
        contexts[f'{str(message.from_user.id)}-{command}'] = context
        with open('prompts_message_ids.json', 'w') as f:
            json.dump(ids, f, indent=4)
        with open('contexts.json', 'w') as f:
            json.dump(contexts, f, ensure_ascii=False, indent=4)
        with open('settings.json') as f:
            settings = json.load(f)
        photos = []
        if settings[str(message.from_user.id)]['pictures_in_dialog']:
            for prompt in response[0]:
                request = requests.post(
                    f'https://https://api.r00t.us.kg/v1/image/{settings[str(message.from_user.id)]["imageai"]}',
                    json={"prompt": prompt})
                photos.append(types.InputMediaPhoto(media=request.text, caption=prompt))
            if len(photos) == 1:
                await message.reply_photo(photos[0].media)
            else:
                await message.reply_media_group(photos)
        await wait_msg.delete()


@dp.callback_query()
async def callback(call: CallbackQuery):
    if call.data == 'delall_context':
        btn1 = types.InlineKeyboardButton(text='Нет', callback_data=f'false_delall_context_{call.from_user.id}')
        btn2 = types.InlineKeyboardButton(text='Да', callback_data=f'true_delall_context_{call.from_user.id}')
        markup = types.InlineKeyboardMarkup(inline_keyboard=[[btn1, btn2]])
        await call.message.reply(f'{call.from_user.mention_html()}, ты уверен, что хочешь сбросить весь контекст?',
                                 parse_mode=ParseMode.HTML, reply_markup=markup)
        await call.answer()

    elif call.data.startswith('true_delall_context'):
        data = call.data.split('_')
        if str(call.from_user.id) == data[3]:
            with open('contexts.json') as f:
                contexts = json.load(f)
            for context in contexts:
                if context.startswith(str(call.from_user.id)):
                    del contexts[context]
            with open('contexts.json', 'w') as f:
                json.dump(contexts, f, ensure_ascii=False, indent=4)
            await call.message.delete()
            await call.answer('Весь контекст удалён', show_alert=True)
        else:
            await call.answer('Отставить! Это не твоя кнопка!')

    elif call.data.startswith('false_delall_context'):
        data = call.data.split('_')
        if str(call.from_user.id) == data[3]:
            await call.message.delete()
            await call.answer('Хорошо, я не буду удалять весь контекст.')
        else:
            await call.answer('Отставить! Это не твоя кнопка!')

    elif call.data.startswith('delcontext__'):
        data = call.data.split('__')
        btn1 = types.InlineKeyboardButton(text='Нет', callback_data=f'false_delcontext_{call.from_user.id}')
        btn2 = types.InlineKeyboardButton(text='Да', callback_data=f'true__delcontext__{data[1]}__{call.from_user.id}')
        markup = types.InlineKeyboardMarkup(inline_keyboard=[[btn1, btn2]])
        await call.message.reply(f'{call.from_user.mention_html()}, ты уверен, что хочешь сбросить контекст?',
                                 parse_mode=ParseMode.HTML, reply_markup=markup)
        await call.answer()

    elif call.data.startswith('true__delcontext__'):
        data = call.data.split('__')
        if str(call.from_user.id) == data[3]:
            key = f'{data[2]}_{data[3]}'
            with open('contexts.json') as f:
                contexts = json.load(f)
            contexts.pop(key, 'Не найдено')
            with open('contexts.json', 'w') as f:
                json.dump(contexts, f, ensure_ascii=False, indent=4)
            await call.message.delete()
            await call.answer('Контекст удалён', show_alert=True)
        else:
            await call.answer('Отставить! Это не твоя кнопка!')

    elif call.data.startswith('false_delcontext'):
        data = call.data.split('_')
        if str(call.from_user.id) == data[2]:
            await call.message.delete()
            await call.answer('Хорошо, я не буду удалять контекст.')
        else:
            await call.answer('Отставить! Это не твоя кнопка!')

    elif call.data.startswith('true__delprompt__'):
        data = call.data.split('__')
        with open('admins.json') as f:
            admins = json.load(f)
        if str(call.from_user.id) == data[3]:
            key = f'{data[2]}'
            with open('prompts.json') as f:
                prompts = json.load(f)
            prompt = prompts[key]
            del prompts[key]
            with open('prompts.json', 'w') as f:
                json.dump(prompts, f, ensure_ascii=False, indent=4)
            await call.message.edit_text(f'Промпт /{key} удалён')
            await bot.send_message(prompts_channel,
                                   f'/addprompt {key}|{prompt["name"]}|{prompt["description"]}|{prompt["prompt"]}\n\n'
                                   f'Создатель: {admins[str(prompt["creator"])]} (`{prompt["creator"]}`)\n'
                                   f'Админы: {prompt["admins"]}', parse_mode=ParseMode.MARKDOWN)
        else:
            await call.answer('Отставить! Это не твоя кнопка!')

    elif call.data.startswith('false_delprompt'):
        data = call.data.split('_')
        if str(call.from_user.id) == data[2]:
            await call.message.delete()
            await call.answer('Хорошо, я не буду удалять промпт.')
        else:
            await call.answer('Отставить! Это не твоя кнопка!')

    elif call.data == 'del':
        await call.message.delete()

    elif call.data.startswith('del_'):
        data = call.data.split('_')
        if str(call.from_user.id) == data[1]:
            await call.message.delete()
        else:
            await call.answer('Отставить! Это не твоя кнопка!')

    elif call.data == 'reset':
        await call.answer('Кнопки сброса диалога')

    elif call.data == 'reset_on':
        with open('settings.json') as f:
            settings = json.load(f)
        settings[str(call.from_user.id)]['reset'] = True
        with open('settings.json', 'w') as f:
            json.dump(settings, f)
        await call.answer('Кнопки сброса диалога включены', show_alert=True)
        msg = sets_msg(call.from_user.id)
        await call.message.edit_text(msg[0], reply_markup=msg[1])

    elif call.data == 'reset_off':
        with open('settings.json') as f:
            settings = json.load(f)
        settings[str(call.from_user.id)]['reset'] = False
        with open('settings.json', 'w') as f:
            json.dump(settings, f)
        await call.answer('Кнопки сброса диалога выключены', show_alert=True)
        msg = sets_msg(call.from_user.id)
        await call.message.edit_text(msg[0], reply_markup=msg[1])

    elif call.data == 'pictures_in_chat':
        await call.answer('Генерация картинок в диалоге')

    elif call.data.startswith('pictures_in_chat_'):
        data = call.data.split('_')
        with open('settings.json') as f:
            settings = json.load(f)
        if data[1] == 'on':
            settings[str(call.from_user.id)]['pictures_in_chat'] = True
            await call.answer(f'Картинки в диалоге включены', show_alert=True)
        elif data[1] == 'off':
            settings[str(call.from_user.id)]['pictures_in_chat'] = False
            await call.answer(f'Картинки в диалоге отключены', show_alert=True)
        with open('settings.json', 'w') as f:
            json.dump(settings, f)
        msg = sets_msg(call.from_user.id)
        await call.message.edit_text(msg[0], reply_markup=msg[1])

    elif call.data == 'pictures_count':
        await call.answer('Количество генерируемых картинок')

    elif call.data.startswith('pictures_count_'):
        data = call.data.split('_')
        with open('settings.json') as f:
            settings = json.load(f)
        settings[str(call.from_user.id)]['pictures_count'] = int(data[1])
        with open('settings.json', 'w') as f:
            json.dump(settings, f)
        await call.answer(f'Количество генерируемых картинок изменено на {data[1]}', show_alert=True)
        msg = sets_msg(call.from_user.id)
        await call.message.edit_text(msg[0], reply_markup=msg[1])

    elif call.data == 'imageai':
        await call.answer('Нейросеть для генерации картинок в диалоге')

    elif call.data.startswith('imageai_'):
        data = call.data.split('_')
        with open('settings.json') as f:
            settings = json.load(f)
        settings[str(call.from_user.id)]['imageai'] = data[1]
        msg = sets_msg(call.from_user.id)
        await call.message.edit_text(msg[0], reply_markup=msg[1])


if __name__ == '__main__':
    asyncio.run(dp.start_polling(bot))
