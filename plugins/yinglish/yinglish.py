# from https://github.com/RimoChan/yinglish
import random

import jieba
import jieba.posseg as pseg


jieba.setLogLevel(20)


def _词转换(x, y, 淫乱度: float):
    if random.random() > 淫乱度:
        return x
    if x in {'，', '。'}:
        return '……'
    if x in {'!', '！'}:
        return '❤'
    if len(x) > 1 and random.random() < 0.5:
        return f'{x[0]}……{x}'
    else:
        if y == 'n' and random.random() < 0.5:
            x = '〇' * len(x)
        return f'……{x}'


def chs2yin(s, 淫乱度: float = 0.5):
    return ''.join([_词转换(x, y, 淫乱度) for x, y in pseg.cut(s)])
