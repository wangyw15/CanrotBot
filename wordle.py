from nonebot import get_driver, on_command
from nonebot.adapters import Message
from nonebot.params import Arg
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State
from pydantic import BaseModel, validator
import random

from .data import get_data

# config
class WordleConfig(BaseModel):
    wordle_enabled: bool = True
    wordle_correct: str = '⭕'
    wordle_medium: str = '❔'
    wordle_wrong: str = '❌'

    @validator('wordle_enabled')
    def wordle_enabled_validator(cls, v):
        if not isinstance(v, bool):
            raise ValueError('wordle_enabled must be a bool')
        return v
    
# metadata
__plugin_meta__ = PluginMetadata(
    name='Wordle',
    description='Wordle game',
    usage='/wordle',
    config=WordleConfig,
)

config = WordleConfig.parse_obj(get_driver().config)

# plugin enabled
async def is_enabled() -> bool:
    return config.wordle_enabled

# load wordle data
words = [x[1] for x in get_data('wordle')]

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

wordle = on_command('wordle', rule=is_enabled, block=True)
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
    elif not guess in words:
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
