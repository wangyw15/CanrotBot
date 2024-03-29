import json
from typing import Tuple

from nonebot import get_loaded_plugins

from storage import asset
from . import render_by_browser, util

_help_assets = asset.AssetManager("help")
_plugin_metadatas: list[dict[str, str]] = []
_help_text: str | None = None
_help_image: bytes | None = None


async def generate_help_message(with_image: bool = True) -> Tuple[str, bytes | None]:
    global _plugin_metadatas, _help_text, _help_image
    # 获取所有插件信息
    if not _plugin_metadatas:
        for plugin in get_loaded_plugins():
            if plugin.metadata:
                _plugin_metadatas.append(
                    {
                        "name": plugin.metadata.name,
                        "description": plugin.metadata.description,
                        "usage": plugin.metadata.usage,
                    }
                )
    # 文本帮助信息
    if _help_text is None:
        _help_text = util.MESSAGE_SPLIT_LINE
        for plugin in _plugin_metadatas:
            _help_text += (
                f'{plugin["name"]}:\n'
                f'描述:\n{plugin["description"]}\n'
                f'用法:\n{plugin["usage"]}\n' + util.MESSAGE_SPLIT_LINE + "\n"
            )
        _help_text = _help_text.strip()
    # 图片帮助信息
    if with_image and _help_image is None:
        with _help_assets("template.html").open(encoding="utf-8") as f:
            html = f.read()
        _help_image = await render_by_browser.render_html(
            html.replace(
                "'{{DATA_HERE}}'", json.dumps(_plugin_metadatas, ensure_ascii=False)
            ),
            _help_assets(),
            viewport={"width": 1000, "height": 1000},
        )
    # 按需返回
    if with_image:
        return _help_text, _help_image
    return _help_text, None
