import pytest
from nonebug import App
from tests.utils import make_event


# TODO 分析用时过长的问题
@pytest.mark.skip(reason="运行覆盖率测试时间极长")
@pytest.mark.asyncio
async def test_bnhhsh(app: App):
    from plugins.bnhhsh import bnhhsh_handler

    async with app.test_matcher(bnhhsh_handler) as ctx:
        bot = ctx.create_bot()
        event = make_event("/bnhhsh a")
        ctx.receive_event(bot, event)
        ctx.should_pass_rule()
        ctx.should_pass_permission()
        ctx.should_call_send(event, "俺")
        ctx.should_finished()
