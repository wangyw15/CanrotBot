import uuid
from typing import Optional, Sequence

from nonebot import get_plugin_config
from nonebot_plugin_alconna import Target
from sqlalchemy import delete, insert, select

from canrotbot.essentials.libraries import database, path

from .config import WebhookConfig
from .data import Webhook

BUILTIN_TEMPLATE_PATH = path.get_asset_path("webhook")
CUSTOM_TEMPLATE_PATH = path.get_data_path("webhook")

config = get_plugin_config(WebhookConfig)


def generate_token() -> str:
    """
    生成 token

    :return: token
    """
    return str(uuid.uuid4()).replace("-", "")


def create_webhook(template_name: str, target: Target) -> str:
    """
    创建 webhook

    :param template_name: 模板名称
    :param target: 推送目标

    :return: token
    """
    with database.get_session().begin() as session:
        # 生成 token
        token = generate_token()
        while session.execute(select(Webhook).where(Webhook.token == token)).scalar():
            token = generate_token()

        # 创建 webhook
        session.execute(
            insert(Webhook).values(
                token=token,
                template_name=template_name,
                private_chat=target.private,
                channel_chat=target.channel,
                self_id=target.self_id,
                platform_id=target.id,
            )
        )

        return token


def list_webhooks(target: Target) -> Sequence[Webhook]:
    """
    列出 webhook

    :param target: 推送目标

    :return: webhook 列表
    """
    with database.get_session().begin() as session:
        ret = (
            session.execute(
                select(Webhook).where(
                    Webhook.private_chat == target.private,
                    Webhook.channel_chat == target.channel,
                    Webhook.self_id == target.self_id,
                    Webhook.platform_id == target.id,
                )
            )
            .scalars()
            .all()
        )
        session.expunge_all()
        return ret


def delete_webhook(target: Target, token: str) -> bool:
    """
    删除 webhook

    :param target: 推送目标
    :param token: token

    :return: 是否成功
    """
    with database.get_session().begin() as session:
        if session.execute(
            select(Webhook).where(
                Webhook.private_chat == target.private,
                Webhook.channel_chat == target.channel,
                Webhook.self_id == target.self_id,
                Webhook.platform_id == target.id,
                Webhook.token == token,
            )
        ).scalar():
            session.execute(
                delete(Webhook).where(
                    Webhook.private_chat == target.private,
                    Webhook.channel_chat == target.channel,
                    Webhook.self_id == target.self_id,
                    Webhook.platform_id == target.id,
                    Webhook.token == token,
                )
            )
            return True
        return False


def get_webhook(token: str) -> Optional[Webhook]:
    """
    获取 webhook

    :param token: token

    :return: webhook
    """
    with database.get_session().begin() as session:
        ret = session.execute(
            select(Webhook).where(Webhook.token == token)
        ).scalar_one_or_none()
        session.expunge_all()
        return ret


def create_template(name: str, content: str, force: bool = False) -> bool:
    """
    创建模板

    :param name: 模板名称
    :param content: 模板内容
    :param force: 是否强制覆盖

    :return: 是否成功
    """
    file = CUSTOM_TEMPLATE_PATH / (name + ".jinja")
    if file.exists() and not force:
        return False
    with file.open("w", encoding="utf-8") as f:
        f.write(content)
    return True


def list_templates() -> list[str]:
    """
    列出模板

    :return: 模板列表
    """
    templates: list[str] = []

    # 内置模板
    for file in BUILTIN_TEMPLATE_PATH.glob("*.jinja"):
        templates.append(file.stem)

    # 自定义模板
    for file in CUSTOM_TEMPLATE_PATH.glob("*.jinja"):
        if file.stem not in templates:
            templates.append(file.stem)

    return templates


def delete_template(name: str, force: bool = False) -> bool:
    """
    删除模板

    :param name: 模板名称
    :param force: 是否强制删除

    :return: 是否成功
    """
    file = CUSTOM_TEMPLATE_PATH / (name + ".jinja")
    # 检查模板是否存在
    if not file.exists():
        return False

    # 检查模板是否被使用
    with database.get_session().begin() as session:
        if (
            session.execute(
                select(Webhook).where(Webhook.template_name == name)
            ).scalar()
            and not force
        ):
            return False

    file.unlink()
    return True


def get_template(name: str) -> Optional[str]:
    """
    获取模板

    :param name: 模板名称

    :return: 模板内容
    """
    file = CUSTOM_TEMPLATE_PATH / (name + ".jinja")
    if file.exists():
        with file.open("r", encoding="utf-8") as f:
            return f.read()

    file = BUILTIN_TEMPLATE_PATH / (name + ".jinja")
    if file.exists():
        with file.open("r", encoding="utf-8") as f:
            return f.read()

    return None


def get_target(token: str) -> Optional[Target]:
    """
    获取推送目标

    :param token: token

    :return: 推送目标
    """
    with database.get_session().begin() as session:
        webhook = session.execute(
            select(Webhook).where(Webhook.token == token)
        ).scalar_one_or_none()
        if webhook:
            return Target(
                private=webhook.private_chat,
                channel=webhook.channel_chat,
                self_id=webhook.self_id,
                id=webhook.platform_id,
            )
        return None


def generate_webhook_url(token: str) -> str:
    """
    生成 webhook URL

    :param token: token

    :return: webhook URL
    """
    return f"{config.domain.rstrip('/')}/webhook/{token}"
