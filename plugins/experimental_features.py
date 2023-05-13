from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
import jieba
import random

from ..libraries.universal_adapters import get_user_name, get_bot_name
from ..libraries.assets import get_assets

__plugin_meta__ = PluginMetadata(
    name='实验性功能',
    description='还在测试中的奇妙功能',
    usage='快速开发懒得写',
    config=None
)

jieba.add_word('{name}')
jieba.add_word('{me}')
reply_data: list[list[str]] = [list(jieba.lcut(x[2])) for x in get_assets('reply')]

# generate markov chain
def markov_chain(data: list[list[str]], n=1) -> dict[str, dict[str, float]]:
    transitions: dict[str, dict[str, float]] = {}
    for words in data:
        conbined = []
        for i in range(0, len(words), n):
            conbined.append(''.join(words[i:i+n]))
        name = ''
        for i in range(len(words) - 1):
            current = words[i]
            if current not in transitions:
                transitions[current] = {}
            if words[i + 1] not in transitions[current]:
                transitions[current][words[i + 1]] = 0
            transitions[current][words[i + 1]] += 1
    return transitions

def generate_reponse(transitions: dict[str, dict[str, float]], max_len = 50) -> str:
    # generate response
    current = random.choice(list(transitions.keys()))
    response = [current]
    for i in range(max_len):
        if current not in transitions:
            break
        next = random.choices(list(transitions[current].keys()), list(transitions[current].values()))[0]
        response.append(next)
        current = next
    return ''.join(response)

transitions = markov_chain(reply_data, 3)

generative_reponse = on_command('generative_reponse', aliases={'gr', '生成回复'}, block=True)
@generative_reponse.handle()
async def _(bot, event, msg: Message = CommandArg()):
    my_name = await get_bot_name(event, bot, '我')
    user_name = await get_user_name(event, bot, '主人')
    length = 50
    if msg := msg.extract_plain_text().strip():
        length = int(msg)
    await generative_reponse.finish(generate_reponse(transitions, length).format(name=user_name, me=my_name) + '\n--------------------\n实验性功能，不保证语句合理性')
    
