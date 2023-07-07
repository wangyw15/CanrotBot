<div align="center">

# CanrotBot

</div>

> 以方舟里面的神秘商人坎诺特Cannot和胡萝卜carrot命名
>
> 具体使用方法使用 `/help` 查看

# 支持平台

- QQ
  - OneBot
    - v11
    - v12（实验性）
  - mirai2（实验性）
- QQ 频道
- Kook
- 纯文本消息

# 使用方法

这可以作为独立的机器人运行，也可以作为一个 [NoneBot v2](https://v2.nonebot.dev/) 的插件使用。

使用方法请参考[快速上手](https://v2.nonebot.dev/docs/quick-start)教程。

如果作为独立机器人使用，使用`pip install -r requirements.txt`安装依赖，然后通过`python bot.py`来运行机器人

# 功能列表

| 功能 | 作用 |
|:-:|:-:|
| 番剧相关 | 现在只做了搜索番剧 |
| 明日方舟 | 现在只做了模拟寻访 |
| Bilibili | 可以查会员购里面的展览（现在只能查上海的） |
| 不能好好说话 |  把一串字母变成涩涩的话！ |
| 计算器 | 算数 |
| cp文 | 随机生成cp文 |
| 发癫文 | 随机发送发癫文 |
| 疯狂星期四 | 随机发送疯狂星期四文案<br>天天疯狂：疯狂星期四<br>支持日文触发：狂乱木曜日 |
| 汇率转换 | 就是汇率转换 |
| 嘴臭 | 发个嘴臭文 |
| 每日新闻 | 从[这里](https://api.03c3.cn/zb/)来的每日新闻图片<br>还支持订阅，每天十点定时发送 |
| 复读机 | 复读你说的话（测试用） |
| 猜数字 | 详见[下面](#猜数字规则) |
| 一言 | 来自于[一言](https://hitokoto.cn/)的[句子包](https://github.com/hitokoto-osc/sentences-bundle) |
| 浅草寺 | 浅草寺抽签 |
| 链接元数据 | 从支持的链接中获取元数据，包括标题、描述、图片等 |
| 偶像大师<br>百万现场 剧场时光 | 查活动和查卡 |
| MuseDash 玩家信息 | 数据来源于 [MuseDash.moe](https://musedash.moe/) |
| 音乐 | 可以把QQ和网易云音乐分享链接转为音乐卡片<br>也可以点歌 |
| 能不能好好说话 | 调用[能不能好好说话？](https://lab.magiconch.com/nbnhhsh/)查找全名 |
| 自动回复 | 词库来源于[Kyomotoi/AnimeThesaurus](https://github.com/Kyomotoi/AnimeThesaurus)，机器人根据词库来概率自动水群 |
| roll 个老婆 | 从 [waifu.pics](https://waifu.pics/) 随机抽取纸片人 |
| 理科笑话 | 随机的理科笑话 |
| 搜图 | 从 [SauceNAO](https://saucenao.com) 或者 [trace.moe](https://trace.moe) 搜图 |
| 签到 | 每日签到，而且附带运势 |
| Steam 助手 | 根据 appid 查询游戏信息 |
| 舔狗语录 | 随机的舔狗语录 |
| vtb小作文 | 随机的管人小作文 |
| wordle 游戏 | 就是 wordle 游戏，用[NYTimes Wordle](https://www.nytimes.com/games/wordle/index.html)的词库做的 |
| 淫语翻译机 | 把[RimoChan/yinglish](https://github.com/RimoChan/yinglish)包装成了机器人 |
| 提取 Line 贴纸 | 发送 Line 贴纸商店链接即可 |
| 疯狂星期四 | 随机发送疯狂星期四文案 |
| Pixiv | 根据id发送对应图片 |
| 偶像荣耀 | 只做了查询活动 |
| 跑团 | 一个简单的跑团工具 |

# 功能说明

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

## 俄罗斯转盘

一个人发起，对bot说装填子弹量（1-6）

然后轮流开枪

建议加入枪走火或者卡壳类

低概率事件

# 打算做的

- [x] **重构插件结构**
  - 最重要！
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

# 特别

![JetBrains Logo (Main) logo](https://resources.jetbrains.com/storage/products/company/brand/logos/jb_beam.svg)
![PyCharm logo](https://resources.jetbrains.com/storage/products/company/brand/logos/PyCharm_icon.svg)

感谢 [JetBrains](https://www.jetbrains.com/) 为本项目免费提供的[开源项目许可](https://jb.gg/OpenSourceSupport)~
