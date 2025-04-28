try:
    from ..data import POKEMON_TYPES
except ImportError:
    # 用于调试
    POKEMON_TYPES = [
        "一般",
        "格斗",
        "飞行",
        "毒",
        "地面",
        "岩石",
        "虫",
        "幽灵",
        "钢",
        "火",
        "水",
        "草",
        "电",
        "超能",
        "冰",
        "龙",
        "恶",
        "妖精",
    ]

DEFAULT_PROMPTS = {
    "attack": "【{attack_type}】属性攻击！",
}
