'''
if __name__ == '__main__' and __package__ == '':
    import os, sys, importlib
    parent_dir = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(os.path.dirname(parent_dir))
    __package__ = os.path.basename(parent_dir)
    importlib.import_module(__package__)
'''


import sys
import functools
import re
import inspect
import random
import functools
import json
import collections

from tornado import ioloop, gen, options, web, log, httpserver, httpclient, process
from wcpan.telegram import api

from . import settings, db


class KelThuzad(api.BotAgent):

    def __init__(self, api_token):
        super(KelThuzad, self).__init__(api_token)

        self._text_handlers = []

    def add_text_handlers(self, handlers):
        self._text_handlers.extend(handlers)

    @property
    def text_handlers(self):
        return self._text_handlers


def command_filter(pattern):
    def real_decorator(fn):
        @functools.wraps(fn)
        def callee(*args, **kwargs):
            spec = inspect.getfullargspec(fn)
            if 'self' in spec.args:
                self = args[0]
                message = args[1]
            else:
                self = None
                message = args[0]

            m = re.match(pattern, message.text.strip())
            if not m:
                return None
            args = m.groups()

            if self:
                return fn(self, message, *args)
            else:
                return fn(message, *args)
        return callee
    return real_decorator


class UpdateHandler(api.BotHookHandler):

    async def on_text(self, message):
        id_ = message.message_id
        chat = message.chat
        text = message.text
        lich = self.settings['lich']
        for handler in lich.text_handlers:
            result = handler(message)
            if result:
                result = await result
                await lich.client.send_message(chat.id_, result, reply_to_message_id=id_)
                break
        else:
            print('update handler: ', message.text)


class NOPHandler(web.RequestHandler):

    def get(self):
        print('??')

    def post(self):
        print(self.request.body)


class YPCHandler(object):

    def __init__(self):
        pass

    @command_filter(r'^/ypc(@\S+)?$')
    async def ypc(self, message, *args, **kwargs):
        with db.Session() as session:
            murmur = session.query(db.Murmur).all()
            if not murmur:
                return None
            mm = random.choice(murmur)
            return mm.sentence

    @command_filter(r'^/ypc(@\S+)?\s+add\s+(.+)$')
    async def ypc_add(self, message, *args, **kwargs):
        with db.Session() as session:
            mm = db.Murmur(sentence=args[1])
            session.add(mm)
            session.commit()
            return str(mm.id)

    @command_filter(r'^/ypc(@\S+)?\s+remove\s+(\d+)$')
    async def ypc_remove(self, message, *args, **kwargs):
        try:
            with db.Session() as session:
                mm = session.query(db.Murmur).filter_by(id=int(args[1]))
                for m in mm:
                    session.delete(m)
                return args[1]
        except Exception:
            return None

    @command_filter(r'^/ypc(@\S+)?\s+list$')
    async def ypc_list(self, message, *args, **kwargs):
        o = ['']
        with db.Session() as session:
            murmur = session.query(db.Murmur)
            for mm in murmur:
                o.append('{0}: {1}'.format(mm.id, mm.sentence))
        return '\n'.join(o)

    @command_filter(r'^/ypc(@\S+)?\s+help$')
    async def ypc_help(self, message, *args, **kwargs):
        return '\n'.join((
            '',
            '/ypc',
            '/ypc story <id>',
            '/ypc add <sentence>',
            '/ypc addstory <id> <sentence>',
            '/ypc remove <id>',
            '/ypc removestory <id> <sentence>',
            '/ypc list',
            '/ypc help',
        ))

    @command_filter(r'^/ypc(@\S+)?\s+story\s+(\d+)$')
    async def ypc_story(self, message, *args, **kwargs):
        try:
            with db.Session() as session:
                mm = session.query(db.MurmurStory).filter_by(murmur_id=int(args[1]))
                if mm.count() < 1:
                    return args[1] + '??'
                m = mm.first()
                return m.sentence
        except Exception:
            return None

    @command_filter(r'^/ypc(@\S+)?\s+addstory\s+(\d+)\s+(.+)$')
    async def ypc_story_add(self, message, *args, **kwargs):
        try:
            with db.Session() as session:
                mm = session.query(db.Murmur).filter_by(id=int(args[1]))
                if mm.count() < 1:
                    return args[1] + '??'
                reply = str(args[2])
                story = session.query(db.MurmurStory).filter_by(murmur_id=int(args[1]))
                if story.count() < 1:
                    story = db.MurmurStory(murmur_id=int(args[1]), sentence=args[2])
                    session.add(story)
                else:
                    story = story.first()
                    reply = story.sentence +'\n----\n' + str(args[2])
                    story.sentence = str(args[2])

                session.commit()
                return reply
        except Exception:
            return None

    @command_filter(r'^/ypc(@\S+)?\s+removestory\s+(\d+)$')
    async def ypc_story_remove(self, message, *args, **kwargs):
        try:
            with db.Session() as session:
                mm = session.query(db.MurmurStory).filter_by(murmur_id=int(args[1]))
                for m in mm:
                    session.delete(m)
                return 'story ' + args[1]
        except Exception:
            return None


@command_filter(r'^/help(@\S+)?$')
async def help(message, *args, **kwargs):
    return '\n'.join((
        '',
        '/ypc',
        '/ypc story <id>'
        '/ypc add <sentence>',
        '/ypc addstory <id> <sentence>',
        '/ypc remove <id>',
        '/ypc removestory <id> <sentence>',
        '/ypc list',
        '/ypc help',
    ))


async def shell_out(*args, **kwargs):
    stdin = kwargs.get('stdin', None)
    if stdin is not None:
        p = process.Subprocess(args, stdin=process.Subprocess.STREAM, stdout=process.Subprocess.STREAM)
        await p.stdin.write(stdin.encode('utf-8'))
        p.stdin.close()
    else:
        p = process.Subprocess(args, stdout=process.Subprocess.STREAM)
    out = await p.stdout.read_until_close()
    exit_code = await p.wait_for_exit(raise_error=True)
    return out.decode('utf-8')


'''
async def forever():
    api_token = options.options.api_token

    kel_thuzad = KelThuzad(api_token)
    ypc = YPCHandler()

    kel_thuzad.add_text_handlers([
        help,
        ypc.ypc,
        ypc.ypc_add,
        ypc.ypc_remove,
        ypc.ypc_list,
        ypc.ypc_help,
    ])

    await kel_thuzad.poll()
'''


async def setup():
    api_token = options.options.api_token
    dsn = options.options.database
    db.prepare(dsn)

    kel_thuzad = KelThuzad(api_token)
    ypc = YPCHandler()

    kel_thuzad.add_text_handlers([
        help,
        ypc.ypc,
        ypc.ypc_add,
        ypc.ypc_remove,
        ypc.ypc_story,
        ypc.ypc_story_add,
        ypc.ypc_story_remove,
        ypc.ypc_list,
        ypc.ypc_help,
    ])

    application = web.Application([
        (r'^/{0}$'.format(api_token), UpdateHandler),
        (r'.*', NOPHandler),
    ], lich=kel_thuzad)
    application.listen(7443)

    await kel_thuzad.listen('https://www.wcpan.me/bot/telegram/ypc/{0}'.format(api_token))


def parse_config(path):
    data = settings.load(path)
    options.options.api_token = data['api_token']
    options.options.database = data['database']


def main(args=None):
    if args is None:
        args = sys.argv

    log.enable_pretty_logging()
    options.define('config', default=None, type=str, help='config file path', metavar='telezombie.yaml', callback=parse_config)
    options.define('api_token', default=None, type=str, help='API token', metavar='<token>')
    options.define('database', default=None, type=str, help='database URI', metavar='<uri>')
    remains = options.parse_command_line(args)

    main_loop = ioloop.IOLoop.instance()

    main_loop.add_callback(setup)

    main_loop.start()
    main_loop.close()

    return 0


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
