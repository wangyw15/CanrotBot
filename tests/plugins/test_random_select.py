def test_parser_with_half_width():
    from plugins.random_select import random_selector

    items = random_selector.parse_items("a,b,c")
    assert items == [("a", 1), ("b", 1), ("c", 1)]


def test_parser_with_full_width():
    from plugins.random_select import random_selector

    items = random_selector.parse_items("a，b，c")
    assert items == [("a", 1), ("b", 1), ("c", 1)]


def test_parser_with_mixed_width():
    from plugins.random_select import random_selector

    items = random_selector.parse_items("a,b，c")
    assert items == [("a", 1), ("b", 1), ("c", 1)]


def test_parser_with_half_width_weight():
    from plugins.random_select import random_selector

    items = random_selector.parse_items("a:0.1,b:0.2,c:0.7")
    assert items == [("a", 0.1), ("b", 0.2), ("c", 0.7)]


def test_parser_with_full_width_weight():
    from plugins.random_select import random_selector

    items = random_selector.parse_items("a：0.1，b：0.2，c：0.7")
    assert items == [("a", 0.1), ("b", 0.2), ("c", 0.7)]


def test_parser_with_mixed_width_weight():
    from plugins.random_select import random_selector

    items = random_selector.parse_items("a：0.1,b：0.2，c:0.7")
    assert items == [("a", 0.1), ("b", 0.2), ("c", 0.7)]


def test_parser_with_mixed_width_weight_cjk():
    from plugins.random_select import random_selector

    items = random_selector.parse_items("甲：0.1,乙：0.2，丙:0.7")
    assert items == [("甲", 0.1), ("乙", 0.2), ("丙", 0.7)]


def test_dump_items():
    from plugins.random_select import random_selector

    items = [random_selector.Item(x[0], x[1]) for x in [("a", 0.1), ("b", 0.2), ("c", 0.7)]]
    dumped = random_selector.dump_items(items)
    assert dumped == "a:0.1,b:0.2,c:0.7"
