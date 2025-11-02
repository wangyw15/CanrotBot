from arclet.alconna import Args
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import (
    Alconna,
    CommandMeta,
    Image,
    Query,
    Subcommand,
    Text,
    on_alconna,
)

from canrotbot.essentials.libraries import util

from . import sudoku

sudoku_command = Alconna(
    "sudoku",
    Subcommand(
        "generate",
        Args["difficulty", float, 0.25]["seed", str, ""],
        alias=["g", "生成"],
    ),
    Subcommand(
        "solve",
        Args["seed", str],
        alias=["s", "解决"],
    ),
    meta=CommandMeta(description="生成数独棋盘"),
)

__plugin_meta__ = PluginMetadata(
    name="数独",
    description=sudoku_command.meta.description,
    usage=sudoku_command.get_help(),
    config=None,
)


sudoku_matcher = on_alconna(
    sudoku_command,
    aliases={"数独"},
    block=True,
)


@sudoku_matcher.assign("generate")
async def _(
    difficulty: Query[float] = Query("generate.difficulty"),
    seed: Query[str] = Query("generate.seed"),
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
        await sudoku_matcher.finish(Image(raw=img))
    else:
        text = sudoku.generate_board_text(board, seed_result)
        await sudoku_matcher.finish(Text(text))


@sudoku_matcher.assign("solve")
async def _(
    seed: Query[str] = Query("solve.seed"),
):
    # 处理参数
    seed_result = seed.result or sudoku.generate_seed()

    # 生成数独解法
    board = sudoku.generate_board(seed=seed_result, masked=False, difficulty=0)

    if await util.can_send_segment(Image):
        img = await sudoku.generate_board_image(board, seed_result)
        await sudoku_matcher.finish(Image(raw=img))
    else:
        text = sudoku.generate_board_text(board, seed_result)
        await sudoku_matcher.finish(Text(text))
