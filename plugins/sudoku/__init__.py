from arclet.alconna import Args
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import (
    on_alconna,
    Alconna,
    AlconnaQuery,
    Query,
    Text,
    Image,
    Option,
)

from essentials.libraries import util
from . import sudoku

__plugin_meta__ = PluginMetadata(
    name="数独",
    description="生成数独棋盘",
    usage="/<sudoku|数独> <g|生成|s|解决> [种子]",
    config=None,
)


sudoku_handler = on_alconna(
    Alconna(
        "sudoku",
        Option(
            "generate",
            Args["difficulty", float, 0.25]["seed", str, ""],
            alias=["g", "生成"],
        ),
        Option(
            "solve",
            Args["seed", str],
            alias=["s", "解决"],
        ),
    ),
    aliases={"数独"},
    block=True,
)


@sudoku_handler.assign("generate")
async def _(
    difficulty: Query[float] = AlconnaQuery("difficulty"),
    seed: Query[str] = AlconnaQuery("seed"),
):
    # 处理参数
    difficulty_result = max(0.0, min(1.0, difficulty.result))
    seed_result = seed.result or sudoku.generate_seed()

    # 生成数独棋盘
    board = sudoku.generate_board(
        seed=seed_result, masked=True, difficulty=difficulty_result
    )

    if await util.can_send_segment(Image):
        img = await sudoku.generate_board_image(board, seed_result)
        await sudoku_handler.finish(Image(raw=img))
    else:
        text = sudoku.generate_board_text(board, seed_result)
        await sudoku_handler.finish(Text(text))
