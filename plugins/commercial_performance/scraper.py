import re
from bs4 import BeautifulSoup
from httpx import AsyncClient

_client = AsyncClient()


async def get_ids_by_page(page: int) -> set[str]:
    url = f"http://wsbs.wgj.sh.gov.cn/shwgj_ywtb/core/web/welcome/index!toResultNotice.action?flag=1&pageDoc.pageNo={page}"
    response = await _client.get(url)
    if response.is_success and response.status_code == 200:
        soup = BeautifulSoup(response.text, features="html.parser")
        ret = set()
        for i in soup.select("#div_md tr>td:nth-of-type(2)>a"):
            result = re.search(r"id=(\S+)", i["href"]).group(1)
            if result not in ret:
                ret.add(result)
        return ret
    return set()


async def get_data_by_id(performance_id: str) -> dict:
    """
    获取演出内容

    :param performance_id: 演出 id

    :return: {
        'performance': CommercialPerformance,
        'actors': list[PerformanceActors]
    }
    """
    url = f"http://wsbs.wgj.sh.gov.cn/shwgj_ywtb/core/web/welcome/index!getDocumentinfobyId.action?id={performance_id}"
    response = await _client.get(url)
    if response.is_success and response.status_code == 200:
        soup = BeautifulSoup(response.text, features="html.parser")
        if soup.select("table:nth-of-type(1)"):
            performance = {
                "id": performance_id,
                "acceptance_id": soup.select_one(
                    "#main-container span:nth-of-type(1)"
                ).text.strip()[5:],
                "approval_id": soup.select_one(
                    "#main-container span:nth-of-type(2)"
                ).text.strip()[4:],
                "permit_id": soup.select_one(
                    "table:nth-of-type(1) tr:nth-of-type(2)>td:nth-of-type(4)"
                ).text.strip(),
                "original_approval_id": soup.select_one(
                    "table:nth-of-type(1) tr:nth-of-type(3)>td:nth-of-type(4)"
                ).text.strip(),
                "license_matter": soup.select_one(
                    "table:nth-of-type(1) tr:nth-of-type(1)>td:nth-of-type(2)"
                ).text.strip(),
                "organizer": soup.select_one(
                    "table:nth-of-type(1) tr:nth-of-type(2)>td:nth-of-type(2)"
                ).text.strip(),
                "name": soup.select_one(
                    "table:nth-of-type(1) tr:nth-of-type(3)>td:nth-of-type(2)"
                ).text.strip(),
                "date": soup.select_one(
                    "table:nth-of-type(1) tr:nth-of-type(4)>td:nth-of-type(2)"
                ).text.strip(),
                "address": soup.select_one(
                    "table:nth-of-type(1) tr:nth-of-type(5)>td:nth-of-type(2)"
                ).text.strip(),
                "actor_count": soup.select_one(
                    "table:nth-of-type(1) tr:nth-of-type(6)>td:nth-of-type(2)"
                ).text.strip(),
                "session_number": soup.select_one(
                    "table:nth-of-type(1) tr:nth-of-type(6)>td:nth-of-type(4)"
                ).text.strip(),
                "foreigner_short_term": soup.select_one(
                    "table:nth-of-type(1) tr:nth-of-type(7)>td:nth-of-type(2)"
                ).text.strip()
                == "是",
                "content": soup.select_one(
                    "table:nth-of-type(1) tr:nth-of-type(8)>td:nth-of-type(2)"
                ).text.strip(),
            }
            actors = []
            for i in soup.select("table:nth-of-type(2) tr:not(:nth-of-type(1))"):
                actors.append(
                    {
                        "performance_id": performance_id,
                        "actor_id": int(i.select_one("td:nth-of-type(1)").text.strip()),
                        "name": i.select_one("td:nth-of-type(2)").text.strip(),
                        "gender": i.select_one("td:nth-of-type(3)").text.strip(),
                        "license_number": i.select_one(
                            "td:nth-of-type(4)"
                        ).text.strip(),
                    }
                )
            return {
                "performance": performance,
                "actors": actors,
            }
        else:
            return {
                "performance_id": performance_id,
                "approval_id": soup.select_one("h3").text.strip(),
                "organizer": soup.select_one("p:nth-of-type(1)").text.strip(),
                "name": soup.select_one("h2:nth-of-type(1)").text.strip(),
                "content": soup.select_one("p:nth-of-type(2)").text.strip(),
            }
    return {}
