from dataclasses import dataclass
import os

from telegram.ext import Application

from ._cmd import setup_commands
from ._db import initialize, Database


@dataclass(kw_only=True, frozen=True)
class Context:
    api_token: str
    database_url: str


def main() -> int:
    context = Context(
        api_token=os.environ["API_TOKEN"], database_url=os.environ["DATABASE_URL"]
    )

    initialize(context.database_url)
    db = Database(context.database_url)

    application = Application.builder().token(context.api_token).build()

    setup_commands(application, db)

    application.run_polling()

    return 0
