from nonebot import get_loaded_plugins
from typing import Tuple
from pathlib import Path
import json

from . import render_by_browser
from ..adapters import unified


_help_assets_path = Path(__file__).parent.parent / 'assets' / 'help'


async def generate_help_message(with_image: bool = True) -> Tuple[str, bytes | None]:
    text_msg: str = unified.util.MESSAGE_SPLIT_LINE
    plugin_metadatas: list[dict[str, str]] = []
    for plugin in get_loaded_plugins():
        if plugin.metadata:
            plugin_metadatas.append({
                'name': plugin.metadata.name,
                'description': plugin.metadata.description,
                'usage': plugin.metadata.usage
            })
            text_msg += f'{plugin.metadata.name}:\n' \
                        f'描述:\n{plugin.metadata.description}\n' \
                        f'用法:\n{plugin.metadata.usage}\n' + \
                        unified.util.MESSAGE_SPLIT_LINE + '\n'
    if with_image:
        with (_help_assets_path / 'template.html').open(encoding='utf-8') as f:
            html = f.read()
        img = await render_by_browser.render_html(
            html.replace("'{{DATA_HERE}}'", json.dumps(plugin_metadatas, ensure_ascii=False)),
            _help_assets_path, viewport={'width': 1000, 'height': 1000})
        return text_msg, img
    return text_msg, None
