import base64

from nonebot import get_driver, logger
from tencentcloud.aiart.v20221229 import aiart_client, models
from tencentcloud.common.credential import Credential

from libraries import tencent_cloud

credential: Credential | None = None
client: aiart_client.AiartClient | None


@get_driver().on_startup
async def _():
    global credential, client
    try:
        credential = tencent_cloud.create_credential()
        client = aiart_client.AiartClient(credential, "ap-shanghai")
    except ValueError as e:
        logger.warning("腾讯云 API 未配置")


def draw(
    prompt: str, negative: str = "", styles: str = "201", resolution: str = "768:1024"
) -> bytes:
    """
    发送 AI 作画请求

    :param prompt: 正向提示词
    :param negative: 反向提示词
    :param styles: 风格
    :param resolution: 分辨率

    :return: 生成的图像
    """
    # 生成请求
    req = models.TextToImageRequest()
    req.Prompt = prompt
    req.NegativePrompt = negative
    req.Styles = styles
    result_config = models.ResultConfig()
    result_config.Resolution = resolution
    req.ResultConfig = result_config
    req.LogoAdd = 0
    req.RspImgType = "base64"

    # 发送请求
    resp = client.TextToImage(req)
    return base64.b64decode(resp.ResultImage)
