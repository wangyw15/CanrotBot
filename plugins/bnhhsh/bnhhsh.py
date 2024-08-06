from essentials.libraries import file, path

_bnhhsh_data: dict[int, dict[str, dict[str, float]]] = file.read_json(
    path.get_asset_path() / "bnhhsh.json"
)
_bnhhsh_data: dict[int, dict[str, dict[str, float]]] = {
    int(k): v for k, v in _bnhhsh_data.items()
}
_longest = max(_bnhhsh_data.keys())


def get_pinyin_abbr(content: str) -> str:
    """
    获取拼音首字母缩写

    :param content: 内容

    :return: 拼音
    """
    import pypinyin

    return "".join(
        [
            x[0].lower()
            for x in pypinyin.pinyin(content, style=pypinyin.Style.FIRST_LETTER)
        ]
    )


def generate(target: str) -> str:
    """
    生成语句

    :param target: 拼音首字母缩写

    :return: 生成的语句
    """
    cost = {-1: 0}
    record = {-1: []}
    for x in range(len(target)):
        cost[x] = 2**32  # 默认cost为无穷大
        for k in range(_longest, 0, -1):
            s = x - k + 1
            if s < 0:
                continue
            if abbr_map := _bnhhsh_data[k].get(target[s : x + 1]):
                least_pain = 2**32
                least_word = ""
                for word, pain in abbr_map.items():
                    if pain < least_pain:
                        least_pain = pain
                        least_word = word
                if cost[x - k] + least_pain < cost[x]:
                    cost[x] = cost[x - k] + least_pain
                    record[x] = record[x - k].copy()
                    record[x].append((s, x + 1, least_word))
        if cost[x - 1] + 1 < cost[x]:
            cost[x] = cost[x - 1] + 1
            record[x] = record[x - 1].copy()
    target = [*target]
    for a, b, abbr_map in record[len(target) - 1][::-1]:
        target[a:b] = abbr_map
    # return "".join(target), cost[len(target) - 1]
    return "".join(target)
