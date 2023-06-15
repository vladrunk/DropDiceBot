from telebot.async_telebot import AsyncTeleBot
from telebot.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
)
from loguru import logger as log
import asyncio
from nanoid import generate
from string import digits, ascii_lowercase
from cfg.config import (
    BOT_TOKEN, CALLBACK_CHOOSE_BET, CALLBACK_SEND_DICE, CALLBACK_MAKE_BET, DEBUG,
)
from helpers.typehints import Session, Bet
from workers.db import DataBase


def chat_info(m: Message) -> str:
    return f'[chat={m.chat.id}][user={m.from_user.id}]'


log.chat_info = chat_info
log.add(
    './log/info_{time:YYYY-MM-DD}.log',
    backtrace=True,
    diagnose=True,
    enqueue=True,
    level='INFO',
    encoding='UTF-8',
    rotation='500 MB',
    compression='zip',
    retention='10 days'
)
log.add(
    './log/debug_{time:YYYY-MM-DD}.log',
    backtrace=True,
    diagnose=True,
    enqueue=True,
    level='DEBUG',
    encoding='UTF-8',
    rotation='500 MB',
    compression='zip',
    retention='10 days'
)
bot = AsyncTeleBot(token=BOT_TOKEN)
db = DataBase(log=log)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
# Regular services defs
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
async def update_listener(messages):
    for message in messages:
        log.debug(message)


def markup_make_session(owner: str, owner_id: int):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(text='Сделать ставку', callback_data=CALLBACK_CHOOSE_BET),
        InlineKeyboardButton(text=f'Кинуть кубить может {owner}',
                             callback_data=f'{CALLBACK_SEND_DICE}#{owner_id}'),
        row_width=1,
    )
    return markup


def markup_choose_bet(user: int):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(text='1', callback_data=f'{CALLBACK_MAKE_BET}{user}#1'),
        InlineKeyboardButton(text='2', callback_data=f'{CALLBACK_MAKE_BET}{user}#2'),
        InlineKeyboardButton(text='3', callback_data=f'{CALLBACK_MAKE_BET}{user}#3'),
        InlineKeyboardButton(text='4', callback_data=f'{CALLBACK_MAKE_BET}{user}#4'),
        InlineKeyboardButton(text='5', callback_data=f'{CALLBACK_MAKE_BET}{user}#5'),
        InlineKeyboardButton(text='6', callback_data=f'{CALLBACK_MAKE_BET}{user}#6'),
        row_width=3
    )
    markup.add(
        InlineKeyboardButton(text='Чётное', callback_data=f'{CALLBACK_MAKE_BET}{user}#246'),
        InlineKeyboardButton(text='Не четное', callback_data=f'{CALLBACK_MAKE_BET}{user}#135'),
        row_width=2
    )
    markup.add(
        InlineKeyboardButton(text='Отмена', callback_data=f'{CALLBACK_MAKE_BET}{user}#cancel'),
    )
    return markup


def check_callback_make_bet(c: CallbackQuery):
    if not c.data.startswith(CALLBACK_MAKE_BET):
        return False

    return True


def check_callback_choose_bet(c: CallbackQuery):
    if not c.data.startswith(CALLBACK_CHOOSE_BET):
        return False

    return True


def check_callback_send_dice(c: CallbackQuery):
    if not c.data.startswith(CALLBACK_SEND_DICE):
        return False

    return True


def generate_id() -> str:
    return generate(''.join([ascii_lowercase, digits]), 22)


def get_owner(src: CallbackQuery | Message) -> str:
    return f"@{src.from_user.username}" if src.from_user.username else src.from_user.full_name


async def get_player_name(chat_id: int) -> str:
    chat = await bot.get_chat(chat_id=chat_id)
    player_name = (
        f"@{chat.username}"
        if chat.username
        else f'{chat.first_name}{f" {chat.last_name}" if chat.last_name else ""}'
    )
    return player_name


def parse_session_id(m: Message) -> str:
    return m.text.split()[1]


def append_session_text(session: Session, text: str) -> Session:
    session = Session(
        id=session.id,
        chat=session.chat,
        message_id=session.message_id,
        owner=session.owner,
        result=session.result,
        finished=session.finished,
        text=f'{session.text}\n{text}',
    )
    return session


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
# Bot handlers
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
@bot.callback_query_handler(func=check_callback_make_bet)
async def callback_make_bet(c: CallbackQuery):
    log.info(f'{log.chat_info(c.message)} Press make bet')
    # Парсим выбор игрока
    _, choose = c.data.split('#')

    if int(_[2:]) != c.from_user.id:
        log.info(f'{log.chat_info(c.message)} Wrong bet owner')
        await bot.answer_callback_query(
            callback_query_id=c.id,
            text='Это не твой выбор ставки',
            show_alert=True,
        )
        return

    # Если отмена удаляем сообщение
    if choose == 'cancel':
        log.info(f'{log.chat_info(c.message)} Cancel bet make')
        await bot.delete_message(
            chat_id=c.message.chat.id,
            message_id=c.message.message_id,
        )
        return
    log.info(f'{log.chat_info(c.message)} Choose: {choose}')

    # Получаем от кого пришел выбор ставки
    owner = get_owner(src=c)

    # Формируем текст выбором игрока
    if choose == '246':
        text = f'{owner} выбрал "Чётное"'
    elif choose == '135':
        text = f'{owner} выбрал "Не чётное"'
    else:
        text = f'{owner} выбрал "{choose}"'

    session_id = parse_session_id(m=c.message)
    session = await db.get_session(c.message, session_id=session_id)
    session = append_session_text(session=session, text=text)

    # Получаем владельца сессии для подписи кнопки
    session_owner = await get_player_name(chat_id=session.owner)

    await bot.edit_message_text(
        chat_id=session.chat,
        message_id=session.message_id,
        text=session.text,
        reply_markup=markup_make_session(owner=session_owner, owner_id=session.owner),
    )

    await db.update_session(c.message, session_id=session_id, text=session.text)

    type_bet = await db.get_type_bet_by_value(m=c.message, value=int(choose))

    bet_id = generate_id()

    await db.create_bet(
        m=c.message,
        bet_id=bet_id,
        session=session,
        user_id=c.from_user.id,
        type_bet=type_bet,
    )
    await bot.delete_message(
        chat_id=c.message.chat.id,
        message_id=c.message.message_id,
    )


@bot.callback_query_handler(func=check_callback_choose_bet)
async def callback_choose_bet(c: CallbackQuery):
    log.info(f'{log.chat_info(c.message)} Press choose bet')

    session_id = parse_session_id(m=c.message)

    bet = await db.get_bet_by_session_id(m=c.message, session_id=session_id, user=c.from_user.id)

    if bet:
        await bot.answer_callback_query(
            callback_query_id=c.id,
            text='Ты уже сделал ставку',
            show_alert=True,
        )
        return

    owner = get_owner(src=c)
    text = (c.message.text.splitlines()[0] + '\n\n'
                                             f'{owner} выбирает что выпадет на кубике.')
    await bot.send_message(
        chat_id=c.message.chat.id,
        text=text,
        reply_markup=markup_choose_bet(user=c.from_user.id),
        message_thread_id=c.message.message_thread_id,
        disable_notification=True,
    )


@bot.callback_query_handler(func=check_callback_send_dice)
async def callback_send_dice(c: CallbackQuery):
    log.info(f'{log.chat_info(c.message)} Press send dice')
    _, session_owner = c.data.split('#')
    if c.from_user.id != int(session_owner):
        log.info(f'{log.chat_info(c.message)} Wrong session owner')
        await bot.answer_callback_query(
            callback_query_id=c.id,
            text='Ты не можешь кинуть кубик',
            show_alert=True,
        )
        return False

    msg_dice = await bot.send_dice(
        chat_id=c.message.chat.id,
        message_thread_id=c.message.message_thread_id,
        disable_notification=True,
    )
    result = msg_dice.dice.value
    session_id = parse_session_id(m=c.message)
    log.info(f'{log.chat_info(c.message)} {session_id = } {result = }')
    session = await db.get_session(m=c.message, session_id=session_id)

    text_src = c.message.text.splitlines()
    text_res = '\n'.join(text_src[:4]) + f'\nВыпало: {result}\n\nСтавки:'
    bets = await db.get_bets_by_session_id(m=c.message, session_id=session_id)
    for bet in bets:
        type_bet = await db.get_type_bet_by_id(m=c.message, type_bet_id=bet.type_bet)
        if str(result) in str(type_bet.value):
            win: float = bet.amount * type_bet.mult
            is_win: int = 1
        else:
            win: float = 0
            is_win: int = 0

        player_name = await get_player_name(chat_id=bet.user)

        line = [_ for _ in text_src if _.split(' выбрал')[0] == player_name][-1]
        text_res += f'\n{line}{" - Выиграл" if is_win else ""}'

        await db.update_bet(m=c.message, bet_id=bet.id, finished=1, win=win, is_win=is_win)

    await bot.edit_message_text(
        chat_id=session.chat,
        message_id=session.message_id,
        text=text_res,
        reply_markup=None,
    )

    await db.update_session(
        m=c.message, text=c.message.text, session_id=session_id, result=result, finished=1
    )


@bot.message_handler(commands=['game', 'drop'])
async def cmd_game(m: Message):
    log.info(f'{log.chat_info(m)} {m.text}')
    owner = get_owner(src=m)
    session_id = generate_id()
    log.info(f'{log.chat_info(m)} {owner} start session {session_id}')
    msg_session = await bot.send_message(
        chat_id=m.chat.id,
        text=(f'Сессия: {session_id}'
              '\n\n'
              f'Начал сессию: {owner}'
              '\n\n'
              f'Можешь сделать ставку на то что выпадет на кубике, пока {owner} не кинул кубик.'
              '\n\n'
              f'Ставки:'),
        message_thread_id=m.message_thread_id,
        disable_notification=True,
        reply_markup=markup_make_session(owner=owner, owner_id=m.from_user.id),
    )
    await db.create_session(m=m, msg_session=msg_session, session_id=session_id)


@bot.message_handler(commands=['start', 'balance'])
async def cmd_start(m: Message):
    log.info(f'{log.chat_info(m)} {m.text}')
    user = await db.get_user(m)
    if not user:
        user = await db.create_user(m)

    log.info(f'{log.chat_info(m)} {user = }')
    await bot.send_message(
        chat_id=m.chat.id,
        text=(
            f'{"ID игрока:":<15}`{user.id}`'
            '\n'
            f'{"Баланс:":<16}`{user.balance}`'
        ),
        disable_notification=True,
        message_thread_id=m.message_thread_id,
    )


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
# Main
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
@log.catch
async def main():
    log.info('Start Bot')

    await db.connect()
    await bot.skip_updates()
    if DEBUG:
        bot.set_update_listener(update_listener)
    await bot.polling()


if __name__ == '__main__':
    asyncio.run(main())
