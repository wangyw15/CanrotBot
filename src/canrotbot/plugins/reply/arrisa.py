import logging
import random

import jieba
import jieba.posseg as pseg

jieba.setLogLevel(logging.INFO)


def generate_response(message: str) -> str:
    templates = [
        "……{}？",
        "{}……",
        "这是……{}……？",
        "{}……是什么？",
    ]
    segments = list(pseg.cut(message))
    nouns: list[str] = [seg.word for seg in segments if seg.flag.startswith("n")]
    selected_template = random.choice(templates)
    if len(nouns) == 0:
        return "……什么？"
    selected_noun = random.choice(nouns)
    return selected_template.format(selected_noun)
