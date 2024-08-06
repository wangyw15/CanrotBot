import random

from essentials.libraries import file, path

SEED_LENGTH = 8
SEED_CHARS = "0123456789abcdef"

ASSET_PATH = path.get_asset_path("sudoku")

type Board = list[list[int]]


def generate_seed(length: int = SEED_LENGTH, chars: str = SEED_CHARS) -> str:
    """
    生成随机种子

    :return: A random seed.
    """
    random.seed()
    return "".join([random.choice(chars) for _ in range(length)])


def generate_basic_board() -> Board:
    """
    生成基础数独棋盘

    :return: 基础数独棋盘
    """
    """
    -------------
    |123|456|789|
    |456|789|123|
    |789|123|456|
    -------------
    |234|567|891|
    |567|891|234|
    |891|234|567|
    -------------
    |345|678|912|
    |678|912|345|
    |912|345|678|
    -------------
    """
    board: Board = [[0 for _ in range(9)] for _ in range(9)]
    for i in range(3):
        for j in range(3):
            for k in range(9):
                board[i * 3 + j][k] = (i + j * 3 + k) % 9 + 1
    return board


def generate_empty_board() -> Board:
    """
    生成空的数独棋盘

    :return: 空的数独棋盘
    """
    return [[0 for _ in range(9)] for _ in range(9)]


def generate_board(
    seed: int | float | str | bytes | bytearray | None = None,
    masked: bool = False,
    difficulty: float = 0.5,
) -> Board:
    """
    生成完整的数独棋盘

    :param seed: 种子
    :param masked: 是否生成带空格的数独棋盘
    :param difficulty: 难度，0-1之间的浮点数，越大越难

    :return: 数度棋盘
    """

    def random_array(n: int) -> list[int]:
        ret = list(range(n))
        random.shuffle(ret)
        return ret

    random.seed(seed)

    basic_board: Board = generate_basic_board()

    # 随机打乱行列
    rows = [g * 3 + c for g in random_array(3) for c in random_array(3)]
    columns = [g * 3 + c for g in random_array(3) for c in random_array(3)]

    board: Board = generate_empty_board()

    # 生成数独棋盘
    for i in range(9):
        for j in range(9):
            board[i][j] = basic_board[rows[i]][columns[j]]

    # 随机挖空
    if masked:
        for i in range(9):
            for j in range(9):
                if random.random() < difficulty:
                    board[i][j] = 0

    return board


async def generate_board_image(
    board: Board, seed: int | float | str | bytes | bytearray
) -> bytes:
    """
    生成数独棋盘图片

    :param board: 数独棋盘
    :param seed: 种子

    :return: 图片
    """
    from essentials.libraries import render_by_browser

    template = (
        file.read_text(ASSET_PATH / "template.html")
        .replace("{SEED}", seed)
        .replace('"{BOARD}"', str(board))
    )

    return await render_by_browser.render_html(
        template, ASSET_PATH, viewport={"width": 500, "height": 500}
    )


def generate_board_text(
    board: Board, seed: int | float | str | bytes | bytearray
) -> str:
    """
    生成文字版数独棋盘

    :param board: 数独棋盘
    :param seed: 种子

    :return: 文字版数独棋盘
    """
    ret = ""
    ret += "-------------\n"
    for x in range(9):
        for y in range(9):
            if y % 3 == 0:
                ret += "|"
            if board[x][y]:
                ret += str(board[x][y])
            else:
                ret += "."
        ret += "|\n"
        if x % 3 == 2:
            ret += "-------------\n"
    ret += f"seed: {seed}"
    return ret
