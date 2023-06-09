import random

import jieba
from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

import essentials.libraries.user
from essentials.libraries import asset, util

__plugin_meta__ = PluginMetadata(
    name='实验性功能',
    description='还在测试中的奇妙功能',
    usage='快速开发懒得写',
    config=None
)

jieba.add_word('{name}')
jieba.add_word('{me}')
_reply_data: list[list[str]] = [list(jieba.lcut(x['response'])) for x in asset.load_json('reply.json')]


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


transitions = markov_chain(_reply_data, 3)

_generative_response_handler = on_command('generative_reponse', aliases={'gr', '生成回复'}, block=True)
@_generative_response_handler.handle()
async def _(bot, event, msg: Message = CommandArg()):
    my_name = await util.get_bot_name(event, bot, '我')
    user_name = await essentials.libraries.user.get_user_name(event, bot, '主人')
    length = 50
    if msg := msg.extract_plain_text().strip():
        length = int(msg)
    await _generative_response_handler.finish(generate_reponse(transitions, length).format(
        name=user_name, me=my_name) + '\n--------------------\n实验性功能，不保证语句合理性')
    
