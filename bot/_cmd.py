from collections.abc import Iterator, Iterable
from random import choice
from typing import Self, Protocol

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from ._db import Database


def setup_commands(application: Application, db: Database):
    application.add_handler(CommandHandler("help", action_help))

    application.add_handler(
        CommandHandler(
            "ypc",
            ActionDispatcher(db=db)
            .use(action_ypc)
            .use(action_ypc_add)
            .use(action_ypc_remove)
            .use(action_ypc_list)
            .use(action_ypc_note)
            .use(action_ypc_note_add)
            .use(action_ypc_note_remove)
            .use(action_ypc_help),
        )
    )


async def action_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    txt = _get_help_message()
    await update.message.reply_text(txt, reply_to_message_id=update.message.id)


def _get_help_message() -> str:
    return "\n".join(
        (
            "",
            "/ypc",
            "/ypc note <id>",
            "/ypc add <sentence>",
            "/ypc add_note <id> <note>",
            "/ypc remove <id>",
            "/ypc remove_note <id>",
            "/ypc list",
            "/ypc help",
        )
    )


class ActionHandler(Protocol):
    def __call__(self, args: list[str], *, db: Database) -> list[str]: ...


class ActionDispatcher:
    def __init__(self, *, db: Database):
        self._handler_list: list[ActionHandler] = []
        self._db = db

    def use(self, handler: ActionHandler) -> Self:
        self._handler_list.append(handler)
        return self

    async def __call__(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        if not update.message:
            return

        args = context.args or []

        for handler in self._handler_list:
            msg_list = handler(args, db=self._db)
            if not msg_list:
                continue

            for msg in msg_list:
                await update.message.reply_text(
                    msg, reply_to_message_id=update.message.id
                )

            break


def action_ypc_help(args: list[str], *, db: Database) -> list[str]:
    if len(args) != 1 or args[0] != "help":
        return []

    msg = _get_help_message()
    return [msg]


def action_ypc(args: list[str], *, db: Database) -> list[str]:
    if args:
        return []

    murmur_list = db.get_murmur_list()
    if not murmur_list:
        return []

    murmur = choice(murmur_list)
    return [murmur.sentence]


def action_ypc_add(args: list[str], *, db: Database) -> list[str]:
    if len(args) != 2 or args[0] != "add":
        return []

    sentence = args[1]
    id_ = db.add_murmur(sentence)
    return [str(id_)]


def action_ypc_remove(args: list[str], *, db: Database) -> list[str]:
    if len(args) != 2 or args[0] != "remove":
        return []

    id_ = int(args[1])
    db.remove_murmur(id_)
    return [str(id_)]


def action_ypc_list(args: list[str], *, db: Database) -> list[str]:
    if len(args) != 1 or args[0] != "list":
        return []

    murmur = db.get_murmur_list()
    msg_list: list[str] = []
    for chunk in _chunks_of(murmur, 100):
        msg = [f"{mm.id}: {mm.sentence}" for mm in chunk]
        msg = "\n" + "\n".join(msg)
        msg_list.append(msg)
    return msg_list


def action_ypc_note(args: list[str], *, db: Database) -> list[str]:
    if len(args) != 2 or args[0] != "note":
        return []

    id_ = int(args[1])
    try:
        murmur = db.get_murmur(id_)
    except Exception:
        return ["no such id"]
    return [murmur.note]


def action_ypc_note_add(args: list[str], *, db: Database) -> list[str]:
    if len(args) != 3 or args[0] != "add_note":
        return []

    id_ = int(args[1])
    note = args[2]
    db.set_note(id_, note)

    try:
        murmur = db.get_murmur(id_)
    except Exception:
        return ["no such id"]

    msg = f"{murmur.sentence}\n----\n{murmur.note}"
    return [msg]


def action_ypc_note_remove(args: list[str], *, db: Database) -> list[str]:
    if len(args) != 2 or args[0] != "remove_note":
        return []

    id_ = int(args[1])
    db.set_note(id_, "")

    try:
        murmur = db.get_murmur(id_)
    except Exception:
        return ["no such id"]

    return [murmur.sentence]


def _chunks_of[T](it: Iterable[T], size: int) -> Iterator[list[T]]:
    chunk = []
    for item in it:
        chunk.append(item)
        if len(chunk) == size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk
