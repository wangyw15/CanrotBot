from typing import Annotated, Any

from fastapi import Body, FastAPI, Request
from fastapi.responses import JSONResponse
from jinja2 import Template
from nonebot import get_app, get_bot, logger
from nonebot.adapters.qq import Bot as QQBot
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import (
    Alconna,
    Args,
    CommandMeta,
    MsgTarget,
    Query,
    Subcommand,
    UniMessage,
    on_alconna,
)

from . import webhook
from .config import WebhookConfig

webhook_command = Alconna(
    "webhook",
    Subcommand(
        "create", Args["template_name", str, "default"], help_text="添加 Webhook"
    ),
    Subcommand("list", help_text="列出 Webhook"),
    Subcommand("delete", Args["token", str], help_text="删除 Webhook"),
    Subcommand("view", Args["token", str], help_text="查看 Webhook"),
    Subcommand(
        "template",
        Subcommand("create", Args["name", str]["content", str], help_text="添加模板"),
        Subcommand("list", help_text="列出模板"),
        Subcommand("delete", Args["name", str], help_text="删除模板"),
        Subcommand("view", Args["name", str], help_text="查看模板"),
        help_text="模板管理",
    ),
    meta=CommandMeta(description="提供Webhook推送功能"),
)

__plugin_meta__ = PluginMetadata(
    name="Webhook",
    description=webhook_command.meta.description,
    usage=webhook_command.get_help(),
    config=WebhookConfig,
)

webhook_matcher = on_alconna(
    webhook_command,
    block=True,
)


@webhook_matcher.assign("template.list")
async def _():
    templates = webhook.list_templates()
    if not templates:
        await webhook_matcher.finish("没有已创建的模板")
    await webhook_matcher.finish("\n".join([i for i in templates]))


@webhook_matcher.assign("template.create")
async def _(name: Query[str] = Query("name"), content: Query[str] = Query("content")):
    if webhook.create_template(name.result, content.result):
        await webhook_matcher.finish(f"模板 {name.result} 创建成功")
    else:
        await webhook_matcher.finish(
            f"模板 {name.result} 创建失败，相同名称的模板已存在"
        )


@webhook_matcher.assign("template.delete")
async def _(name: Query[str] = Query("name")):
    if webhook.delete_template(name.result):
        await webhook_matcher.finish(f"模板 {name.result} 删除成功")
    else:
        await webhook_matcher.finish(
            f"模板 {name.result} 删除失败，模板不存在或有在使用"
        )


@webhook_matcher.assign("template.view")
async def _(name: Query[str] = Query("name")):
    content = webhook.get_template(name.result)
    if not content:
        await webhook_matcher.finish(f"模板 {name.result} 不存在")
    await webhook_matcher.finish(content)


@webhook_matcher.assign("list")
async def _(target: MsgTarget):
    webhooks = webhook.list_webhooks(target)
    if not webhooks:
        await webhook_matcher.finish("没有已创建的 Webhook")
    await webhook_matcher.finish(
        "\n".join([f"{i.token} - {i.template_name}" for i in webhooks])
    )


@webhook_matcher.assign("delete")
async def _(target: MsgTarget, token: Query[str] = Query("token")):
    if webhook.delete_webhook(target, token.result):
        await webhook_matcher.finish("Webhook 删除成功")
    else:
        await webhook_matcher.finish("Webhook 删除失败")


@webhook_matcher.assign("view")
async def _(target: MsgTarget, token: Query[str] = Query("token")):
    if hook := webhook.get_webhook(token.result):
        tokens = [i.token for i in webhook.list_webhooks(target)]
        if hook.token in tokens:
            url = webhook.generate_webhook_url(token.result)
            await webhook_matcher.finish(
                f"token: {token.result}\n模板: {hook.template_name}\nURL: {url}"
            )
    await webhook_matcher.finish("Webhook token 不存在")


@webhook_matcher.assign("create")
async def _(
    target: MsgTarget,
    template_name: Query[str] = Query("template_name", "default"),
):
    token = webhook.create_webhook(template_name.result, target)
    url = webhook.generate_webhook_url(token)
    await webhook_matcher.finish(
        f"Webhook 创建成功\ntoken: {token}\n模板: {template_name.result}\nURL: {url}\n请妥善保管，不要随意泄露给他人，避免骚扰信息。"
    )


app: FastAPI = get_app()


@app.post("/webhook/{token}")
async def _(token: str, body: Annotated[Any, Body()], request: Request):
    """
    Webhook 推送
    """
    # 获取 Webhook 配置
    push_config = webhook.get_webhook(token)
    if not push_config:
        logger.error(f"Webhook not found: {token}")
        return JSONResponse(status_code=404, content={"message": "Webhook not found"})

    # 生成消息
    target = webhook.get_target(token)
    template = Template(webhook.get_template(push_config.template_name))
    # 官方 QQ 机器人不发送链接
    message = template.render(
        body=body,
        headers=dict(zip(request.headers.keys(), request.headers.values())),
        with_url=not isinstance(get_bot(target.self_id), QQBot),
    )

    # 推送消息
    logger.info("Received webhook and pushed")
    await UniMessage(message).send(target)
    return JSONResponse(status_code=200, content={"message": "success"})
