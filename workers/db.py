import aiosqlite
import telebot
from cfg.config import (
    PATH_DATABASE,
    PATH_DIR_DATABASE, DATABASE_NAME,
)
from helpers.typehints import User, Session, TypeBet, Bet


class DataBase:

    def __init__(self, log):
        self.__log = log
        PATH_DIR_DATABASE.mkdir(parents=True, exist_ok=True)

    async def __execute_sql(self, sql, values: tuple = None):
        self.__log.debug(f'Execute {sql = } , {values = }')
        async with aiosqlite.connect(PATH_DATABASE) as db:
            await db.execute(sql) if not values else await db.execute(sql, values)
            await db.commit()

    async def __execute_sql_fetchone(self, sql, values):
        self.__log.debug(f'Execute fetchone {sql = } , {values = }')
        async with aiosqlite.connect(PATH_DATABASE) as db:
            async with db.execute(sql, values) as cursor:
                data = await cursor.fetchone()
        return data

    async def __execute_sql_fetchall(self, sql, values):
        self.__log.debug(f'Execute fetchall {sql = } , {values = }')
        async with aiosqlite.connect(PATH_DATABASE) as db:
            async with db.execute(sql, values) as cursor:
                data = await cursor.fetchall()
        return data

    async def __create_table_users(self):
        self.__log.debug(f'Create table: users')
        fields = {
            'id': 'INT PRIMARY KEY',
            'balance': 'REAL',
        }
        self.__log.debug(f'{fields = }')
        sql_req = (
                'CREATE TABLE IF NOT EXISTS users(' +
                ', '.join([f'{k} {v}' for k, v in fields.items()]) +
                ' );'
        )
        await self.__execute_sql(sql_req)

    async def __create_table_type_bet(self):
        self.__log.debug(f'Create table: type_bet')
        fields = {
            'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
            'mult': 'REAL',
            'value': 'INT',
        }
        self.__log.debug(f'{fields = }')
        sql_req = (
                'CREATE TABLE IF NOT EXISTS type_bet(' +
                ', '.join([f'{k} {v}' for k, v in fields.items()]) +
                ' );'
        )
        await self.__execute_sql(sql_req)

    async def __create_table_sessions(self):
        self.__log.debug(f'Create table: sessions')
        fields = {
            'id': 'TEXT PRIMARY KEY',
            'chat': 'INT',
            'message_id': 'INT',
            'owner': 'INT',
            'result': 'INT',
            'finished': 'INT',
            'text': 'TEXT',
        }
        self.__log.debug(f'{fields = }')
        sql_req = (
                'CREATE TABLE IF NOT EXISTS sessions(' +
                ', '.join([f'{k} {v}' for k, v in fields.items()]) +
                ' );'
        )
        await self.__execute_sql(sql_req)

    async def __create_table_bets(self):
        self.__log.debug(f'Create table: bets')
        fields = {
            'id': 'TEXT PRIMARY KEY',
            'session': 'INT',
            'chat': 'INT',
            'user': 'INT',
            'amount': 'INT',
            'finished': 'INT',
            'bet': 'INT',
            'win': 'REAL',
            'is_win': 'INT',
        }
        self.__log.debug(f'{fields = }')
        sql_req = (
                'CREATE TABLE IF NOT EXISTS bets(' +
                ', '.join([f'{k} {v}' for k, v in fields.items()]) +
                ' );'
        )
        await self.__execute_sql(sql_req)

    async def __create_db(self):
        self.__log.debug(f'Create DB if not exist: {PATH_DATABASE}')
        await self.__create_table_users()
        await self.__create_table_type_bet()
        await self.__create_table_sessions()
        await self.__create_table_bets()

    async def __fill_table_type_bet(self):
        self.__log.debug('Fill table type_bet')
        sql_req = "INSERT INTO type_bet (id, mult, value) VALUES(?, ?, ?);"
        types_bet = [
            (None, 1.6, '246'),
            (None, 1.6, '135'),
            (None, 3, '1'),
            (None, 3, '2'),
            (None, 3, '3'),
            (None, 3, '4'),
            (None, 3, '5'),
            (None, 3, '6'),
        ]
        for type_bet in types_bet:
            await self.__execute_sql(sql=sql_req, values=type_bet)

    async def connect(self):
        self.__log.info(f'Connect to DB: {DATABASE_NAME}')
        if not PATH_DATABASE.exists():
            await self.__create_db()
            await self.__fill_table_type_bet()

    async def create_user(self, m: telebot.types.Message) -> User:
        self.__log.debug(f'{self.__log.chat_info(m)} Create user {m.chat.id} in DB')
        sql_req = "INSERT INTO users VALUES(?, ?);"
        values = (m.from_user.id, 0)
        await self.__execute_sql(sql=sql_req, values=values)
        return User(*values)

    async def get_user(self, m: telebot.types.Message) -> User | None:
        self.__log.debug(f'{self.__log.chat_info(m)} Get user {m.chat.id} from DB')
        sql_req = "SELECT * FROM users WHERE id=?;"
        values = (m.from_user.id,)
        data = await self.__execute_sql_fetchone(sql=sql_req, values=values)
        if data is None:
            return None
        return User(*data)

    async def create_session(self, m: telebot.types.Message, msg_session: telebot.types.Message,
                             session_id: str) -> Session:
        self.__log.debug(f'{self.__log.chat_info(m)} Create session {session_id} in DB')
        sql_req = "INSERT INTO sessions (id, chat, message_id, owner, result, finished, text) VALUES(?,?,?,?,?,?,?);"
        values = (session_id, m.chat.id, msg_session.message_id, m.from_user.id, -1, 0, msg_session.text)
        await self.__execute_sql(sql=sql_req, values=values)
        return Session(*values)

    async def get_session(self, m: telebot.types.Message, session_id: str) -> Session | None:
        self.__log.debug(f'{self.__log.chat_info(m)} Get session {session_id} from DB')
        sql_req = "SELECT * FROM sessions WHERE id=?;"
        values = (session_id,)
        data = await self.__execute_sql_fetchone(sql=sql_req, values=values)
        if data is None:
            return None
        return Session(*data)

    async def update_session(self, m: telebot.types.Message, session_id: str, text: str, result: int = -1,
                             finished: int = 0):
        self.__log.debug(f'{self.__log.chat_info(m)} Update session {session_id} in DB')
        sql_req = "UPDATE sessions SET result = ?, finished = ?, text = ? WHERE id=?;"
        values = (result, finished, text, session_id,)
        await self.__execute_sql(sql=sql_req, values=values)

    async def get_type_bet_by_id(self, m: telebot.types.Message, type_bet_id: int) -> TypeBet | None:
        self.__log.debug(f'{self.__log.chat_info(m)} Get type_bet with {type_bet_id = } from DB')
        sql_req = "SELECT * FROM type_bet WHERE id=?;"
        values = (type_bet_id,)
        data = await self.__execute_sql_fetchone(sql=sql_req, values=values)
        if data is None:
            return None
        return TypeBet(*data)

    async def get_type_bet_by_value(self, m: telebot.types.Message, value: int) -> TypeBet | None:
        self.__log.debug(f'{self.__log.chat_info(m)} Get type_bet with {value = } from DB')
        sql_req = "SELECT * FROM type_bet WHERE value=?;"
        values = (value,)
        data = await self.__execute_sql_fetchone(sql=sql_req, values=values)
        if data is None:
            return None
        return TypeBet(*data)

    async def create_bet(self, m: telebot.types.Message, bet_id: str,
                         session: Session, user_id: int, type_bet: TypeBet) -> Bet:
        self.__log.debug(f'{self.__log.chat_info(m)} Create bet in {session.id} in DB')
        sql_req = ("INSERT INTO bets (id, session, chat, user, amount, finished, bet, win, is_win) "
                   "VALUES(?,?,?,?,?,?,?,?,?);")
        values = (bet_id, session.id, session.chat, user_id, 5, 0, type_bet.id, 0, 0)
        await self.__execute_sql(sql=sql_req, values=values)
        return Bet(*values)

    async def get_bet_by_id(self, m: telebot.types.Message, bet_id: str) -> Bet | None:
        self.__log.debug(f'{self.__log.chat_info(m)} Get bet by {bet_id = } from DB')
        sql_req = "SELECT * FROM bets WHERE id=?;"
        values = (bet_id,)
        data = await self.__execute_sql_fetchone(sql=sql_req, values=values)
        if data is None:
            return None
        return Bet(*data)

    async def get_bet_by_session_id(self, m: telebot.types.Message, session_id: str, user: int) -> Bet | None:
        self.__log.debug(f'{self.__log.chat_info(m)} Get bet by {session_id = } from DB')
        sql_req = "SELECT * FROM bets WHERE session=? and user=?;"
        values = (session_id, user,)
        data = await self.__execute_sql_fetchone(sql=sql_req, values=values)
        if data is None:
            return None
        return Bet(*data)

    async def get_bets_by_session_id(self, m: telebot.types.Message, session_id: str) -> list[Bet] | None:
        self.__log.debug(f'{self.__log.chat_info(m)} Get bets by {session_id = } from DB')
        sql_req = "SELECT * FROM bets WHERE session=?;"
        values = (session_id,)
        datas = await self.__execute_sql_fetchall(sql=sql_req, values=values)
        if datas is None:
            return None
        return [Bet(*data) for data in datas]

    async def update_bet(self, m: telebot.types.Message, bet_id: str, finished: int = 0, win: float = 0, is_win: int = 0):
        self.__log.debug(f'{self.__log.chat_info(m)} Update bet {bet_id} with finished=1 in DB')
        sql_req = "UPDATE bets SET finished = ?, win = ?, is_win = ? WHERE id=?;"
        values = (finished, win, is_win, bet_id,)
        await self.__execute_sql(sql=sql_req, values=values)
