import pytest
from nonebug import App

import nonebot.adapters.mirai2 as mirai2
import nonebot.adapters.onebot.v11 as onebot_v11
import nonebot.adapters.onebot.v12 as onebot_v12


@pytest.mark.asyncio
async def test_is_qq_ob11(app: App):
    async with app.test_matcher() as ctx:
        from essentials.libraries.util import is_qq
        assert is_qq(ctx.create_bot(base=onebot_v11.Bot))


@pytest.mark.skip("无法构造OneBot v12 Bot")
@pytest.mark.asyncio
async def test_is_qq_ob12(app: App):
    async with app.test_matcher() as ctx:
        from essentials.libraries.util import is_qq
        assert is_qq(ctx.create_bot(base=onebot_v12.Bot))


@pytest.mark.asyncio
async def test_is_qq_mirai2(app: App):
    async with app.test_matcher() as ctx:
        from essentials.libraries.util import is_qq
        assert is_qq(ctx.create_bot(base=mirai2.Bot))


@pytest.mark.asyncio
async def test_is_qq_false(app: App):
    async with app.test_matcher() as ctx:
        from essentials.libraries.util import is_qq
        assert not is_qq(ctx.create_bot())
