import logging
import random
import re

import jieba
import jieba.posseg as pseg

jieba.setLogLevel(logging.INFO)


ACCEPTED_FLAGS = ["n.*", "l.*"]
TEMPLATES = [
    ("……{}？", ".*"),
    ("{}……", ".*"),
    ("这是……{}……？", "n.*"),
    ("{}……是什么？", "[nl].*"),
    ("{}……是谁？", "nr.*"),
    ("{}……是哪里？", "ns.*"),
    ("{}，你在这里干什么？", "nr.*"),
]


def extract_words(text: str) -> list[tuple[str, str]]:
    """
    提取文本中的关键词

    :param text: 文本内容

    :return: 关键词列表 [(word, flag)]
    """

    def check_word_flag(flag: str) -> bool:
        for accepted_flag in ACCEPTED_FLAGS:
            if re.fullmatch(accepted_flag, flag):
                return True
        return False

    result: list[tuple[str, str]] = []
    latest_word: tuple[str, str] = ("", "")  # ("word", "flag")
    for seg in pseg.cut(text):
        if check_word_flag(seg.flag):
            if not latest_word[0]:
                latest_word = (seg.word, seg.flag)
            else:
                if seg.flag == latest_word[1]:
                    # 合并相同词性的词
                    latest_word = (latest_word[0] + seg.word, latest_word[1])
                else:
                    result.append(latest_word)
                    latest_word = (seg.word, seg.flag)
            continue
        if latest_word[0]:
            result.append(latest_word)
            latest_word = ("", "")
    if latest_word[0]:
        result.append(latest_word)
    return result


def get_templates(flag: str) -> list[str]:
    """
    获取符合条件的模板

    :param flag: 词性标记

    :return: 模板列表
    """
    return [template[0] for template in TEMPLATES if re.fullmatch(template[1], flag)]


def generate_response(message: str) -> str:
    """
    生成回复

    :param message: 消息内容

    :return: 回复内容
    """
    words = extract_words(message)
    if not words:
        return random.choice(["……什么？", ""])
    selected_word: tuple[str, str] = random.choice(words)
    selected_template: str = random.choice(get_templates(selected_word[1]))
    return selected_template.format(selected_word[0])
