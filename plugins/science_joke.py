from nonebot import on_command
from nonebot.adapters import Message, Event, Bot
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
import random

from ..libraries import random_text
from ..adapters import unified

__plugin_meta__ = PluginMetadata(
    name='理科笑话',
    description='随便来点理科笑话',
    usage='/<science-joke|science_joke|理科笑话>',
    config=None
)

_science_joke_data: list[str] = random_text.get_data('science_jokes')

# message
_science_joke_handler = on_command('science-joke', aliases={'理科笑话', 'science_joke'}, block=True)
@_science_joke_handler.handle()
async def _(event: Event, bot: Bot, args: Message = CommandArg()):
    name = await unified.util.get_user_name(event, bot, 'ta')
    if msg := args.extract_plain_text():
        name = msg
    await _science_joke_handler.finish(random.choice(_science_joke_data).format(name=name))
