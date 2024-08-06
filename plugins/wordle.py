import random

from nonebot import get_driver, on_command
from nonebot.adapters import Message
from nonebot.params import Arg
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State
from pydantic import BaseModel

from essentials.libraries import file, path

__plugin_meta__ = PluginMetadata(
    name="Wordle", description="Wordle小游戏", usage="/wordle", config=None
)


# config
class WordleConfig(BaseModel):
    wordle_correct: str = "⭕"
    wordle_medium: str = "❔"
    wordle_wrong: str = "❌"


config = WordleConfig.parse_obj(get_driver().config)

# load wordle data
WORDS = file.read_text(path.get_asset_path() / "wordle.json")


def get_wordle_result(answer: str, guess: str) -> str:
    result = ""
    for i in range(5):
        if guess[i] == answer[i]:
            result += config.wordle_correct
        elif guess[i] in answer:
            result += config.wordle_medium
        else:
            result += config.wordle_wrong
    return result


wordle_matcher = on_command("wordle", block=True)
WORDLE_ANSWER = "wordle_answer"
WORDLE_GUESSES = "wordle_guesses"


@wordle_matcher.handle()
async def _(state: T_State):
    state[WORDLE_ANSWER] = random.choice(WORDS)
    state[WORDLE_GUESSES] = []
    await wordle_matcher.send("新一轮wordle游戏开始，请输入单词")


@wordle_matcher.got("guess")
async def _(state: T_State, guess: Message = Arg()):
    # current guess
    guess = guess.extract_plain_text()
    # previous answers
    answer: str = state[WORDLE_ANSWER]
    # success
    if guess == answer:
        # don't forget to add current guess
        await wordle_matcher.finish(
            f"恭喜你猜对了！\n共用了{len(state[WORDLE_GUESSES]) + 1}次机会"
        )
    # invalid word
    elif guess not in WORDS:
        await wordle_matcher.reject("你输入的单词不在词库中")
    else:
        state[WORDLE_GUESSES].append(guess)
        msg = ""
        for i in state[WORDLE_GUESSES]:
            msg += f"{i}\n{get_wordle_result(answer, i)}\n"
        msg += f"第{len(state[WORDLE_GUESSES])}次"
        if len(state[WORDLE_GUESSES]) == 6:
            await wordle_matcher.finish(
                f"{msg}\n你已经用完了6次机会\n答案是{state[WORDLE_ANSWER]}"
            )
        await wordle_matcher.reject(msg)
