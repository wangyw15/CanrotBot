import json
from enum import Enum
from time import sleep

from httpx import AsyncClient


class ForumSigninResultType(Enum):
    """
    贴吧签到结果类型
    """

    SUCCESS = 0
    ALREADY_SIGNED = 1
    ERROR = 2


class ForumSigninResult:
    """
    贴吧签到结果
    """

    def __init__(
        self,
        code: ForumSigninResultType,
        name: str,
        days: int = 0,
        rank: int = 0,
        description: str = "",
    ) -> None:
        self.code = code
        self.name = name
        self.days = days
        self.rank = rank
        self.description = description


def unicode2chinese(content: str) -> str:
    """
    恢复Unicode转义
    """
    return content.encode(encoding="utf-8").decode("unicode_escape")


async def signin(bduss: str, stoken: str) -> list[ForumSigninResult] | None:
    """
    自动签到

    :param bduss: BDUSS
    :param stoken: STOKEN

    :return: 签到结果
    """
    result: list[ForumSigninResult] = []

    like_url = "https://tieba.baidu.com/mo/q/newmoindex"
    sign_url = "http://tieba.baidu.com/sign/add"

    client = AsyncClient()
    client.cookies.set("BDUSS", bduss)
    client.cookies.set("STOKEN", stoken)

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
                    ForumSigninResult(
                        code=ForumSigninResultType.SUCCESS,
                        name=forum["forum_name"],
                        days=signin_result["data"]["uinfo"]["total_sign_num"],
                        rank=signin_result["data"]["uinfo"]["user_sign_rank"],
                    )
                )
            else:
                result.append(
                    ForumSigninResult(
                        code=ForumSigninResultType.ERROR,
                        name=forum["forum_name"],
                        description=json.dumps(signin_result, ensure_ascii=False),
                    )
                )
        else:
            result.append(
                ForumSigninResult(
                    code=ForumSigninResultType.ALREADY_SIGNED, name=forum["forum_name"]
                )
            )
    return result


def generate_text_result(results: list[ForumSigninResult]) -> str:
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
    return (
        (
            f"共{len(results)}个吧\n"
            f"已签到{signed_count}个\n"
            f"签到成功{success_count}个\n"
            f"签到失败{len(failed)}个\n\n"
        )
        + f"签到失败的吧：{'，'.join(failed)}"
        if failed
        else ""
    )
