import pytest
from httpx import Response
from pytest_mock import MockerFixture


@pytest.mark.asyncio
async def test_commercial_performance_scraper_id(mocker: MockerFixture):
    from canrotbot.plugins.commercial_performance import scraper

    fake_page_html = r'<html><head></head><body><div id="div_md"><table><tr><td>许可单位</td><td>查看</td></tr><tr><td><a href="/shwgj_ywtb/core/web/welcome/index!getDocumentinfobyId.action?id=test01">test01</a></td><td><a href="/shwgj_ywtb/core/web/welcome/index!getDocumentinfobyId.action?id=test01">查看</a></td></tr><tr><td><a href="/shwgj_ywtb/core/web/welcome/index!getDocumentinfobyId.action?id=test02">test02</a></td><td><a href="/shwgj_ywtb/core/web/welcome/index!getDocumentinfobyId.action?id=test02">查看</a></td></tr><tr><td><a href="/shwgj_ywtb/core/web/welcome/index!getDocumentinfobyId.action?id=test03">test03</a></td><td><a href="/shwgj_ywtb/core/web/welcome/index!getDocumentinfobyId.action?id=test03">查看</a></td></tr><tr><td><a href="/shwgj_ywtb/core/web/welcome/index!getDocumentinfobyId.action?id=test04">test04</a></td><td><a href="/shwgj_ywtb/core/web/welcome/index!getDocumentinfobyId.action?id=test04">查看</a></td></tr><tr><td><a href="/shwgj_ywtb/core/web/welcome/index!getDocumentinfobyId.action?id=test05">test05</a></td><td><a href="/shwgj_ywtb/core/web/welcome/index!getDocumentinfobyId.action?id=test05">查看</a></td></tr><tr><td><a href="/shwgj_ywtb/core/web/welcome/index!getDocumentinfobyId.action?id=test06">test06</a></td><td><a href="/shwgj_ywtb/core/web/welcome/index!getDocumentinfobyId.action?id=test06">查看</a></td></tr><tr><td><a href="/shwgj_ywtb/core/web/welcome/index!getDocumentinfobyId.action?id=test07">test07</a></td><td><a href="/shwgj_ywtb/core/web/welcome/index!getDocumentinfobyId.action?id=test07">查看</a></td></tr><tr><td><a href="/shwgj_ywtb/core/web/welcome/index!getDocumentinfobyId.action?id=test08">test08</a></td><td><a href="/shwgj_ywtb/core/web/welcome/index!getDocumentinfobyId.action?id=test08">查看</a></td></tr><tr><td><a href="/shwgj_ywtb/core/web/welcome/index!getDocumentinfobyId.action?id=test09">test09</a></td><td><a href="/shwgj_ywtb/core/web/welcome/index!getDocumentinfobyId.action?id=test09">查看</a></td></tr><tr><td><a href="/shwgj_ywtb/core/web/welcome/index!getDocumentinfobyId.action?id=test10">test10</a></td><td><a href="/shwgj_ywtb/core/web/welcome/index!getDocumentinfobyId.action?id=test10">查看</a></td></tr><tr bgcolor="#eff9fd"><td colspan="2"><div class="jtext13"><div  id="page"></div></div></td></tr></table></div></body></html>'

    mocker.patch(
        "httpx.AsyncClient.get",
        return_value=Response(
            status_code=200,
            content=fake_page_html.encode("utf-8"),
        ),
    )

    performance_ids = await scraper.get_ids_by_page(1)
    assert len(performance_ids) == 10


@pytest.mark.asyncio
async def test_commercial_performance_scraper_detail(mocker: MockerFixture):
    from canrotbot.plugins.commercial_performance import scraper

    fake_page_html = r'<html><head></head><body><div class="main-container" id="main-container"><div class="content"><span>受理编号：00000000000000</span> <span>批文号：number</span><table><tr><td>许可事项:</td><td>type</td><td>新办</td></tr><tr><td>举办单位：</td><td>company</td><td>许可证号：</td><td>number</td></tr><tr><td>演出名称:</td><td>name</td><td>原批文号:</td><td></td></tr><tr><td>演出日期：</td><td>datetime</td></tr><tr><td>演出场所：</td><td>location</td></tr><tr><td>演员人数：</td><td>14</td><td>场次：</td><td>1</td></tr><tr><td>是否属于外国人在中国短期工作任务：</td><td>否</td></tr><tr><td>演出内容：</td><td>type</td></tr></table><div>bureau</div><div>date</div><div>note</div><div>演员名单</div><table><tr><th>序号</th><th>姓名</th><th>性别</th><th>证件号</th></tr><tr><td>1</td><td>Z*</td><td>女</td><td>0****************0</td></tr><tr><td>2</td><td>S*</td><td>女</td><td>0****************0</td></tr><tr><td>3</td><td>Y*</td><td>女</td><td>0****************0</td></tr><tr><td>4</td><td>L*</td><td>女</td><td>0****************0</td></tr><tr><td>5</td><td>Z*</td><td>女</td><td>0****************0</td></tr><tr><td>6</td><td>W*</td><td>女</td><td>0****************0</td></tr><tr><td>7</td><td>M*</td><td>女</td><td>0****************0</td></tr><tr><td>8</td><td>L*</td><td>女</td><td>0****************0</td></tr><tr><td>9</td><td>W*</td><td>女</td><td>0****************0</td></tr><tr><td>10</td><td>W*</td><td>女</td><td>0****************0</td></tr><tr><td>11</td><td>X*</td><td>女</td><td>0****************0</td></tr><tr><td>12</td><td>L*</td><td>女</td><td>0****************0</td></tr><tr><td>13</td><td>C*</td><td>女</td><td>0****************0</td></tr><tr><td>14</td><td>M*</td><td>男</td><td>5*******1</td></tr></table></div></div></body></html>'

    mocker.patch(
        "httpx.AsyncClient.get",
        return_value=Response(
            status_code=200,
            content=fake_page_html.encode("utf-8"),
        ),
    )

    performance_data = await scraper.get_data_by_id("example")
    assert performance_data
