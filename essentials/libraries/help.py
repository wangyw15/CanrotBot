import json

from nonebot import get_loaded_plugins
from nonebot.plugin import PluginMetadata

from . import path, render_by_browser, util

ASSET_PATH = path.get_asset_path("help")


def get_plugins_metadata() -> dict[str, PluginMetadata]:
    """
    获取所有插件的元数据

    :return: {插件名: 元数据}
    """
    return {
        plugin.name: plugin.metadata
        for plugin in get_loaded_plugins()
        if plugin.metadata
    }


def generate_help_text() -> str:
    """
    生成文本帮助信息

    :return: 帮助信息文本
    """
    return f"\n{util.MESSAGE_SPLIT_LINE}\n".join(
        [
            f"{metadata.name}:\n描述:\n{metadata.description}\n用法:\n{metadata.usage}"
            for _, metadata in get_plugins_metadata().items()
        ]
    )


async def generate_help_image() -> bytes:
    """
    生成图片帮助信息

    :return: 帮助信息图片
    """
    # 生成元数据对象
    metadata_obj: list[dict[str, str]] = [
        {
            "name": metadata.name,
            "description": metadata.description,
            "usage": metadata.usage,
        }
        for _, metadata in get_plugins_metadata().items()
    ]

    html = (ASSET_PATH / "template.html").read_text(encoding="utf-8")
    return await render_by_browser.render_html(
        html.replace("'{{DATA_HERE}}'", json.dumps(metadata_obj, ensure_ascii=False)),
        ASSET_PATH,
        viewport={"width": 1000, "height": 1000},
    )
