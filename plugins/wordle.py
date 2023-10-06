import random

from nonebot import get_driver, on_command
from nonebot.adapters import Message
from nonebot.params import Arg
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State
from pydantic import BaseModel

from storage import asset

__plugin_meta__ = PluginMetadata(
    name='Wordle',
    description='Wordle小游戏',
    usage='/wordle 开始游戏',
    config=None
)


# config
class WordleConfig(BaseModel):
    wordle_correct: str = '⭕'
    wordle_medium: str = '❔'
    wordle_wrong: str = '❌'


config = WordleConfig.parse_obj(get_driver().config)

# load wordle data
words = asset.load_json('reply.json')


def get_wordle_result(answer: str, guess: str) -> str:
    result = ''
    for i in range(5):
        if guess[i] == answer[i]:
            result += config.wordle_correct
        elif guess[i] in answer:
            result += config.wordle_medium
        else:
            result += config.wordle_wrong
    return result


wordle = on_command('wordle', block=True)
WORDLE_ANSWER = 'wordle_answer'
WORDLE_GUESSES = 'wordle_guesses'


@wordle.handle()
async def _(state: T_State):
    state[WORDLE_ANSWER] = random.choice(words)
    state[WORDLE_GUESSES] = []
    await wordle.send('新一轮wordle游戏开始，请输入单词')


@wordle.got('guess')
async def _(state: T_State, guess: Message = Arg()):
    guess = guess.extract_plain_text()
    answer: str = state[WORDLE_ANSWER]
    if guess == answer:
        await wordle.finish(f'恭喜你猜对了！\n共用了{len(state[WORDLE_ANSWER])}次机会')
    elif guess not in words:
        await wordle.reject('你输入的单词不在词库中')
    else:
        state[WORDLE_GUESSES].append(guess)
        msg = ''
        for i in state[WORDLE_GUESSES]:
            msg += f'{i}\n{get_wordle_result(answer, i)}\n'
        msg += f'第{len(state[WORDLE_GUESSES])}次'
        if len(state[WORDLE_GUESSES]) == 6:
            await wordle.finish(f'{msg}\n你已经用完了6次机会\n答案是{state[WORDLE_ANSWER]}')
        await wordle.reject(msg)
