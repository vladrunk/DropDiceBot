from typing import NamedTuple


class User(NamedTuple):
    id: int
    balance: float


class TypeBet(NamedTuple):
    id: int
    mult: int
    value: int


class Session(NamedTuple):
    id: str
    chat: int
    message_id: int
    owner: int
    result: int
    finished: int
    text: str


class Bet(NamedTuple):
    id: str
    session: str
    chat: int
    user: int
    amount: int
    finished: int
    type_bet: int
    win: float
    is_win: int
