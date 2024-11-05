import json
from time import sleep
from typing import cast

from httpx import AsyncClient
from nonebot_plugin_alconna import Target
from sqlalchemy import ColumnElement, delete, insert, select

from canrotbot.essentials.libraries import database

from .data import (
    Account,
    ForumSigninResultData,
    ForumSigninResultList,
    SigninResultSubscriber,
)
from .model import ForumSigninResultType


def add_account(owner_user_id: int, bduss: str, stoken: str, alias: str = "") -> int:
    """
    添加百度账号

    :param owner_user_id: 用户ID
    :param bduss: BDUSS
    :param stoken: STOKEN
    :param alias: 别名

    :return: 账号ID
    """
    with database.get_session().begin() as session:
        account = Account(
            owner_user_id=owner_user_id,
            bduss=bduss,
            stoken=stoken,
            alias=alias,
        )
        session.add(account)
        session.flush()
        session.commit()
        return account.id


def delete_account(owner_user_id: int, account_id: int) -> None:
    """
    删除百度账号

    :param owner_user_id: 用户ID
    :param account_id: 账号ID
    """
    with database.get_session().begin() as session:
        session.execute(
            delete(Account)
            .where(cast(ColumnElement[bool], Account.owner_user_id == owner_user_id))
            .where(cast(ColumnElement[bool], Account.id == account_id))
        )
        session.commit()


def delete_account_all(owner_user_id: int) -> None:
    """
    删除所有百度账号

    :param owner_user_id: 用户ID
    """
    with database.get_session().begin() as session:
        session.execute(
            delete(Account).where(
                cast(ColumnElement[bool], Account.owner_user_id == owner_user_id)
            )
        )
        session.commit()


def get_account(owner_user_id: int, account_id: int) -> Account | None:
    """
    获取百度账号

    :param owner_user_id: 用户ID
    :param account_id: 账号ID

    :return: 百度账号
    """
    with database.get_session().begin() as session:
        result = session.execute(
            select(Account)
            .where(cast(ColumnElement[bool], Account.owner_user_id == owner_user_id))
            .where(cast(ColumnElement[bool], Account.id == account_id))
        )
        ret = result.scalar_one_or_none()
        session.expunge_all()
        return ret


def get_all_accounts() -> list[Account]:
    """
    获取所有百度账号

    :return: 百度账号
    """
    with database.get_session().begin() as session:
        result = session.execute(select(Account))
        ret: list[Account] = [x for x in result.scalars().all()]
        session.expunge_all()
        return ret


def get_all_owned_accounts(owner_user_id: int) -> list[Account]:
    """
    获取所有百度账号

    :param owner_user_id: 用户ID

    :return: 百度账号
    """
    with database.get_session().begin() as session:
        result = session.execute(
            select(Account).where(
                cast(ColumnElement[bool], Account.owner_user_id == owner_user_id)
            )
        )
        ret: list[Account] = [x for x in result.scalars().all()]
        session.expunge_all()
        return ret


def subscribe(baidu_account_id: int, target: Target) -> None:
    """
    订阅签到结果

    :param baidu_account_id: 百度账号ID
    :param target: 订阅目标
    """
    with database.get_session().begin() as session:
        session.execute(
            insert(SigninResultSubscriber).values(
                account_id=baidu_account_id,
                private_chat=target.private,
                channel_chat=target.channel,
                self_id=target.self_id,
                platform_id=target.id,
            )
        )


def unsubscribe(baidu_account_id: int, target: Target) -> None:
    """
    取消订阅签到结果

    :param baidu_account_id: 百度账号ID
    :param target: 订阅目标
    """
    with database.get_session().begin() as session:
        session.execute(
            delete(SigninResultSubscriber)
            .where(
                cast(
                    ColumnElement[bool],
                    SigninResultSubscriber.account_id == baidu_account_id,
                )
            )
            .where(
                cast(
                    ColumnElement[bool],
                    SigninResultSubscriber.private_chat == target.private,
                )
            )
            .where(
                cast(
                    ColumnElement[bool],
                    SigninResultSubscriber.channel_chat == target.channel,
                )
            )
            .where(
                cast(
                    ColumnElement[bool],
                    SigninResultSubscriber.self_id == target.self_id,
                )
            )
            .where(
                cast(
                    ColumnElement[bool],
                    SigninResultSubscriber.platform_id == target.id,
                )
            )
        )


def unsubscribe_all(baidu_account_id: int) -> None:
    """
    取消所有订阅

    :param baidu_account_id: 百度账号ID
    """
    with database.get_session().begin() as session:
        session.execute(
            delete(SigninResultSubscriber).where(
                cast(
                    ColumnElement[bool],
                    SigninResultSubscriber.account_id == baidu_account_id,
                )
            )
        )


def get_signin_result_subscribers(
    baidu_account_id: int,
) -> list[Target]:
    """
    获取订阅者

    :param baidu_account_id: 百度账号ID

    :return: 订阅者
    """
    with database.get_session().begin() as session:
        result = session.execute(
            select(SigninResultSubscriber).where(
                cast(
                    ColumnElement[bool],
                    SigninResultSubscriber.account_id == baidu_account_id,
                )
            )
        )
        ret: list[Target] = []
        for raw_subscriber in result.scalars().all():
            ret.append(
                Target(
                    private=raw_subscriber.private_chat,
                    channel=raw_subscriber.channel_chat,
                    self_id=raw_subscriber.self_id,
                    id=raw_subscriber.platform_id,
                )
            )
        return ret


def check_alias_exists(owner_user_id: int, alias: str) -> bool:
    """
    检查账号别名是否存在

    :param owner_user_id: 用户ID
    :param alias: 别名

    :return: 是否存在
    """
    with database.get_session().begin() as session:
        result = session.execute(
            select(Account)
            .where(cast(ColumnElement[bool], Account.owner_user_id == owner_user_id))
            .where(cast(ColumnElement[bool], Account.alias == alias))
        )
        return result.one_or_none() is not None


def check_account_exists(owner_user_id: int, account_id: int) -> bool:
    """
    检查账号是否存在于对应用户中

    :param owner_user_id: 用户ID
    :param account_id: 账号ID

    :return: 是否存在
    """
    with database.get_session().begin() as session:
        result = session.execute(
            select(Account)
            .where(cast(ColumnElement[bool], Account.owner_user_id == owner_user_id))
            .where(cast(ColumnElement[bool], Account.id == account_id))
        )
        return result.one_or_none() is not None


def save_signin_result(account_id: int, result: list[ForumSigninResultData]) -> int:
    """
    保存签到结果

    :param account_id: 百度账号ID
    :param result: 签到结果

    :return: 签到结果ID
    """
    with database.get_session().begin() as session:
        signin_result_list = ForumSigninResultList(
            account_id=account_id,
        )
        session.add(signin_result_list)
        session.flush()

        signin_id = signin_result_list.id

        for data in result:
            data.signin_id = signin_id
            session.add(data)
        session.expunge_all()

        return signin_id


def get_latest_signin_result(account_id: int) -> list[ForumSigninResultData]:
    """
    获取最新签到结果

    :param account_id: 百度账号ID

    :return: 签到结果
    """
    with database.get_session().begin() as session:
        result = session.execute(
            select(ForumSigninResultList)
            .where(
                cast(
                    ColumnElement[bool], ForumSigninResultList.account_id == account_id
                )
            )
            .order_by(ForumSigninResultList.time.desc())
            .limit(1)
        ).scalar_one_or_none()

        if not result:
            return []

        result = session.execute(
            select(ForumSigninResultData).where(
                cast(ColumnElement[bool], ForumSigninResultData.signin_id == result.id)
            )
        )
        ret: list[ForumSigninResultData] = [x for x in result.scalars().all()]
        session.expunge_all()
        return ret


def get_account_alias(account_id: int) -> str:
    """
    获取账号别名

    :param account_id: 账号ID

    :return: 别名
    """
    with database.get_session().begin() as session:
        result = session.execute(
            select(Account).where(cast(ColumnElement[bool], Account.id == account_id))
        )
        if result:
            return result.scalar_one().alias
    return ""


async def signin(account: Account) -> list[ForumSigninResultData]:
    """
    自动签到

    :param account: 百度账号

    :return: 签到结果
    """
    result: list[ForumSigninResultData] = []

    like_url = "https://tieba.baidu.com/mo/q/newmoindex"
    sign_url = "http://tieba.baidu.com/sign/add"

    client = AsyncClient()
    client.cookies.set("BDUSS", account.bduss)
    client.cookies.set("STOKEN", account.stoken)

    # 获取贴吧列表
    resp = await client.get(like_url)
    if not resp.is_success or resp.status_code != 200 or resp.json()["no"] != 0:
        raise Exception("获取贴吧列表失败", resp.json())

    forum_info: dict[str] = resp.json()

    # 签到
    for forum in forum_info["data"]["like_forum"]:
        if forum["is_sign"] == 0:
            sleep(0.5)
            data = {
                "ie": "utf-8",
                "kw": forum["forum_name"],
                "tbs": forum_info["data"]["tbs"],
            }
            resp = await client.post(sign_url, data=data)
            if not resp.is_success or resp.status_code != 200:
                raise Exception("签到失败", resp.json())

            signin_result: dict[str] = resp.json()
            if signin_result["no"] == 0:
                result.append(
                    ForumSigninResultData(
                        code=ForumSigninResultType.SUCCESS,
                        name=forum["forum_name"],
                        days=signin_result["data"]["uinfo"]["total_sign_num"],
                        rank=signin_result["data"]["uinfo"]["user_sign_rank"],
                    )
                )
            else:
                result.append(
                    ForumSigninResultData(
                        code=ForumSigninResultType.ERROR,
                        name=forum["forum_name"],
                        description=json.dumps(signin_result, ensure_ascii=False),
                    )
                )
        else:
            result.append(
                ForumSigninResultData(
                    code=ForumSigninResultType.ALREADY_SIGNED, name=forum["forum_name"]
                )
            )
    return result


def generate_text_result(results: list[ForumSigninResultData]) -> str:
    """
    生成文本结果

    :param results: 签到结果

    :return: 文本结果
    """
    success_count = 0
    signed_count = 0
    failed: list[str] = []
    for result in results:
        if result.code == ForumSigninResultType.SUCCESS:
            success_count += 1
        elif result.code == ForumSigninResultType.ALREADY_SIGNED:
            signed_count += 1
        elif result.code == ForumSigninResultType.ERROR:
            failed.append(result.name)
    ret = (
        f"共{len(results)}个吧\n"
        f"已签到{signed_count}个\n"
        f"签到成功{success_count}个\n"
        f"签到失败{len(failed)}个\n\n"
    )
    if len(failed) > 0:
        ret += f"签到失败的吧：{'，'.join(failed)}"
    return ret
