<div align="center">

# CanrotBot

</div>

> 以方舟里面的神秘商人坎诺特Cannot和胡萝卜carrot命名
>
> 具体使用方法使用 `/help` 查看

# 使用方法

这不是一个独立的机器人，只是一个 [NoneBot v2](https://v2.nonebot.dev/) 的插件，使用方法请参考[快速上手](https://v2.nonebot.dev/docs/quick-start)教程。

此外，需要连接 [go-cqhttp](https://go-cqhttp.org/) 等使用。

# 功能列表

| 功能 | 作用 |
| :-: | :-: |
| 不能好好说话 | 把一串字母变成涩涩的话！ |
| 计算器 | 算数 |
| cp文 | 随机生成cp文 |
| 发癫文 | 随机发送发癫文 |
| 汇率转换 | 就是汇率转换 |
| 嘴臭 | 发个嘴臭文 |
| 每日新闻 | 从[这里](https://api.03c3.cn/zb/)来的每日新闻图片 |
| 猜数字 | 详见[下面](#猜数字规则) |
| 一言 | 来自于[一言](https://hitokoto.cn/)的[句子包](https://github.com/hitokoto-osc/sentences-bundle) |
| 浅草寺 | 浅草寺抽签 |
| MuseDash 玩家信息 | 数据来源于 [MuseDash.moe](https://musedash.moe/) |
| 能不能好好说话 | 调用[能不能好好说话？](https://lab.magiconch.com/nbnhhsh/)查找全名 |
| 自动回复 | 词库来源于[Kyomotoi/AnimeThesaurus](https://github.com/Kyomotoi/AnimeThesaurus)，机器人根据词库来概率自动水群 |
| roll 个老婆 | 从 [waifu.pics](https://waifu.pics/) 随机抽取纸片人 |
| 理科笑话 | 随机的理科笑话 |
| 搜图 | 从 [SauceNAO](https://saucenao.com) 或者 [trace.moe](https://trace.moe) 搜图 |
| Steam 助手 | 根据 appid 查询游戏信息 |
| 舔狗语录 | 随机的舔狗语录 |
| vtb小作文 | 随机的管人小作文 |
| wordle 游戏 | 就是 wordle 游戏，用[NYTimes Wordle](https://www.nytimes.com/games/wordle/index.html)的词库做的 |
| 淫语翻译机 | 把[RimoChan/yinglish](https://github.com/RimoChan/yinglish)包装成了机器人 |

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
- [ ] 抽签
  - 替换第三方插件
- [ ] 考虑删除 meme 图
- [ ] 换个 ChatGPT 插件，或者自己写

# 功能或数据来源

| 来源 | 说明 |
| :-: | :-: |
| [hitokoto-osc/sentences-bundle](https://github.com/hitokoto-osc/sentences-bundle) | 一言数据 |
| [Kyomotoi/AnimeThesaurus](https://github.com/Kyomotoi/AnimeThesaurus) | 自动回复的部分数据 |
| [FloatTech/zbpdata](https://github.com/FloatTech/zbpdata) | 自动回复等数据来源 |
| [RimoChan/bnhhsh](https://github.com/RimoChan/bnhhsh) | 不能好好说话 |
