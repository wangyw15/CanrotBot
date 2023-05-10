# nonebot_plugins

> 一些nonebot的插件

- [每日新闻](daily_news.py)
  - 从[这里](https://api.03c3.cn/zb/)来的每日新闻图片
- [一言](hitokoto.py)
  - 调用[一言](https://hitokoto.cn/)官方API
- [自动~~带颜色~~水群](kimo.py)
  - 词库来源于[Kyomotoi/AnimeThesaurus](https://github.com/Kyomotoi/AnimeThesaurus)，可以设置自动回复频率，也可以用命令强制回复
- [Wordle](wordle.py)
  - 用[NYTimes Wordle](https://www.nytimes.com/games/wordle/index.html)的词库做的，有待改进
- [淫语翻译机](yinglish.py)
  - 把[RimoChan/yinglish](https://github.com/RimoChan/yinglish)包装成了机器人

# 打算做的

- [ ] **重构插件结构**
  - 最重要！
- [ ] （上海）公交实时到站
  - 不一定能做
- [ ] roll 图
- [ ] 查天气
- [ ] 货币系统
- 小游戏
  - [ ] 俄罗斯转盘
  - [ ] 猜数字
    - 类似wordle
  - [ ] 24点
  - [ ] ...
- [ ] 电子宠物
  - 还没想好
- [ ] 象棋
- [ ] SaucsNAO 查图
- [ ] 抽签
  - 替换第三方插件
- [ ] 考虑删除 meme 图
- [ ] 换个 ChatGPT 插件，或者自己写

# 猜数字规则

是0-9roll出不重复的四个数作为目标

玩家给出猜测

若玩家猜的四位数中，存在n（0到4）个目标中的数，则给出 nA 的提示

若玩家猜的四位数中，存在m（0到4）个数位置与目标中的相同，则给出 mB 的提示

当猜测数与目标数完全相同时游戏结束
