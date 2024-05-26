<div align="center">

# CanrotBot

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

</div>

> 以方舟里面的神秘商人坎诺特Cannot和胡萝卜carrot命名
>
> 具体使用方法使用 `/help` 查看

# 支持平台

所有[nonebot-plugin-alconna](https://github.com/nonebot/plugin-alconna)所支持的平台

# 使用方法

```bash
pip install -r requirements.txt
playwright install # 如果是第一次启动，则安装 playwright
python bot.py
```

## 配置数据库

如果不做更改，默认使用SQLite

需要使用其他数据库，可以修改`canrot_database`配置，具体内容请参考[SQLAlchemy文档](canrot_database)

## 测试

```bash
pytest tests # 普通测试
pytest tests --cov --cov-report=html # 覆盖率测试
```

# 功能列表

对机器人发送`/help`查看

# 功能说明

> 只有一部分

## 猜数字规则

是0-9roll出不重复的四个数作为目标

玩家给出猜测

若玩家猜的四位数中，存在n（0到4）个目标中的数，则给出 nA 的提示

若玩家猜的四位数中，存在m（0到4）个数位置与目标中的相同，则给出 mB 的提示

当猜测数与目标数完全相同时游戏结束

## 搜图

需要在配置中设置 SauceNAO 的 api key

```
saucenao_api_key="你的 api key"
```

# 打算做的

- [x] **重构插件结构**
  - 最重要！
- [x] 统一的多平台适配器
  - 官方有做
- [ ] ~~（上海）公交实时到站~~
  - 不    能做
- [x] roll 图
- [ ] 查天气
- [x] 用户系统
- [x] 经济系统
- 小游戏
  - [ ] 俄罗斯转盘
  - [x] 猜数字
    - 类似wordle
  - [ ] 24点
  - [ ] ...
- [ ] 电子宠物
  - 还没想好
- [ ] 象棋
- [x] SaucsNAO 查图
  - ~~还在看~~
- [x] 抽签
  - 替换第三方插件
- [ ] 考虑 meme 图
- [ ] ~~换个 ChatGPT 插件，或者自己写~~
- [ ] ShindanMaker
- [ ] WolframAlpha
- [ ] WebUI

## 俄罗斯转盘

一个人发起，对bot说装填子弹量（1-6）

然后轮流开枪

建议加入枪走火或者卡壳类

低概率事件

# 功能或数据来源

| 来源 | 说明 |
|:-:|:-:|
| [hitokoto-osc/sentences-bundle](https://github.com/hitokoto-osc/sentences-bundle) |   一言数据    |
| [Kyomotoi/AnimeThesaurus](https://github.com/Kyomotoi/AnimeThesaurus) | 自动回复的部分数据 |
| [FloatTech/zbpdata](https://github.com/FloatTech/zbpdata) | 自动回复等数据来源 |
| [RimoChan/bnhhsh](https://github.com/RimoChan/bnhhsh) |  不能好好说话   |
| [Paper-co](https://free-paper-texture.com/japanese-paper-texture-2/) | 浅草寺背景图片来源 |
| [MinatoAquaCrews/nonebot_plugin_fortune](https://github.com/MinatoAquaCrews/nonebot_plugin_fortune) |   运势数据    |
| [Princess](https://api.matsurihi.me/docs/) | MLTD API  |
| [MinatoAquaCrews/nonebot_plugin_crazy_thursday](https://github.com/MinatoAquaCrews/nonebot_plugin_crazy_thursday) |  疯狂星期四文案  |
| [Bestdori](https://bestdori.com/) | 邦邦数据 |

# 鸣谢

![JetBrains Logo (Main) logo](https://resources.jetbrains.com/storage/products/company/brand/logos/jb_beam.svg)
![PyCharm logo](https://resources.jetbrains.com/storage/products/company/brand/logos/PyCharm_icon.svg)

感谢 [JetBrains](https://www.jetbrains.com/) 为本项目免费提供的[开源项目许可](https://jb.gg/OpenSourceSupport)~
