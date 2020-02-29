import logging
import os
import time
from functools import wraps

import delegator
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
from telegram.ext.dispatcher import run_async

import settings

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# https://github.com/python-telegram-bot/python-telegram-bot/wiki/Code-snippets

# TODO auth delegator

def restricted(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in settings.ENABLED_USERS:
            print(f"Unauthorized access denied for {user_id}.")
            return
        return func(update, context, *args, **kwargs)
    return wrapped


@restricted
def start(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text(
        "Support command:\r\n"
        "/script run scripts in ./scripts directory\r\n"
        "/tasks show all running tasks\r\n"
        "/sudo_login call sudo\r\n"
        "/kill kill running task"
    )


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, update.error)


def __do_exec(cmd, update, context, cwd=None):
    c = delegator.run(cmd, block=False, cwd=cwd)
    out = ''
    tasks = context.user_data.setdefault('tasks', set([]))
    task = (c.pid, cmd, c)
    tasks.add(task)
    start_time = time.time()
    idx = 0
    for line in c.subprocess:
        out += line
        cost_time = time.time() - start_time
        if cost_time > 5:
            update.message.reply_text(out[:-settings.MAX_TASK_OUTPUT])
            idx += 1
            out = ''
            start_time = time.time()
        if idx > 3:
            print('not finished, you can kill by send xxx')
            break
    c.block()
    tasks.remove(task)
    if out:
        update.message.reply_text(out[:-settings.MAX_TASK_OUTPUT])
    if idx > 3:
        update.message.reply_text(f'Task finished: {cmd}')


@run_async
@restricted
def do_exec(update, context):
    """Add a job to the queue."""
    cmd = update.message.text
    __do_exec(cmd, update, context)


@restricted
def do_tasks(update, context):
    tasks = context.user_data.get('tasks')
    msg = '\r\n'.join([', '.join(e[:2]) for e in tasks])
    update.message.reply_text(msg)


@restricted
def do_script(update, context):
    args = context.args.copy()
    if args:
        args[0] = os.path.join(settings.SCRIPTS_ROOT_PATH, args[0])
        cmd = ' '.join(args)
        __do_exec(cmd, update, context)
        return
    scripts = '\r\n'.join(
        os.path.join(r[len(settings.SCRIPTS_ROOT_PATH):], file)
        for r, d, f in os.walk(settings.SCRIPTS_ROOT_PATH) for file in f
    )
    msg = "Usage: /script script_name args\r\n"
    msg += scripts
    update.message.reply_text(msg)


@restricted
def do_kill(update, context):
    if not context.args:
        update.message.reply_text('Usage: /kill pid')
        return

    pid = context.args[0]
    tasks = context.user_data.get('tasks')
    for task in tasks:
        if task[0] == pid:
            task[2].kill()
            update.message.reply_text(f'killed: {task[1]}')
            return
    update.message.reply_text(f'pid "{pid}" not find')


@restricted
def do_sudo_login(update, context):
    password = context.args[0]
    c = delegator.chain(f'echo "{password}" | sudo -S xxxvvv')
    out = c.out
    if 'xxxvvv: command not found' in out:
        update.message.reply_text(f'sudo successed.')
    update.message.reply_text(f'sudo failed.')


def main():
    updater = Updater(settings.TOKEN, use_context=True)
    # check user name

    dp = updater.dispatcher

    # TODO cwd
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))

    dp.add_handler(CommandHandler("script", do_script, pass_args=True))
    dp.add_handler(CommandHandler("tasks", do_tasks, pass_user_data=True))
    dp.add_handler(CommandHandler("sudo_login", do_sudo_login, pass_args=True))
    dp.add_handler(CommandHandler("kill", do_kill, pass_args=True, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.text, do_exec, pass_user_data=True))

    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
